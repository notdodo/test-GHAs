#!/usr/bin/env python3
import os
from dataclasses import dataclass
from enum import Enum

from github import Auth, Github, InputGitAuthor
from semver import Version


class BumpStrategy(Enum):
    MAJOR: str = "major"
    MINOR: str = "minor"
    PATCH: str = "patch"
    SKIP: str = "skip"


@dataclass
class Tag:
    name: str
    message: str
    object: str
    type: str = "commit"


@dataclass
class Configuration:
    _BUMP_STRATEGY: BumpStrategy = BumpStrategy.SKIP
    MAIN_BRANCH: str = "main"
    PREFIX: str = "v"
    SUFFIX: str = ""

    @property
    def BUMP_STRATEGY(self):
        return self._BUMP_STRATEGY

    @BUMP_STRATEGY.setter
    def BUMP_STRATEGY(self, value: str):
        self._BUMP_STRATEGY = BumpStrategy(value)


config = Configuration(
    os.environ.get("INPUT_BUMP_STRATEGY", BumpStrategy.SKIP),
    os.environ.get("INPUT_MAIN_BRANCH", os.environ.get("GITHUB_REF_NAME")),
    os.environ.get("INPUT_PREFIX", Configuration.PREFIX),
    os.environ.get("INPUT_SUFFIX", Configuration.SUFFIX),
)

auth = Auth.Token(os.environ.get("INPUT_GITHUB_TOKEN"))
g = Github(auth=auth)
repo = g.get_repo(os.environ.get("GITHUB_REPOSITORY"))

try:
    latest_tag = repo.get_tags().get_page(0)[0]
except IndexError:
    latest_tag = "0.0.0"
    latest_tag = Tag(
        name=config.PREFIX + "0.0.0" + config.SUFFIX,
        message="ok",
        object=repo.get_commits()[0].sha,
    )

i = Version.parse(
    latest_tag.name.removeprefix(config.PREFIX).removesuffix(config.SUFFIX)
).bump_patch()

new_tag = Tag(
    name=config.PREFIX + str(i) + config.SUFFIX,
    message="ok",
    object=repo.get_commits()[0].sha,
)

latest_push = repo.get_commits()[0]

c = repo.get_commit(latest_push.sha)

print(c.author.email)
print(c.committer)
print(c.last_modified_datetime)

output_date = c.last_modified_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")


t = repo.create_git_tag(
    new_tag.name,
    new_tag.message,
    new_tag.object,
    new_tag.object,
    InputGitAuthor(c.author.name, str(c.author.email), str(output_date)),
)
print(t)
repo.create_git_ref(f"refs/tags/{new_tag.name}", t.sha)
