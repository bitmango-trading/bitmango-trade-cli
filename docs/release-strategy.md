# Bitmango Trade CLI Release Strategy

## Overview
This document outlines the current release process for both the Free and Pro versions of the Bitmango Trade CLI.

## Free Release Process

### Description
The Free release is deployed to a public repository, which triggers an automated build and publish process.

### Scripts Involved
1. **Build Free Release Locally** (`scripts/deploy/deploy_free_local.sh`)
   - Usage: `./scripts/deploy/deploy_free_local.sh <version>` (e.g., `./scripts/deploy/deploy_free_local.sh 2026-05-18`)
   - Steps:
     - Builds the release branch in `/tmp/bitmango-trade-cli-releases/<version>`
     - Copies core files (config, docs, tutorials, etc.) using include list
     - Syncs the contents of `bitmango-free/` to the staging directory root
     - Patches `pyproject.toml` to adjust the package name
     - Copies installer scripts and sets executable permissions
     - Creates a `.gitignore` for the release branch
     - Initializes a git repo in the staging directory
     - Pushes the release branch to the public repository
     - Triggers the "Build and Publish Release" workflow on the public repo

### Manual Preparation
A script `scripts/archived/prepare_manual_release.sh` is available to replicate the Free release preparation locally for version `<version>`. It outputs a directory structure that can be used to create a release branch and push to the public repo.

## Pro Release Process

### Description
The Pro release is compiled locally (via GitHub Actions) and the resulting binaries are stored in a branch of the private repository.

### Scripts Involved
1. **Deploy Pro Release** (`scripts/deploy/deploy_pro_release.sh`)
   - Usage: `./scripts/deploy/deploy_pro_release.sh <version>`
   - Steps:
     - Runs codebase validation
     - Calls `deploy_free_local.sh` to push the Free release to public repo
     - Creates a Pro-specific branch (`releases-<VERSION>-pro`)
     - Adds Pro-specific plugins and core logic using `.whitelist-pro`
     - Pushes the Pro branch to the private repository

### Workflows Involved
1. **Build Pro Release** (`.github/workflows/build-pro-release.yml`)
   - Triggered manually via `workflow_dispatch` with inputs: `version` (required).
   - Steps:
     - **Pre-flight Job**: Verifies that all required assets (listed in `bitmango-pro/.whitelist-pro`) are present.
     - **Build Job** (matrix build for Linux, Windows, macOS):
       - Installs dependencies (nuitka, zstandard, maturin, and requirements.txt).
       - Builds the Pro core (Rust) using `maturin` (Linux only).
       - Builds standalone binaries for `bitmango`, `bitmango-vault`, and `bitmango-help` using `Nuitka`.
       - Uploads the built binaries as artifacts named `pro-binaries-${VERSION}-{platform}`.
     - **Collect and Commit Job**:
       - Checks out the Pro release branch (`releases-${VERSION}-pro`).
       - Downloads all artifacts from the build job.
       - Commits the binaries (unzipped) to the `dist_release/` directory of the branch and pushes.

### Notes on Pro Release Workflow
- The `deploy-pro-release` workflow is designed to be run after the `build-pro-release` workflow has successfully produced artifacts. However, as a standalone `workflow_dispatch`, it will not find any artifacts unless the build job has been run in the same workflow (which is not the case when triggered separately).
- To ensure the deploy step works, either:
  - Chain the workflows (have `build-pro-release` trigger `deploy-pro-release` upon completion), or
  - Modify `deploy-pro-release` to download artifacts from a specific workflow run (e.g., by specifying the run ID or using the `workflow_run` event).

### Pro Installer Scripts
The repository includes Pro-specific installer scripts in the `scripts/` directory:
- `install-bitmango-pro.sh`
- `install-bitmango-pro.ps1`
- `install-bitmango-pro.command`

## Archived Scripts
Legacy scripts have been moved to `scripts/archived/`:
- `prepare_manual_release.sh` - Original manual release preparation script
- `deploy_free.sh` - Original deploy script (replaced by `deploy_free_local.sh`)
- `deploy_free_release.sh` - Original script that staged releases in current repo (replaced by `deploy_free_local.sh`)