#!/usr/bin/env python3
"""Build and inspect JOY's public-directory ZIP. Never claims review approval."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "chatgpt-plugin" / "joy-automart"


def compatibility_files(manifest, mcp):
    """Keep the portable source and Codex fallback metadata in sync."""
    settings = deepcopy(manifest["extensions"]["com.openai"])
    overlay = {key: deepcopy(value) for key, value in manifest.items()
               if key not in {"$schema", "extensions"}}
    overlay["mcpServers"] = "./.mcp.json"
    overlay["interface"] = settings.pop("interface")
    overlay["extensions"] = {"com.openai": settings}
    # Codex's documented HTTP format uses url. The portable transport and
    # authentication stay explicit in mcp.json; the public endpoint needs no key.
    legacy_mcp = {"mcpServers": {
        name: {"url": server["url"]}
        for name, server in mcp["mcpServers"].items()
    }}
    return {".codex-plugin/plugin.json": overlay, ".mcp.json": legacy_mcp}


def inspect_archive(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), "Duplicate archive entries"
        assert {"plugin.json", "mcp.json", ".codex-plugin/plugin.json", ".mcp.json"} <= set(names), "Upload the standalone plugin ZIP; manifests must be at the ZIP root"
        assert all(".." not in PurePosixPath(n).parts for n in names), "Unsafe archive path"
        assert all(not PurePosixPath(n).is_absolute() for n in names), "Unsafe absolute archive path"
        assert not any(n.lower().endswith(".zip") for n in names), "Nested ZIP kits are not plugin uploads"
        assert not any(n.endswith(".app.json") for n in names), "Private app bindings forbidden"
        assert z.testzip() is None, "Corrupt archive entry"
        manifest = json.loads(z.read("plugin.json"))
        mcp = json.loads(z.read("mcp.json"))
        assert manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
        assert manifest["name"] == "joy-automart"
        assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
        assert not {"apps", "skills", "mcpServers", "interface"}.intersection(manifest)
        settings = manifest["extensions"]["com.openai"]
        assert settings.get("apps") is None
        for name, expected in compatibility_files(manifest, mcp).items():
            assert json.loads(z.read(name)) == expected, "Compatibility metadata drift: " + name
        overlay = json.loads(z.read(".codex-plugin/plugin.json"))
        assert overlay.get("apps") is None
        assert overlay["extensions"]["com.openai"].get("apps") is None
        assert overlay["mcpServers"] == "./.mcp.json"
        ui = settings["interface"]
        for field, limit in [("displayName", 30), ("shortDescription", 30), ("longDescription", 4000)]:
            assert isinstance(ui[field], str) and 0 < len(ui[field]) <= limit, field
        assert ui["category"] in {
            "Business & Operations", "Communication", "Creativity", "Data & Analytics",
            "Developer Tools", "Education & Research", "Entertainment", "Finance",
            "Healthcare", "Other", "Productivity", "Scientific Research", "Security", "Travel"
        }
        prompts = ui["defaultPrompt"]
        assert 1 <= len(prompts) <= 3 and len(set(" ".join(p.split()) for p in prompts)) == len(prompts)
        assert all(0 < len(p) <= 128 and "\n" not in p for p in prompts)
        for field in ["websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"]:
            assert ui[field].startswith("https://www.joyautomart.com/") and len(ui[field]) <= 1024, field
        for field in ["logo", "composerIcon"]:
            rel = PurePosixPath(ui[field])
            assert not rel.is_absolute() and ".." not in rel.parts
            data = z.read(str(rel))
            assert data[:8] == b"\x89PNG\r\n\x1a\n", "PNG icon required"
            width, height = struct.unpack(">II", data[16:24])
            assert width == height and (256 if field == "logo" else 48) <= width <= 4096
            assert len(data) <= 5 * 1024 * 1024
        review = settings["review"]
        cases = review["test_cases"]
        assert len(cases["positive"]) == 5 and len(cases["negative"]) == 3
        for case in cases["positive"]:
            assert all(isinstance(case[k], str) and case[k].strip() for k in ["description", "prompt", "tools_triggered", "expected_behavior"])
        for case in cases["negative"]:
            assert all(isinstance(case[k], str) and case[k].strip() for k in ["description", "prompt"])
        assert isinstance(review["commerce"], bool) and review["commerce_description"].strip()
        assert settings["publication"]["countries"] == [], "Global directory targeting requested"
        assert settings["publication"]["release_notes"].strip()
        assert mcp["$schema"] == "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
        assert set(mcp["mcpServers"]) == {"joy-automart"}
        connection = mcp["mcpServers"]["joy-automart"]
        assert connection["type"] == "streamable-http"
        assert connection["url"] == "https://www.joyautomart.com/mcp"
        assert connection["extensions"]["com.openai"]["auth"] == {"type": "none"}
        assert not any(k in connection for k in ["headers", "env", "command"])
        gaps = []
        if not ui.get("developerName"):
            gaps.append("Confirm intended verified publisher identity and set developerName")
        if not review.get("demo_recording_url"):
            gaps.append("Record real in-host demo, verify accessible playback URL and add demo_recording_url")
        gaps += [
            "Owner confirmation of commerce declaration",
            "Final saved portal version connection, in-host cases, required scans and domain/developer verification",
            "Authorised developer legal/policy attestations, submission, OpenAI approval, then publication"
        ]
        return {"archive": str(path), "structural_validation": "PASS", "compatibility_manifest_validation": "PASS", "direct_upload_archive": True, "version": manifest["version"],
                "short_description_characters": len(ui["shortDescription"]), "inventory": names,
                "public_submission_ready": False, "remaining": gaps,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    assert not output.is_relative_to(SOURCE), "Write the archive outside its source"
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((SOURCE / "plugin.json").read_text())
    mcp = json.loads((SOURCE / "mcp.json").read_text())
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(SOURCE.rglob("*")):
            assert not path.is_symlink(), "Symlinks are forbidden"
            if path.is_file():
                z.write(path, path.relative_to(SOURCE).as_posix())
        for name, content in compatibility_files(manifest, mcp).items():
            z.writestr(name, json.dumps(content, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(inspect_archive(output), indent=2))


if __name__ == "__main__":
    main()
