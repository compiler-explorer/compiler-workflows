#!/usr/bin/env python

from __future__ import annotations
import click
import boto3
import datetime
import dataclasses
from enum import Enum
from typing import List, Optional, Mapping, Any


class BuildStatus(Enum):
    UNKNOWN = ""
    SKIPPED = "SKIPPED"
    OK = "OK"

    @staticmethod
    def parse(name: str) -> BuildStatus:
        if name in BuildStatus:
            return BuildStatus[name]
        return BuildStatus.UNKNOWN


@dataclasses.dataclass(frozen=True)
class Build:
    path: str
    github_run_id: str
    status: BuildStatus
    timestamp: datetime.datetime
    duration: datetime.timedelta

    @classmethod
    def from_response(cls, response: Mapping[str, Any]):
        return cls(
            path=response["path"],
            github_run_id=response["github_run_id"],
            status=BuildStatus.parse(response["status"]),
            timestamp=datetime.datetime.fromisoformat(response["timestamp"]),
            duration=datetime.timedelta(seconds=(float(response["duration"]))),
        )


@dataclasses.dataclass
class CompilerStats:
    name: str
    last_successful_build: Optional[Build]
    all_builds: List[Build]


@click.command()
def main():
    dynamodb = boto3.resource("dynamodb")
    compilations = dynamodb.Table("compiler-builds")
    print(compilations.creation_date_time)
    response = compilations.scan()

    compilers = {}
    for item in response["Items"]:
        compiler_name = item["compiler"]
        build = Build.from_response(item)
        compiler: CompilerStats = compilers.setdefault(
            compiler_name,
            CompilerStats(
                name=compiler_name, last_successful_build=None, all_builds=[]
            ),
        )
        compiler.all_builds.append(build)
        if build.status == BuildStatus.OK and (
            compiler.last_successful_build is None
            or compiler.last_successful_build.timestamp < build.timestamp
        ):
            compiler.last_successful_build = build

    print(compilers)


if __name__ == "__main__":
    main()
