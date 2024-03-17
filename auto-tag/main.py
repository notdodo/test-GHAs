#!/usr/bin/env python3
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import github
from github import Commit, Repository
from semver import Version


class BumpStrategy(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    SKIP = "skip"


@dataclass
class CustomTag:
    name: str
    commit: str
    message: str = ""
    type: str = "commit"
    last_modified_datetime: datetime = datetime.now()


@dataclass
class Configuration:
    DEFAULT_BUMP_STRATEGY: BumpStrategy = BumpStrategy.SKIP
    DEFAULT_BRANCH: str = "main"
    PREFIX: str = "v"
    SUFFIX: str = ""


config = Configuration(
    BumpStrategy(
        os.environ.get("INPUT_DEFAULT_BUMP_STRATEGY", BumpStrategy.MINOR.value)
    ),
    os.environ.get("INPUT_MAIN_BRANCH", Configuration.DEFAULT_BRANCH),
    os.environ.get("INPUT_PREFIX", Configuration.PREFIX),
    os.environ.get("INPUT_SUFFIX", Configuration.SUFFIX),
)

if os.environ.get("GITHUB_REF_NAME") != config.DEFAULT_BRANCH:
    print("Not running from the default branch")
    quit()


def github_auth() -> Repository.Repository:
    auth = github.Github(os.environ.get("INPUT_GITHUB_TOKEN", ""))
    return auth.get_repo(os.environ.get("GITHUB_REPOSITORY", ""))


def get_latest_tag_or_default(repo: Repository.Repository) -> CustomTag:
    try:
        last_tag = repo.get_tags().get_page(0)[0]
        last_tag = CustomTag(
            name=last_tag.name,
            commit=last_tag.commit.sha,
            last_modified_datetime=(
                last_tag.last_modified_datetime
                if last_tag.last_modified_datetime
                else datetime.now()
            ),
        )
    except IndexError:
        last_tag = CustomTag(
            name=config.PREFIX + "0.0.0" + config.SUFFIX,
            commit=repo.get_commits()[0].sha,
            last_modified_datetime=datetime.now(),
        )
    return last_tag


def check_bump_strategy_since_last_tag(
    repo: Repository.Repository, last_tag: CustomTag
) -> BumpStrategy:
    strategies = [strategy.value for strategy in BumpStrategy]
    last_commits_since_tag = repo.get_commits(sha=last_tag.commit)
    for commit in last_commits_since_tag:
        for strategy in strategies:
            if f"[#{strategy.upper()}]" in commit.commit.message:
                return BumpStrategy(strategy)
    return config.DEFAULT_BUMP_STRATEGY


def get_last_commit(repo: Repository.Repository) -> Commit.Commit:
    return repo.get_commits()[0]


def bump_tag_version(
    strategy: BumpStrategy, last_tag: CustomTag, repo: Repository.Repository
) -> CustomTag:
    current_version = Version.parse(
        last_tag.name.removeprefix(config.PREFIX).removesuffix(config.SUFFIX)
    )
    if strategy == BumpStrategy.MAJOR:
        new_version = current_version.bump_major()
    elif strategy == BumpStrategy.MINOR:
        new_version = current_version.bump_minor()
    elif strategy == BumpStrategy.PATCH:
        new_version = current_version.bump_patch()

    last_commit = get_last_commit(repo)
    new_tag = CustomTag(
        name=config.PREFIX + str(new_version) + config.SUFFIX,
        commit=last_commit.sha,
        last_modified_datetime=(
            last_commit.commit.last_modified_datetime
            if last_commit.commit.last_modified_datetime
            else datetime.now()
        ),
    )
    return new_tag


repo = github_auth()
last_tag = get_latest_tag_or_default(repo)
bump_strategy = check_bump_strategy_since_last_tag(repo, last_tag)

if bump_strategy == BumpStrategy.SKIP:
    print("No need to create a new tag, skipping")
    quit()

new_tag = bump_tag_version(bump_strategy, last_tag, repo)
last_commit = get_last_commit(repo)
new_tag_date = (
    last_commit.commit.last_modified_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    if last_commit.commit.last_modified_datetime
    else datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
)

tag = repo.create_git_tag(
    new_tag.name,
    new_tag.message,
    new_tag.commit,
    new_tag.type,
    github.InputGitAuthor(
        last_commit.author.name, str(last_commit.author.email), str(new_tag_date)
    ),
)
print(f"Creating new tag: {new_tag.name}")
repo.create_git_ref(f"refs/tags/{new_tag.name}", tag.sha)
