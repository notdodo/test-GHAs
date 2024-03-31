"""
Module with the configuration of the action
"""

import os
from enum import Enum
from typing import List

from github import Commit


class BumpStrategy(Enum):
    """Enum containing the different version bump strategy for semver"""

    MAJOR: str = "major"
    MINOR: str = "minor"
    PATCH: str = "patch"
    SKIP: str = "skip"


class Configuration:
    """Configuration resource"""

    # pylint: disable=invalid-name
    BIND_TO_MAJOR = True
    DEFAULT_BUMP_STRATEGY: BumpStrategy = BumpStrategy.SKIP
    DEFAULT_BRANCH: str = "main"
    PREFIX: str = "v"
    REPOSITORY: str = os.environ.get("GITHUB_REPOSITORY", "")
    SUFFIX: str = ""
    DRY_RUN: bool = False

    @classmethod
    def from_env(cls):
        """Create default configuration instance with values from env variables"""
        return cls(
            BIND_TO_MAJOR=os.environ.get("INPUT_BIND_TO_MAJOR", cls.BIND_TO_MAJOR)
            == "true",
            DEFAULT_BUMP_STRATEGY=os.environ.get(
                "INPUT_DEFAULT_BUMP_STRATEGY", cls.DEFAULT_BUMP_STRATEGY
            ),
            DEFAULT_BRANCH=os.environ.get("INPUT_MAIN_BRANCH", cls.DEFAULT_BRANCH),
            PREFIX=os.environ.get("INPUT_PREFIX", cls.PREFIX),
            REPOSITORY=os.environ.get("GITHUB_REPOSITORY", ""),
            SUFFIX=os.environ.get("INPUT_SUFFIX", cls.SUFFIX),
            DRY_RUN=os.environ.get("INPUT_DRY_RUN", cls.DRY_RUN),
        )

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        BIND_TO_MAJOR,
        DEFAULT_BUMP_STRATEGY,
        DEFAULT_BRANCH,
        PREFIX,
        REPOSITORY,
        SUFFIX,
        DRY_RUN,
    ):
        self.BIND_TO_MAJOR = (BIND_TO_MAJOR,)
        self.DEFAULT_BUMP_STRATEGY = DEFAULT_BUMP_STRATEGY
        self.DEFAULT_BRANCH = DEFAULT_BRANCH
        self.PREFIX = PREFIX
        self.REPOSITORY = REPOSITORY
        self.SUFFIX = SUFFIX
        self.DRY_RUN = DRY_RUN

    def get_bump_strategy_from_commits(self, commits: List[Commit.Commit]):
        """Get the bump strategy from a list of commits parsing the keywords [#<strategy>]"""
        strategies = [strategy.value for strategy in BumpStrategy]
        for commit in commits:
            for strategy in strategies:
                if f"[#{strategy.lower()}]" in commit.commit.message:
                    return BumpStrategy(strategy)
        return self.DEFAULT_BUMP_STRATEGY