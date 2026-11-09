import json
from hashlib import sha256
from io import BytesIO
from pathlib import Path, PurePosixPath
import re
import unittest
from zipfile import ZipFile

import yaml

from scripts import distribution


class Packages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = distribution.inputs()
        cls.files = distribution.output_files(cls.catalog)

    def load(self, path):
        return json.loads(self.files[Path(path)])

    def test_all_marketplaces_resolve_to_the_matching_plugin(self):
        codex = self.load(f"openai/.agents/plugins/marketplace.json")
        entry, = codex["plugins"]
        plugin = self.load(Path(f"openai", entry["source"]["path"], "plugin.json"))
        self.assertEqual(entry["name"], plugin["name"])
        claude = self.load(f"claude/.claude-plugin/marketplace.json")
        entry, = claude["plugins"]
        other = self.load(Path(f"claude", entry["source"], ".claude-plugin/plugin.json"))
        self.assertEqual(entry["name"], other["name"])
        self.assertEqual(plugin["name"], other["name"])
        self.assertEqual(plugin["version"], other["version"])
        self.assertEqual(
            plugin["extensions"]["com.openai"]["interface"]["displayName"], other["displayName"]
        )

    def test_production_endpoint_is_absent_until_verified(self):
        catalog = distribution.inputs()
        catalog["release"]["productionMcp"] = None
        files = distribution.output_files(catalog)
        gemini = json.loads(files[Path("gemini/garmin-mcp/gemini-extension.json")])
        self.assertNotIn("mcpServers", gemini)
        for path in ("openai/garmin-mcp/mcp.json", "claude/plugins/garmin-mcp/.mcp.json"):
            self.assertNotIn(Path(path), files)

    def test_verified_production_endpoint_uses_the_host_transport(self):
        catalog = distribution.inputs()
        url = "https://public.geekist.co/mcp"
        catalog["release"]["productionMcp"] = {"url": url, "verification": "synthetic test fixture"}
        files = distribution.output_files(catalog)
        for path, transport in (
            ("openai/garmin-mcp/mcp.json", "streamable-http"),
            ("claude/plugins/garmin-mcp/.mcp.json", "http"),
        ):
            servers = json.loads(files[Path(path)])["mcpServers"]
            self.assertEqual(servers, {"garmin-mcp": {"type": transport, "url": url}})
        with self.assertRaises(ValueError):
            catalog["release"]["productionMcp"]["url"] = "https://preview.geekist.co/mcp"
            distribution.output_files(catalog)
        with self.assertRaises(ValueError):
            catalog["release"]["productionMcp"] = {"url": url}
            distribution.output_files(catalog)

    def test_archives_have_self_contained_layout_and_matching_checksums(self):
        sums_path = Path("archives/SHA256SUMS")
        lines = self.files[sums_path].decode().splitlines()
        self.assertEqual(len(lines), 5)
        self.assertTrue(all("-review.zip" not in line for line in lines))
        for line in lines:
            checksum, name = line.split("  ", 1)
            with self.subTest(archive=name):
                content = self.files[sums_path.parent / name]
                self.assertEqual(sha256(content).hexdigest(), checksum)
                with ZipFile(BytesIO(content)) as archive:
                    members = archive.namelist()
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(members, sorted(set(members)))
                    self.assertTrue(all(
                        not PurePosixPath(path).is_absolute() and ".." not in PurePosixPath(path).parts
                        for path in members
                    ))
                    if "gemini-cli" in name:
                        self.assertIn("gemini-extension.json", members)
                        self.assertIn("GEMINI.md", members)
                        manifest = json.loads(archive.read("gemini-extension.json"))
                        self.assertEqual(manifest["mcpServers"]["garmin-mcp"], {"httpUrl": "https://garmin.geekist.co/mcp"})
                        self.assertNotIn("includeTools", manifest["mcpServers"]["garmin-mcp"])
                    elif "openai" in name:
                        self.assertIn("plugin.json", members)
                        self.assertNotIn("REVIEW.md", members)
                        self.assertFalse(any(path.startswith((".agents/", ".app.json")) for path in members))
                    elif "claude-code" in name:
                        self.assertIn(".claude-plugin/marketplace.json", members)
                    elif "claude-plugin" in name:
                        self.assertIn(".claude-plugin/plugin.json", members)
                        self.assertNotIn(".claude-plugin/marketplace.json", members)
                    else:
                        self.assertIn(".agents/plugins/marketplace.json", members)
                    skill, = (path for path in members if path.endswith("/SKILL.md"))
                    for reference in re.findall(rb"\((references/[^)]+)\)", archive.read(skill)):
                        self.assertIn(str(PurePosixPath(skill).parent / reference.decode()), members)
                    for entry in archive.infolist():
                        self.assertEqual(entry.date_time, (1980, 1, 1, 0, 0, 0))

    def test_claude_plugin_zip_contains_the_complete_marketplace_plugin(self):
        plugin_id = self.catalog["id"]
        plugin_dir = Path("claude", "plugins", plugin_id)
        filename = f'{plugin_id}-{self.catalog["version"]}-claude-plugin.zip'
        with ZipFile(BytesIO(self.files[Path("archives", filename)])) as archive:
            self.assertEqual(
                {name: archive.read(name) for name in archive.namelist()},
                {
                    path.relative_to(plugin_dir).as_posix(): content
                    for path, content in self.files.items()
                    if plugin_dir in path.parents
                },
            )
            manifest = json.loads(archive.read(".claude-plugin/plugin.json"))
            self.assertRegex(manifest["name"], r"^[a-z0-9-]{1,64}$")
            self.assertLessEqual(len(manifest["displayName"]), 64)
            self.assertLessEqual(len(manifest["description"]), 500)
            self.assertNotIn("license", manifest)
            license_text = archive.read("LICENSE").decode()
            self.assertIn("download, install, and use this package", license_text)
            self.assertIn("directory operators that Geekist expressly authorizes", license_text)
            self.assertIn("host and distribute\nunmodified copies", license_text)
            self.assertIn("may not modify, adapt, sublicense", license_text)
            self.assertIn("does not cover third-party materials", license_text)
            self.assertIn("does not grant rights to Garmin's names", license_text)
            self.assertEqual(archive.read("LICENSE"), (distribution.ROOT / "LICENSE").read_bytes())
            self.assertGreaterEqual(len(archive.read("README.md").decode().split()), 40)
            self.assertNotIn("review build", archive.read("README.md").decode().lower())
            release = self.catalog["release"]["productionMcp"]
            if release is not None:
                self.assertEqual(json.loads(archive.read(".mcp.json")), {
                    "mcpServers": {plugin_id: {"type": "http", "url": release["url"]}},
                })
            else:
                self.assertNotIn(".mcp.json", archive.namelist())

    def test_packaged_skill_has_valid_matching_frontmatter(self):
        for path, content in self.files.items():
            if path.name != "SKILL.md":
                continue
            first, delimiter, rest = content.decode().partition("\n---\n")
            self.assertTrue(first.startswith("---\n"))
            self.assertEqual(delimiter, "\n---\n")
            self.assertTrue(rest.strip())
            data = yaml.safe_load(first[4:])
            self.assertEqual(data["name"], path.parent.name)
            self.assertTrue(isinstance(data["description"], str) and data["description"].strip())
            self.assertLessEqual(len(data["description"]), 1024)

    def test_each_declared_icon_is_present(self):
        for path, content in self.files.items():
            if path.name != "plugin.json":
                continue
            manifest = json.loads(content)
            if "extensions" in manifest:
                interface = manifest["extensions"]["com.openai"]["interface"]
                paths = [interface["logo"], interface["composerIcon"]]
                plugin_root = path.parent
            else:
                paths = [manifest["icon"]]
                plugin_root = path.parent.parent
            for icon in paths:
                image = self.files[plugin_root / icon]
                self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
                width = int.from_bytes(image[16:20], "big")
                height = int.from_bytes(image[20:24], "big")
                self.assertEqual(width, height)
                self.assertTrue(48 <= width <= 4096)
                self.assertLessEqual(len(image), 5 * 1024 * 1024)
