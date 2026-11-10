#!/usr/bin/env python3
"""Generate and check the public distribution seed without changing host settings."""

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from zipfile import ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_BASE = "https://agent-plugins.org/schemas/1.0.0/"
SCHEMAS = ROOT / "schemas/agent-plugins-1.0.0"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def public_https(value):
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    labels = host.split(".")
    return (
        parsed.scheme == "https" and len(value) <= 1024 and "." in host
        and all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label) for label in labels)
        and any(c.isalpha() for c in labels[-1])
        and labels[-1] not in {"invalid", "test", "example", "localhost", "local", "internal"}
        and "example" not in labels
        and not re.search(r"(^|[.-])(?:staging|stage|dev|sandbox|preview)([.-]|$)", host)
        and not (parsed.username or parsed.password or parsed.query or parsed.fragment)
    )


def inputs():
    catalog = read_json(ROOT / "catalogue/garmin.json")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", catalog["id"]):
        raise ValueError("Catalogue id must be lowercase kebab-case.")
    if not re.fullmatch(r"(?:0|[1-9]\d*)(?:\.(?:0|[1-9]\d*)){2}", catalog["version"]):
        raise ValueError("Catalogue version must have major, minor and patch numbers.")
    for name in ("displayName", "shortDescription"):
        if not 1 <= len(catalog[name].strip()) <= 30 or "\n" in catalog[name]:
            raise ValueError(f"{name} must be one line of 1–30 characters.")
    return catalog


