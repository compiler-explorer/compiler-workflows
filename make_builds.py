#!/usr/bin/env python

from __future__ import annotations
from typing import TextIO
import click
from pathlib import Path
import yaml

import urllib.parse
def make_yaml_doc(
    friendly_name: str, image: str, name: str, command: str, args: str
) -> str:
    return f"""### DO NOT EDIT - created by a script ###
name: {friendly_name}

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  daily-build:
    runs-on: [ 'self-hosted', 'ce', 'linux' ]
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
        build_yml = f"build-daily-{name}.yml"
        friendly_name = f"{name} via {image} {args}"
        (output_path / build_yml).write_text(
            make_yaml_doc(
                friendly_name=friendly_name,
                image=image,
                name=name,
                command=command,
                args=args,
            )
        )
        badges[friendly_name] = make_status_badges(friendly_name, name, build_yml)
    status_file.write(f"## Build status\n\n")
    for name in sorted(badges.keys()):
        status_file.write(f"* {badges[name]}\n")

if __name__ == "__main__":
    main()
