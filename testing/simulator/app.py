import random
import time
import os
import sys
import ccxt
import asyncio
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Request, Query, Response, Header, Depends
import uvicorn

# Add project root to sys.path to import bitmango_free.output
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from bitmango_free.output import display_message

app = FastAPI(title="Multi-User Simulated Exchange API")

# --- Multi-User State ---
# Structure: { user_id: { "USDT": 100000.0, ... } }
user_balances: Dict[str, Dict[str, float]] = {}
user_orders: Dict[str, List[dict]] = {}
user_processed_orders: Dict[str, Dict[str, dict]] = {}

prices = {"BTCUSDT": 70000.0, "ETHUSDT": 2500.0}
trades = [] 
order_counter = 1

# --- Config ---
CHAOS_CONFIG = {
    "latency_min": 0.01, "latency_max": 0.05,
    "error_rate": 0.0, "dropout_rate": 0.0,
    "stale_timestamp": None # If set, return this instead of real time
}

@app.post("/chaos")
async def update_chaos(config: dict):
    CHAOS_CONFIG.update(config)
    return {"message": "Updated"}

def get_user_id(x_user_id: Optional[str] = Header(None), uid: Optional[str] = Query(None)):
    final_uid = x_user_id or uid or "default"
    if final_uid not in user_balances:
        user_balances[final_uid] = {"USDT": 100000.0, "BTC": 0.0, "ETH": 0.0}
        user_orders[final_uid] = []
        user_processed_orders[final_uid] = {}
    return final_uid

async def price_generator_task():
    while True:
        for s in prices:
            change = random.uniform(-0.0001, 0.0001)
            prices[s] *= (1 + change)
            # Match STOP orders for ALL users
            cp = prices[s]
            for uid in list(user_orders.keys()):
                for o in user_orders[uid][:]:
                    if o['symbol'] == s and o['status'] == 'NEW' and o.get('stopPrice'):
                        sp = float(o['stopPrice'])
                        triggered = (o['side'] == 'BUY' and cp >= sp) or (o['side'] == 'SELL' and cp <= sp)
                        if triggered:
                            execute_fill(o, cp, uid)
                            user_orders[uid].remove(o)
        await asyncio.sleep(1)

def execute_fill(o, price, uid):
    # Ensure state exists even if called before dependency injection
    if uid not in user_balances:
        user_balances[uid] = {"USDT": 100000.0, "BTC": 0.0, "ETH": 0.0}
        user_orders[uid] = []
        user_processed_orders[uid] = {}
        
    o['status'] = 'FILLED'
    o['executedQty'] = o['origQty']
    o['avgPrice'] = str(price)
    
    cost = float(o['origQty']) * price
    asset = o['symbol'].replace("USDT", "")
    bal = user_balances[uid]
    if o['side'] == 'BUY':
        bal["USDT"] -= cost
        bal[asset] = bal.get(asset, 0.0) + float(o['origQty'])
    else:
        bal[asset] = bal.get(asset, 0.0) - float(o['origQty'])
        bal["USDT"] += cost

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(price_generator_task())

# --- Middleware ---
@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    if request.url.path in ["/chaos", "/", "/debug", "/ticker/price"]:
        return await call_next(request)
    
    if CHAOS_CONFIG["error_rate"] > 0:
        print(f"DEBUG: Chaos Middleware checking error_rate {CHAOS_CONFIG['error_rate']}")
    
    wait = random.uniform(CHAOS_CONFIG["latency_min"], CHAOS_CONFIG["latency_max"])
    if wait > 0: await asyncio.sleep(wait)
    if random.random() < CHAOS_CONFIG["error_rate"]: return Response(content="Error", status_code=500)
    if random.random() < CHAOS_CONFIG["dropout_rate"]: raise RuntimeError("Dropout")
    return await call_next(request)

@app.get("/")
async def root():
    return {"status": "ok", "prices": prices}

@app.get("/debug")
async def debug_state(uid: str = Depends(get_user_id)):
    return {
        "balance": user_balances.get(uid, {}),
        "prices": prices,
        "orders": user_orders.get(uid, []),
        "processed_orders": user_processed_orders.get(uid, {})
    }

@app.get("/api/v3/ticker/price")
@app.get("/fapi/v1/ticker/price")
async def get_price(symbol: str):
    # stale_timestamp can also be used for future if passed a large value
    ts = CHAOS_CONFIG["stale_timestamp"] or int(time.time() * 1000)
    return {
        "symbol": symbol.upper(), 
        "price": str(prices.get(symbol.upper(), 70000.0)),
        "timestamp": ts
    }

@app.post("/ticker/price")
async def set_price(symbol: str, price: float):
    s = symbol.upper()
    prices[s] = price
    # Trigger all users' stops
    for uid in list(user_orders.keys()):
        for o in user_orders[uid][:]:
            if o['symbol'] == s and o['status'] == 'NEW' and o.get('stopPrice'):
                sp = float(o['stopPrice'])
                triggered = (o['side'] == 'BUY' and price >= sp) or (o['side'] == 'SELL' and price <= sp)
                if triggered:
                    execute_fill(o, price, uid)
                    user_orders[uid].remove(o)
    return {"symbol": s, "price": str(price)}