def output_files(catalog):
    endpoint = None
    release = catalog["release"]["productionMcp"]
    if release is not None:
        endpoint = release["url"]
        if not public_https(endpoint) or not release.get("verification"):
            raise ValueError("Production MCP requires a public HTTPS URL and verification reference.")

    plugin_name = catalog["id"]
    openai = Path("openai", plugin_name)
    openai_marketplace = Path("openai/.agents/plugins/marketplace.json")
    claude = Path("claude")
    gemini = Path("gemini", plugin_name)
    claude_plugin = claude / "plugins" / plugin_name
    description = catalog["description"]
    package_readme = (
        "# Garmin by geekist.co\n\n"
        + (f"Live MCP endpoint: `{endpoint}`.\n\n" if endpoint else "")
        + "Connect a compatible MCP client to Geekist's Garmin service and follow the "
        "client's authentication flow. The server exposes the tools available to your "
        "account; review a tool's effect and confirm any requested Garmin change in "
        "your client before it is made.\n\n"
        "The included Garmin Review skill guides activity, trend, workout and supported "
        "change requests. Tool availability and client compatibility can vary. For "
        "setup guidance, see the package distribution README.\n"
    )
    shared = {
        "name": plugin_name,
        "version": catalog["version"],
        "description": description,
        "author": {"name": catalog["publisher"], "url": catalog["publisherWebsite"]},
    }
    logo = Path("assets/garmin-mcp-product-logo.png")
    logo_data = (ROOT / logo).read_bytes()
    license_text = (ROOT / "LICENSE").read_bytes()
    openai_manifest = {
        "$schema": SCHEMA_BASE + "plugin.schema.json",
        **shared,
        "extensions": {
            "com.openai": {
                "interface": {
                    "displayName": catalog["displayName"],
                    "shortDescription": catalog["shortDescription"],
                    "longDescription": description,
                    "developerName": catalog["publisher"],
                    "category": catalog["category"],
                    "websiteURL": "https://garmin.geekist.co/",
                    "supportURL": "https://garmin.geekist.co/support/",
                    "privacyPolicyURL": "https://garmin.geekist.co/privacy/",
                    "termsOfServiceURL": "https://garmin.geekist.co/terms/",
                    "defaultPrompt": catalog["candidatePrompts"],
                    "logo": f"./{logo.as_posix()}",
                    "composerIcon": f"./{logo.as_posix()}",
                },
                "review": {
                    "test_cases": {
                        "positive": [
                            {"description": "Compare runs across two weeks", "prompt": "Compare my runs in the last two complete weeks, including total distance and time.", "tools_triggered": "garmin_list_activities", "expected_behavior": "Compare the returned runs in equal date ranges and report dates and units."},
                            {"description": "Read a recent activity and laps", "prompt": "Show my latest run's corrected totals and lap timing.", "tools_triggered": "garmin_list_activities, garmin_get_activity, garmin_get_activity_laps", "expected_behavior": "Find the run and report current totals and lap timing from its returned data."},
                            {"description": "Read menstrual-cycle data when available", "prompt": "Show my Garmin menstrual-cycle data for November 9, 2026; if there is none, say so.", "tools_triggered": "garmin_get_menstrual_cycle_day", "expected_behavior": "Report only the connected account's returned data, distinguish estimates from logged records, or state that data is unavailable."},
                            {"description": "Preview a structured workout", "prompt": "Preview a cycling workout with four two-minute intervals; do not save it.", "tools_triggered": "garmin_preview_workout", "expected_behavior": "Show the workout preview without creating or saving a workout."},
                            {"description": "Send approved feedback to Geekist", "prompt": "Send Geekist this feedback: The activity comparison was easy to read.", "tools_triggered": "garmin_send_feedback", "expected_behavior": "Send only the requested text and report the returned submission status."}
                        ],
                        "negative": [
                            {"description": "Do not delete without an identified record and confirmation", "prompt": "Delete yesterday's activity without asking which one or confirming."},
                            {"description": "Do not save a workout when asked only for a preview", "prompt": "Preview a workout; do not save it."},
                            {"description": "Do not send unrequested feedback", "prompt": "Help me understand why my last run looks incomplete; do not send feedback."}
                        ]
                    },
                    "commerce": False
                },
                "publication": {"countries": [], "release_notes": "Improves Geekist attribution, feedback and service announcements, and client guidance."}
            },
        },
    }
    marketplace_name = "geekist-plugins"
    codex_marketplace = {
        "name": marketplace_name,
        "interface": {"displayName": "Geekist"},
        "plugins": [{
            "name": plugin_name,
            "source": {"source": "local", "path": f"./{plugin_name}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": catalog["category"],
        }],
    }
    claude_marketplace = {
        "name": marketplace_name,
        "owner": {"name": catalog["publisher"]},
        "plugins": [
            {"name": plugin_name, "source": f"./plugins/{plugin_name}", "description": description},
        ],
    }
    skill_root = ROOT / "skills"
    files = {
        openai / "plugin.json": encode_json(openai_manifest),
        openai_marketplace: encode_json(codex_marketplace),
        openai / logo: logo_data,
        openai / "LICENSE": license_text,
        claude / ".claude-plugin/marketplace.json": encode_json(claude_marketplace),
        claude_plugin / ".claude-plugin/plugin.json": encode_json({
            **shared, "displayName": catalog["displayName"], "icon": f"./{logo.as_posix()}",
        }),
        claude_plugin / logo: logo_data,
        gemini / "GEMINI.md": (ROOT / "providers/gemini/GEMINI.md").read_bytes(),
        gemini / "LICENSE": license_text,
        claude_plugin / "LICENSE": license_text,
        claude_plugin / "README.md": (
            package_readme
        ).encode(),
    }
    for path in sorted(skill_root.rglob("*.md")):
        if path.is_symlink():
            raise ValueError(f"Symlink in skill source: {path}")
        content = path.read_bytes()
        relative = path.relative_to(ROOT)
        for folder in (openai, claude_plugin, gemini):
            files[folder / relative] = content
    gemini_manifest = {"name": plugin_name, "version": catalog["version"], "description": description, "contextFileName": "GEMINI.md"}
    if endpoint is not None:
        gemini_manifest["mcpServers"] = {plugin_name: {"httpUrl": endpoint}}
    files[gemini / "gemini-extension.json"] = encode_json(gemini_manifest)
    if endpoint is not None:
        for path, transport, portable in (
            (openai / "mcp.json", "streamable-http", True),
            (claude_plugin / ".mcp.json", "http", False),
        ):
            mcp = {"mcpServers": {plugin_name: {"type": transport, "url": endpoint}}}
            if portable:
                mcp = {"$schema": SCHEMA_BASE + "mcp.schema.json", **mcp}
            files[path] = encode_json(mcp)
    archives = Path("archives")
    checksums = []
    for provider, folder in (
        ("gemini-cli", gemini),
        ("claude-code", claude),
        ("claude-plugin", claude_plugin),
        ("codex-marketplace", openai.parent),
        ("openai", openai),
    ):
        filename = f'{plugin_name}-{catalog["version"]}-{provider}.zip'
        archive = make_archive(files, folder)
        files[archives / filename] = archive
        checksums.append(f"{sha256(archive).hexdigest()}  {filename}\n")
    files[archives / "SHA256SUMS"] = "".join(checksums).encode()
    return files


def make_archive(files, folder):
    output = BytesIO()
    members = {
        path.relative_to(folder).as_posix(): content
        for path, content in files.items()
        if folder in path.parents
    }
    with ZipFile(output, "w") as archive:
        for filename in sorted(members):
            entry = ZipInfo(filename, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, members[filename])
    return output.getvalue()


def check_outputs(dist, expected):
    entries = list(dist.rglob("*"))
    links = [path.relative_to(dist) for path in entries if path.is_symlink()]
    if links or dist.is_symlink():
        raise ValueError(f"Generated output contains symlinks: {links or [dist]}")
    actual = {path.relative_to(dist) for path in entries if path.is_file()}
    missing = sorted(map(str, expected.keys() - actual))
    extra = sorted(map(str, actual - expected.keys()))
    changed = sorted(str(path) for path in actual & expected.keys()
                     if (dist / path).read_bytes() != expected[path])
    if missing or extra or changed:
        raise ValueError(f"Generated output differs. Missing: {missing}. Extra: {extra}. Changed: {changed}.")


def validate_upstream(expected, schema_dir):
    from jsonschema import Draft202012Validator

    for path, content in expected.items():
        if "openai" not in path.parts or path.name not in {"plugin.json", "mcp.json"}:
            continue
        filename = path.stem + ".schema.json"
        schema = read_json(schema_dir / filename)
        if schema.get("$id") != SCHEMA_BASE + filename:
            raise ValueError(f"Expected official Agent Plugins 1.0.0 schema: {filename}")
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(json.loads(content))
        print(f"Upstream schema passed for {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check", "release-check"))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist", help="Directory for generated files")
    parser.add_argument("--official-schemas", type=Path, nargs="?", const=SCHEMAS,
                        help="Check Agent Plugins schemas from the bundled or supplied directory")
    args = parser.parse_args()
    catalog = inputs()
    if args.command == "release-check":
        missing = [key for key, value in catalog["release"].items() if not value]
        if missing:
            print("Production release evidence pending: " + ", ".join(missing))
        else:
            print("Production release evidence recorded. Review provider requirements against the exact packages.")
        return
    files = output_files(catalog)
    dist = args.output_dir
    if args.command == "build":
        if dist.is_symlink() or any(path.is_symlink() for path in dist.rglob("*")):
            raise ValueError("Generated output directory contains symlinks.")
        for name, content in files.items():
            target = dist / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
    check_outputs(dist, files)
    if args.official_schemas:
        validate_upstream(files, args.official_schemas)
    print(f"{args.command} passed ({len(files)} generated files).")


if __name__ == "__main__":
    try:
        main()
    except (ImportError, OSError, ValueError, KeyError) as error:
        sys.exit(str(error))
