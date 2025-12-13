# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository manages GitHub Actions workflows for building compilers used by Compiler Explorer (godbolt.org). It generates workflow YAML files from a central configuration file.

## Key Commands

```bash
make deps              # Install dependencies (Poetry + Python packages)
make build-yamls       # Regenerate workflow YAML files from compilers.yaml
make test              # Run tests
make pre-commit        # Run all pre-commit hooks
make install-pre-commit # Install pre-commit hooks
```

## Architecture

### Configuration Flow

1. **compilers.yaml** - Central configuration defining all compiler builds
2. **make_builds.py** - Python script that reads compilers.yaml and generates:
   - Individual workflow files in `.github/workflows/build-daily-*.yml`
   - Status badges in `build-status.md`
3. **pre-commit hook** - Automatically runs `make build-yamls` when Python/YAML files change

### Workflow Structure

- `.github/actions/daily-build/action.yml` - Reusable composite action for all builds
- `.github/workflows/build-daily-*.yml` - Auto-generated (DO NOT EDIT directly)
- `.github/workflows/ci.yml` - CI for this repo itself

### Adding a New Compiler

1. Add entry to `compilers.yaml` under `compilers.daily`:
   ```yaml
   - { image: <docker-image>, name: <unique-name>, args: <build-args> }
   # or with custom command:
   - { image: <docker-image>, name: <unique-name>, command: <script.sh>, args: <args> }
   # with repo activity checking (skips build if no commits in last N days):
   - { image: <docker-image>, name: <unique-name>, args: <args>, repos: ["https://github.com/owner/repo"] }
   # with specific branch:
   - { image: <docker-image>, name: <unique-name>, args: <args>, repos: ["https://github.com/owner/repo/tree/branch-name"] }
   ```
2. Run `make build-yamls` (or let pre-commit do it)
3. Also add entry in `remove_old_compilers.sh` in the infra repository

### Repo Activity Checking

Compilers can specify a `repos` field with a list of GitHub repository URLs. If specified, a `check-activity` job runs first on `ubuntu-latest` to check for recent commits. The expensive `daily-build` job only runs if activity is found.

- If ANY repo has recent commits, the build runs
- If no `repos` field, builds always run (backwards compatible)
- Branch can be specified in URL: `https://github.com/owner/repo/tree/branch-name`
- Stale days can be adjusted via `STALE_DAYS` constant in `make_builds.py` (default: 7)

### Build Process

Builds run on self-hosted runners. The daily-build action:
- Pulls previous build revision from S3
- Runs Docker container with `compilerexplorer/<image>-builder`
- Uploads artifacts to `s3://compiler-explorer/opt/`
- Logs build status to DynamoDB `compiler-builds` table

### Shell Scripts

- `pre-run.sh` - Records start timestamp
- `post-run.sh` - Records build result to DynamoDB