@app.get("/api/v3/account")
@app.get("/fapi/v1/account")
async def get_account(uid: str = Depends(get_user_id)):
    bal = user_balances[uid]
    return {
        "balances": [{"asset": k, "free": str(v), "locked": "0.0"} for k, v in bal.items()],
        "canTrade": True
    }

@app.post("/api/v3/order")
@app.post("/fapi/v1/order")
async def place_order(
    symbol: str, side: str, type: str, 
    quantity: float = Query(...), 
    price: Optional[float] = Query(None),
    stopPrice: Optional[float] = Query(None),
    newClientOrderId: Optional[str] = Query(None),
    uid: str = Depends(get_user_id)
):
    global order_counter
    s = symbol.upper()
    order_id = order_counter
    order_counter += 1
    
    order = {
        "symbol": s, "orderId": order_id, "clientOrderId": newClientOrderId or f"sim_{order_id}",
        "transactTime": int(time.time() * 1000), "price": str(price or 0.0),
        "origQty": str(quantity), "executedQty": "0.0", "status": "NEW",
        "type": type.upper(), "side": side.upper(), "stopPrice": str(stopPrice) if stopPrice else None
    }
    
    if type.upper() == "MARKET":
        execute_fill(order, prices.get(s, 70000.0), uid)
    else:
        user_orders[uid].append(order)
        
    user_processed_orders[uid][str(order_id)] = order
    return order

@app.get("/fapi/v1/positionRisk")
async def get_positions(uid: str = Depends(get_user_id)):
    pos = []
    for asset, qty in user_balances[uid].items():
        if asset == 'USDT' or qty == 0: continue
        s = f"{asset}USDT"
        pos.append({
            "symbol": s, 
            "positionAmt": str(qty), 
            "entryPrice": str(prices.get(s, 0.0)),
            "unRealizedProfit": "0.0",
            "liquidationPrice": "0.0",
            "leverage": "10",
            "marginType": "cross",
            "isAutoAddMargin": "false"
        })
    return pos

@app.post("/sapi/v1/asset/transfer")
async def post_transfer(uid: str = Depends(get_user_id)):
    return {"tranId": 12345}

@app.delete("/api/v3/order")
@app.delete("/fapi/v1/order")
async def cancel_order(symbol: str, orderId: int, uid: str = Depends(get_user_id)):
    for o in user_orders[uid]:
        if o['orderId'] == orderId:
            user_orders[uid].remove(o)
            o['status'] = 'CANCELED'
            return o
    raise HTTPException(status_code=404)

@app.get("/api/v3/openOrders")
@app.get("/fapi/v1/openOrders")
async def open_orders(uid: str = Depends(get_user_id)):
    return user_orders[uid]

@app.get("/api/v3/depth")
@app.get("/fapi/v1/depth")
async def get_depth(symbol: str, limit: int = 5):
    p = prices.get(symbol.upper(), 70000.0)
    return {
        "lastUpdateId": int(time.time() * 1000),
        "bids": [[str(p * (1 - 0.0001 * i)), str(1.0 + i)] for i in range(limit)],
        "asks": [[str(p * (1 + 0.0001 * i)), str(1.0 + i)] for i in range(limit)]
    }

@app.get("/api/v3/myTrades")
@app.get("/fapi/v1/userTrades")
async def get_my_trades(symbol: str, uid: str = Depends(get_user_id)):
    return [
        {
            "symbol": symbol.upper(),
            "id": 28457,
            "orderId": 100234,
            "price": "70000.0",
            "qty": "0.1",
            "quoteQty": "7000.0",
            "commission": "7.0",
            "commissionAsset": "USDT",
            "time": int(time.time() * 1000) - 3600000,
            "isBuyer": True,
            "isMaker": False,
            "isBestMatch": True
        }
    ]

@app.get("/api/v3/allOrders")
@app.get("/fapi/v1/allOrders")
async def get_all_orders(symbol: str, uid: str = Depends(get_user_id)):
    return [
        {
            "symbol": symbol.upper(),
            "orderId": 100234,
            "clientOrderId": "sim_100234",
            "price": "70000.0",
            "origQty": "0.1",
            "executedQty": "0.1",
            "status": "FILLED",
            "type": "MARKET",
            "side": "BUY",
            "time": int(time.time() * 1000) - 3600000,
            "updateTime": int(time.time() * 1000) - 3500000
        }
    ]

@app.get("/api/v3/ledger")
async def get_ledger(uid: str = Depends(get_user_id)):
    return [
        {
            "id": "72134",
            "currency": "USDT",
            "amount": "100.0",
            "type": "TRANSFER",
            "status": "COMPLETED",
            "timestamp": int(time.time() * 1000) - 86400000
        }
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
