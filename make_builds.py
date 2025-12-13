#!/usr/bin/env python

from __future__ import annotations
from typing import TextIO
import click
import json
from pathlib import Path
import yaml

import urllib.parse

# Number of days without commits to consider a repo stale
STALE_DAYS = 7


def make_yaml_doc(
    friendly_name: str, image: str, name: str, command: str, args: str, repos: list[str]
) -> str:
    # If repos are specified, add a check-activity job that runs first on a cheap runner
    if repos:
        repos_json = json.dumps(repos)
        return f"""### DO NOT EDIT - created by a script ###
name: {friendly_name}

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  check-activity:
    runs-on: ubuntu-latest
    outputs:
      should_build: ${{{{ steps.check.outputs.should_build }}}}
    steps:
      - name: Check for recent commits
        id: check
        run: |
          REPOS='{repos_json}'
          STALE_DAYS={STALE_DAYS}

          SINCE_DATE=$(date -d "${{STALE_DAYS}} days ago" --iso-8601=seconds)
          echo "Checking for commits since ${{SINCE_DATE}} (${{STALE_DAYS}} days ago)"
          HAS_RECENT=false

          for repo in $(echo "$REPOS" | jq -r '.[]'); do
            REPO_PATH=$(echo "$repo" | sed -E 's|https://github.com/([^/]+/[^/]+).*|\\1|')
            BRANCH=$(echo "$repo" | sed -n -E 's|https://github.com/[^/]+/[^/]+/tree/(.+)|\\1|p')

            if [ -n "$BRANCH" ]; then
              echo "Checking $REPO_PATH (branch: $BRANCH) for recent commits..."
              COMMITS=$(curl -sf "https://api.github.com/repos/${{REPO_PATH}}/commits?sha=${{BRANCH}}&since=${{SINCE_DATE}}&per_page=1" || echo "[]")
            else
              echo "Checking $REPO_PATH (default branch) for recent commits..."
              COMMITS=$(curl -sf "https://api.github.com/repos/${{REPO_PATH}}/commits?since=${{SINCE_DATE}}&per_page=1" || echo "[]")
            fi

            if [ "$(echo "$COMMITS" | jq 'length')" -gt 0 ]; then
              echo "Found recent commits in $repo"
              HAS_RECENT=true
              break
            fi
          done

          if [ "$HAS_RECENT" = "true" ]; then
            echo "should_build=true" >> "$GITHUB_OUTPUT"
          else
            echo "No recent commits in any repo (within ${{STALE_DAYS}} days), skipping build"
            echo "should_build=false" >> "$GITHUB_OUTPUT"
          fi

  daily-build:
    needs: check-activity
    if: ${{{{ needs.check-activity.outputs.should_build == 'true' }}}}
    runs-on: [ 'self-hosted', 'ce', 'linux', 'x64' ]
    steps:
      - name: Start from a clean directory
        uses: AutoModality/action-clean@v1.1.0
      - uses: actions/checkout@v4
      - name: Run the build
        uses: ./.github/actions/daily-build
        with:
          image: {image}
          name: {name}
          command: {command}
          args: {args}
          AWS_ACCESS_KEY_ID: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
          AWS_SECRET_ACCESS_KEY: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
"""
    else:
        # No repos specified - simple workflow without activity check
        return f"""### DO NOT EDIT - created by a script ###
name: {friendly_name}

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  daily-build:
    runs-on: [ 'self-hosted', 'ce', 'linux', 'x64' ]
    steps:
      - name: Start from a clean directory
        uses: AutoModality/action-clean@v1.1.0
      - uses: actions/checkout@v4
      - name: Run the build
        uses: ./.github/actions/daily-build
        with:
          image: {image}
          name: {name}
          command: {command}
          args: {args}
          AWS_ACCESS_KEY_ID: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
          AWS_SECRET_ACCESS_KEY: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
"""


def make_shield_url(friendly_name: str, build_name: str, colour:str, query: str) -> str:
    status_url= f"https://lambda.compiler-explorer.com/compiler-build/{build_name}"
    params = dict(color=colour, label=friendly_name, query=query, url=status_url)
    return f"""https://img.shields.io/badge/dynamic/json?{urllib.parse.urlencode(params)}"""


def make_status_badges(friendly_name: str, build_name, build_file: str) -> str:
    wf = "https://github.com/compiler-explorer/compiler-workflows/actions/workflows/"
    gh_badge = f"""[![Status]({wf}/{build_file}/badge.svg)]({wf}/{build_file})"""
    success_shield_url = make_shield_url("Last OK", build_name, "success", "$.last_success.timestamp")
    success_shield = f"![Last success]({success_shield_url})"
    build_shield_url = make_shield_url("Last build", build_name, "yellow", "$.last_build.timestamp")
    build_shield = f"![Last build]({build_shield_url})"
    return f"{gh_badge}{success_shield}{build_shield}"

@click.command()
@click.option("--yaml-file", default="compilers.yaml", type=click.File())
@click.option(
    "--status-file",
    default="build-status.md",
    type=click.File(mode="w"),
)
@click.option(
    "--output-dir",
    default=".github/workflows",
    type=click.Path(file_okay=False, exists=True, dir_okay=True, writable=True),
)
def main(yaml_file: TextIO, status_file: TextIO, output_dir: str):
    output_path = Path(output_dir)
    yaml_doc = yaml.load(yaml_file, Loader=yaml.FullLoader)
    badges = {}
    for daily_compiler in yaml_doc["compilers"]["daily"]:
        image = daily_compiler["image"]
        name = daily_compiler["name"]
        command = daily_compiler.get("command", "build.sh")
        args = daily_compiler.get("args", "trunk")
        repos = daily_compiler.get("repos", [])
        build_yml = f"build-daily-{name}.yml"
        friendly_name = f"{name} via {image} {args}"
        (output_path / build_yml).write_text(
            make_yaml_doc(
                friendly_name=friendly_name,
                image=image,
                name=name,
                command=command,
                args=args,
                repos=repos,
            )
        )
        badges[friendly_name] = make_status_badges(friendly_name, name, build_yml)
    status_file.write(f"## Build status\n\n")
    for name in sorted(badges.keys()):
        status_file.write(f"* {badges[name]}\n")

if __name__ == "__main__":
    main()
