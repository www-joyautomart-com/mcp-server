#!/usr/bin/env python3
"""Build and inspect JOY's public-directory ZIP. Never claims review approval."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "chatgpt-plugin" / "joy-automart"


def inspect_archive(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        assert len(names) == len(set(names)), "Duplicate archive entries"
        assert all(n.startswith("joy-automart/") for n in names), "One plugin root required"
        assert all(".." not in PurePosixPath(n).parts for n in names), "Unsafe archive path"
        assert not any(n.endswith(".app.json") for n in names), "Private app bindings forbidden"
        manifest = json.loads(z.read("joy-automart/plugin.json"))
        mcp = json.loads(z.read("joy-automart/mcp.json"))
        assert manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
        assert manifest["name"] == "joy-automart"
        assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
        assert not {"apps", "skills", "mcpServers", "interface"}.intersection(manifest)
        settings = manifest["extensions"]["com.openai"]
        assert settings.get("apps") is None
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
            data = z.read("joy-automart/" + str(rel))
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
        return {"archive": str(path), "structural_validation": "PASS", "version": manifest["version"],
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
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(SOURCE.rglob("*")):
            assert not path.is_symlink(), "Symlinks are forbidden"
            if path.is_file():
                z.write(path, "joy-automart/" + path.relative_to(SOURCE).as_posix())
    print(json.dumps(inspect_archive(output), indent=2))


if __name__ == "__main__":
    main()
