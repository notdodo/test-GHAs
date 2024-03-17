"""
Python script to generate a new GitHub tag bumping its version following semver rules
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import github
from github import Repository
from semver import Version


class BumpStrategy(Enum):
    """Enum containing the different version bump strategy for semver"""

    MAJOR: str = "major"
    MINOR: str = "minor"
    PATCH: str = "patch"
    SKIP: str = "skip"


@dataclass
class Tag:
    """Tag resource"""

    name: str
    commit: str
    message: str = ""
    type: str = "commit"


@dataclass
class Configuration:
    """Configuration resource"""

    # pylint: disable=invalid-name
    DEFAULT_BUMP_STRATEGY: BumpStrategy = BumpStrategy.SKIP
    DEFAULT_BRANCH: str = "main"
    PREFIX: str = "v"
    SUFFIX: str = ""


config = Configuration(
    DEFAULT_BUMP_STRATEGY=BumpStrategy(
        os.environ.get("INPUT_BUMP_STRATEGY", Configuration.DEFAULT_BUMP_STRATEGY.value)
    ),
    DEFAULT_BRANCH=os.environ.get("INPUT_MAIN_BRANCH", Configuration.DEFAULT_BRANCH),
    PREFIX=os.environ.get("INPUT_PREFIX", Configuration.PREFIX),
    SUFFIX=os.environ.get("INPUT_SUFFIX", Configuration.SUFFIX),
)

if os.environ.get("GITHUB_REF_NAME") != config.DEFAULT_BRANCH:
    print("Not running from the default branch")
    sys.exit()


def github_auth() -> Repository.Repository:
    """Authenticate to GitHub and set the scope to this repository"""
    auth = github.Github(os.environ.get("INPUT_GITHUB_TOKEN", ""))
    return auth.get_repo(os.environ.get("GITHUB_REPOSITORY", ""))


def get_latest_tag_or_default(repository: Repository.Repository) -> Tag:
    """Get the latest available tag on the repository"""
    try:
        _last_tag = repository.get_tags().get_page(0)[0]
        last_available_tag = Tag(
            name=_last_tag.name,
            commit=_last_tag.commit.sha,
        )
    except IndexError:
        last_available_tag = Tag(
            name=config.PREFIX + "0.0.0" + config.SUFFIX,
            commit=repository.get_commits()[0].sha,
        )
    return last_available_tag


def check_bump_strategy_since_last_tag(
    repository: Repository.Repository, last_available_tag: Tag
) -> BumpStrategy:
    """Select the correct bump strategy based on commit message or the default one"""
    strategies = [strategy.value for strategy in BumpStrategy]
    last_commits_since_tag = repository.get_commits(
        sha=last_available_tag.commit
    )  # TODO: this should be since=datetime
    for commit in last_commits_since_tag:
        for strategy in strategies:
            if f"[#{strategy.lower()}]" in commit.commit.message:
                return BumpStrategy(strategy)
    return config.DEFAULT_BUMP_STRATEGY


def bump_tag_version(strategy: BumpStrategy, last_available_tag: Tag) -> Tag:
    """Create a new Tag resource with the increased version number"""
    current_version = Version.parse(
        last_available_tag.name.removeprefix(config.PREFIX).removesuffix(config.SUFFIX)
    )
    new_version = current_version
    if strategy == BumpStrategy.MAJOR:
        new_version = current_version.bump_major()
    elif strategy == BumpStrategy.MINOR:
        new_version = current_version.bump_minor()
    elif strategy == BumpStrategy.PATCH:
        new_version = current_version.bump_patch()

    return Tag(
        name=config.PREFIX + str(new_version) + config.SUFFIX,
        commit=os.environ.get("GITHUB_SHA", ""),
    )


repo = github_auth()
last_tag = get_latest_tag_or_default(repo)
bump_strategy = check_bump_strategy_since_last_tag(repo, last_tag)

if bump_strategy == BumpStrategy.SKIP:
    print("No need to create a new tag, skipping")
    sys.exit()

new_tag = bump_tag_version(bump_strategy, last_tag)
last_commit = repo.get_commit(
    os.environ.get("GITHUB_SHA", repo.get_commits().get_page(0)[0].sha)
)
new_tag_date = (
    last_commit.commit.last_modified_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
    if last_commit.commit.last_modified_datetime
    else datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
)

if last_commit.commit.sha == last_tag.commit:
    print("Nothing to do")
    sys.exit()

tag = repo.create_git_tag(
    new_tag.name,
    new_tag.message,
    new_tag.commit,
    new_tag.type,
    github.InputGitAuthor(
        str(last_commit.author.name), str(last_commit.author.email), str(new_tag_date)
    ),
)

print(last_tag)
print(new_tag)
print(bump_strategy)
print(last_commit)

print(f"Creating new tag: {new_tag.name}")
repo.create_git_ref(f"refs/tags/{new_tag.name}", tag.sha)
