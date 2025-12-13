#!/usr/bin/env python3
import os
import json
import yaml
import argparse
import sys
from typing import List, Dict, Any

# We use packaging.version for robust version comparison
try:
    from packaging import version
except ImportError:
    print("::warning:: 'packaging' library not found. Version comparison might be less robust.")
    version = None

def error(message: str, file: str = None, line: int = None, col: int = None):
    """Prints error in GitHub Actions format."""
    location = ""
    if file:
        location += f"file={file}"
    if line:
        location += f",line={line}"
    if col:
        location += f",col={col}"

    if location:
        print(f"::error {location}::{message}")
    else:
        print(f"::error::{message}")
    print(f"ERROR: {message}", file=sys.stderr)

def validate_addons_json(repo_path: str) -> Dict[str, Any]:
    json_path = os.path.join(repo_path, "addons.json")
    if not os.path.exists(json_path):
        error("addons.json missing in repository root", file=json_path)
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in addons.json: {e.msg}", file=json_path, line=e.lineno, col=e.colno)
        return None

    if "addons" not in data or not isinstance(data["addons"], list):
        error("addons.json must contain a top-level 'addons' list", file=json_path)
        return None

    return data

def validate_addon_directory(repo_path: str, addon_id: str, core_version: str = None) -> bool:
    addon_path = os.path.join(repo_path, addon_id)
    if not os.path.isdir(addon_path):
        error(f"Directory not found for addon '{addon_id}'", file=addon_path)
        return False

    # Check manifest.json
    manifest_path = os.path.join(addon_path, "manifest.json")
    if not os.path.exists(manifest_path):
        error(f"Missing manifest.json for addon '{addon_id}'", file=manifest_path)
        return False

    manifest = None
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in manifest.json for '{addon_id}': {e}", file=manifest_path)
        return False

    # Required Fields Check
    required_manifest_fields = ["domain", "name", "version"]
    for field in required_manifest_fields:
        if field not in manifest:
            error(f"manifest.json missing required field '{field}'", file=manifest_path)
            return False

    # Domain Validation (Simple)
    domain = manifest.get("domain")
    if not domain.isidentifier():
         error(f"Invalid domain '{domain}'. Must be a valid identifier (alphanumeric, underscore).", file=manifest_path)
         return False

    # Check Implementations
    implementations = manifest.get("implementations")
    if not implementations or not isinstance(implementations, dict):
        # Allow legacy fallback logic or error?
        # For this refactor, let's enforce 'implementations' OR 'integration.py' implicit
        # But user asked for Polyglot. Let's warn if missing.
        if os.path.exists(os.path.join(addon_path, "integration.py")):
             # Implicit python support
             pass
        else:
             error(f"manifest.json in '{addon_id}' missing 'implementations' map, and no implicit 'integration.py' found.", file=manifest_path)
             return False

    if implementations:
        for lang, filename in implementations.items():
            file_path = os.path.join(addon_path, filename)
            if not os.path.exists(file_path):
                 error(f"Implementation file '{filename}' for '{lang}' not found in '{addon_id}'", file=file_path)
                 return False

    # Check Core Version Compatibility
    min_ver = manifest.get("min_core_version")
    if min_ver and core_version and version:
        try:
            if version.parse(min_ver) > version.parse(core_version):
                error(f"Addon '{addon_id}' requires Core >= {min_ver}, but current Core is {core_version}", file=manifest_path)
                return False
        except Exception as e:
             error(f"Version comparison failed for '{addon_id}' (min: {min_ver}, core: {core_version}): {e}", file=manifest_path)
             return False

    return True

def main():
    parser = argparse.ArgumentParser(description="Validate Addon Repository")
    parser.add_argument("repo_path", help="Path to the repository root")
    parser.add_argument("--core-version", help="Current version of faneX-ID Core to check compatibility against", default=None)
    args = parser.parse_args()

    repo_path = os.path.abspath(args.repo_path)
    core_ver = args.core_version

    print(f"Validating repository at: {repo_path}")
    if core_ver:
        print(f"Checking compatibility against Core Version: {core_ver}")

    # 1. Validate addons.json
    db = validate_addons_json(repo_path)
    if not db:
        sys.exit(1)

    success = True

    # 2. Iterate through addons
    for i, addon in enumerate(db["addons"]):
        # Minimal check on addons.json entry format could persist, but directory check is more important
        addon_id = addon.get("id")
        if not addon_id:
             error(f"Addon entry at index {i} missing 'id'", file=os.path.join(repo_path, "addons.json"))
             success = False
             continue

        print(f"Validating addon: {addon_id}...")

        if not validate_addon_directory(repo_path, addon_id, core_ver):
            success = False

    if not success:
        print("Validation FAILED.")
        sys.exit(1)

    print("Validation SUCCESSFUL.")
    sys.exit(0)

if __name__ == "__main__":
    main()
