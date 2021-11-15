#!/usr/bin/env python

from __future__ import annotations
from typing import TextIO
import click
from pathlib import Path
import yaml


def make_yaml_doc(
    friendly_name: str, image: str, build_name: str, command: str, build: str
) -> str:
    return f"""### DO NOT EDIT - created by a script ###
name: {friendly_name}

on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

jobs:
  daily-build:
    runs-on: [ 'self-hosted', 'ce', 'ubuntu' ]
    steps:
      - name: Start from a clean directory
        uses: AutoModality/action-clean@v1.1.0
      - uses: actions/checkout@v2
      - name: Run the build
        uses: ./.github/actions/daily-build
        with:
          image: {image}
          build_name: {build_name}
          command: {command}
          build: {build}
          AWS_ACCESS_KEY_ID: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
          AWS_SECRET_ACCESS_KEY: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
"""


def make_status_badge(friendly_name: str, build_file: str) -> str:
    wf = "https://github.com/compiler-explorer/compiler-workflows/actions/workflows/"
    return f"""[![{friendly_name}]({wf}/{build_file}/badge.svg)]({wf}/{build_file})"""


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
        build_name = daily_compiler["build_name"]
        command = daily_compiler["command"]
        build = daily_compiler["build"]
        build_yml = f"build-daily-{build_name}.yml"
        friendly_name = f"Daily build of {build_name} via {image} {build}"
        (output_path / build_yml).write_text(
            make_yaml_doc(
                friendly_name=friendly_name,
                image=image,
                build_name=build_name,
                command=command,
                build=build,
            )
        )
        badges[friendly_name] = make_status_badge(friendly_name, build_yml)
    status_file.write(f"## Build status\n\n")
    for name in sorted(badges.keys()):
        status_file.write(f"* {badges[name]}\n")

if __name__ == "__main__":
    main()
