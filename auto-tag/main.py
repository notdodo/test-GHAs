#!/usr/bin/env python3
import os
import uuid
from dataclasses import dataclass
from enum import Enum


class BumpStrategy(Enum):
    MAJOR: str = "major"
    MINOR: str = "minor"
    PATCH: str = "patch"
    SKIP: str = "skip"


@dataclass
class Configuration:
    BUMP_STRATEGY: BumpStrategy = BumpStrategy.SKIP
    BRANCH: str = "main"  # $GITHUB_BASE_REF
    PREFIX: str = ""
    SUFFIX: str = ""


def set_output(name, value):
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        print(f"{name}={value}", file=fh)


def set_multiline_output(name, value):
    with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
        delimiter = uuid.uuid1()
        print(f"{name}<<{delimiter}", file=fh)
        print(value, file=fh)
        print(delimiter, file=fh)


set_output("asdf", "asdf")
set_multiline_output("asdfa", "ASdfsdafds\isdfjosdifjdfjj\jj")
