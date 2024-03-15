#!/usr/bin/env python3

import os

# Config
default_semvar_bump = os.getenv("DEFAULT_BUMP", "minor")
default_branch = os.getenv("DEFAULT_BRANCH", os.getenv("GITHUB_BASE_REF"))
with_v = os.getenv("WITH_V", "false").lower() == "true"
release_branches = os.getenv("RELEASE_BRANCHES", "master,main").split(",")
custom_tag = os.getenv("CUSTOM_TAG", "")
source = os.getenv("SOURCE", ".")
dryrun = os.getenv("DRY_RUN", "false").lower() == "true"
git_api_tagging = os.getenv("GIT_API_TAGGING", "true").lower() == "true"
initial_version = os.getenv("INITIAL_VERSION", "0.0.0")
tag_context = os.getenv("TAG_CONTEXT", "repo")
prerelease = os.getenv("PRERELEASE", "false").lower() == "true"
suffix = os.getenv("PRERELEASE_SUFFIX", "beta")
verbose = os.getenv("VERBOSE", "false").lower() == "true"
major_string_token = os.getenv("MAJOR_STRING_TOKEN", "#major")
minor_string_token = os.getenv("MINOR_STRING_TOKEN", "#minor")
patch_string_token = os.getenv("PATCH_STRING_TOKEN", "#patch")
none_string_token = os.getenv("NONE_STRING_TOKEN", "#none")
branch_history = os.getenv("BRANCH_HISTORY", "compare")
force_without_changes = os.getenv("FORCE_WITHOUT_CHANGES", "false").lower() == "true"

os.chdir(os.path.join(os.getenv("GITHUB_WORKSPACE"), source))

# Print configuration
print("*** CONFIGURATION ***")
print(f"\tDEFAULT_BUMP: {default_semvar_bump}")
print(f"\tDEFAULT_BRANCH: {default_branch}")
print(f"\tWITH_V: {with_v}")
print(f"\tRELEASE_BRANCHES: {release_branches}")
print(f"\tCUSTOM_TAG: {custom_tag}")
print(f"\tSOURCE: {source}")
print(f"\tDRY_RUN: {dryrun}")
print(f"\tGIT_API_TAGGING: {git_api_tagging}")
print(f"\tINITIAL_VERSION: {initial_version}")
print(f"\tTAG_CONTEXT: {tag_context}")
print(f"\tPRERELEASE: {prerelease}")
print(f"\tPRERELEASE_SUFFIX: {suffix}")
print(f"\tVERBOSE: {verbose}")
print(f"\tMAJOR_STRING_TOKEN: {major_string_token}")
print(f"\tMINOR_STRING_TOKEN: {minor_string_token}")
print(f"\tPATCH_STRING_TOKEN: {patch_string_token}")
print(f"\tNONE_STRING_TOKEN: {none_string_token}")
print(f"\tBRANCH_HISTORY: {branch_history}")
print(f"\tFORCE: {force_without_changes}")
