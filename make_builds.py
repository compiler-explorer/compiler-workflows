#!/usr/bin/env python

from __future__ import annotations
from typing import TextIO
import click


@click.command()
@click.argument("--yaml-file", default="compilers.yaml", type=click.File())
@click.argument(
    "--output-dir",
    default=".github/workflows",
    type=click.Path(file_okay=False, exists=True, dir_okay=True, writable=True),
)
def main(yaml_file: TextIO, output_dir: str):
    pass


if __name__ == "__main__":
    main()
