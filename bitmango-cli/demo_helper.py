import sys
import time
import subprocess
import os
import re

def get_sleep_time(seconds):
    """Returns a reduced sleep time if BITMANGO_FAST_DEMO is set."""
    if os.environ.get("BITMANGO_FAST_DEMO") == "true":
        return 0.01
    return seconds

def typewriter_print(text, speed=0.01, end="\n"):
    """Prints text one character at a time."""
    actual_speed = get_sleep_time(speed)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(actual_speed)
    sys.stdout.write(end)
    sys.stdout.flush()

def delete_line(text, speed=0.002):
    """Deletes the current line using ANSI codes for robustness."""
    # Move to start of line and clear to end
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def teacher_explain(explanation):
    """Types each sentence, waits, and deletes it."""
    if not explanation:
        return
        
    # Split by common sentence endings but keep the delimiter
    sentences = re.split(r'(?<=[.!?]) +', explanation)
    
    for sentence in sentences:
        if not sentence.strip():
            continue
            
        # Type it as a comment/prompt
        prefix = "\033[90m# \033[0m"
        sys.stdout.write(prefix)
        sys.stdout.flush()
        
        typewriter_print(sentence, speed=0.02, end="")
        sys.stdout.flush()
        time.sleep(get_sleep_time(1.5))
        
        # Clear the line
        sys.stdout.write('\r\033[2K') # Clear entire line
        sys.stdout.flush()

def run_demo_step(objective, command_args, explanation=None, display_cmd=None):
    print("\n" + "─" * 60)
    print(f"OBJECTIVE: {objective}")
    
    if explanation:
        teacher_explain(explanation)
    
    full_cmd = ["./bitmango"] + command_args + ["--exchange", "simulated", "--no-confirm"]
    show_cmd = display_cmd if display_cmd else " ".join(["bitmango"] + command_args)
    
    sys.stdout.write("\033[94m$\033[0m ")
    sys.stdout.flush()
    time.sleep(get_sleep_time(0.3))
    typewriter_print(f"\033[38;5;208m{show_cmd}\033[0m", speed=0.01)
    
    time.sleep(get_sleep_time(0.5))
    executable = sys.executable
    subprocess.run([executable] + full_cmd, stderr=subprocess.DEVNULL)
    time.sleep(get_sleep_time(0.5))

def run_canned_step(objective, command_args, explanation, canned_output_func, display_cmd=None, use_case=None, pro_tip=None):
    print("\n" + "─" * 60)
    print(f"OBJECTIVE: {objective}")
    
    if explanation:
        teacher_explain(explanation)
    
    show_cmd = display_cmd if display_cmd else " ".join(["bitmango"] + command_args)
    
    print(f"\nEXECUTING COMMAND:")
    sys.stdout.write("\033[94m$\033[0m ")
    sys.stdout.flush()
    time.sleep(get_sleep_time(0.3))
    typewriter_print(f"\033[38;5;208m{show_cmd}\033[0m", speed=0.01)
    
    time.sleep(get_sleep_time(0.5))
    canned_output_func()
    
    # In README mode, we skip the extra commentary to keep the animation clean and concise
    if os.environ.get("BITMANGO_README_DEMO") == "true":
        time.sleep(get_sleep_time(1.0))
        return

    if use_case:
        time.sleep(get_sleep_time(0.5))
        print("\n" + "\033[96m" + "DETAILED RATIONALE & USE CASES" + "\033[0m")
        print("─" * 30)
        for line in use_case.strip().split('\n'):
            print(f"  {line.strip()}")
            sys.stdout.flush()
            time.sleep(get_sleep_time(0.2))

    if pro_tip:
        time.sleep(get_sleep_time(0.5))
        # Gold/Orange color for Pro Tips
        print("\n" + "\033[38;5;214m" + "💡 PRO TIP" + "\033[0m")
        print("─" * 10)
        for line in pro_tip.strip().split('\n'):
            print(f"  {line.strip()}")
            sys.stdout.flush()
            time.sleep(get_sleep_time(0.2))
    
    time.sleep(get_sleep_time(0.5))

def start_simulator():
    """Starts the simulator in the background."""
    try:
        # Kill anything on port 8080 safely
        pids = subprocess.check_output(["lsof", "-t", "-i", ":8080"]).decode().strip().split('\n')
        for pid in pids:
            if pid:
                subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
    except Exception:
        pass

    log = open("simulator_demo.log", "w")
    proc = subprocess.Popen([sys.executable, "testing/simulator/app.py"], stdout=log, stderr=log)
    time.sleep(3)
    return proc

def stop_simulator(proc):
    """Stops the simulator."""
    proc.terminate()
    proc.wait()
