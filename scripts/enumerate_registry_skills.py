#!/usr/bin/env python3
"""Enumerate registry skills via the k8s live stack (internal token recipe).

契约见 MCP-REGISTRY.md §3.z 与 scripts/reconcile_mcp_registry.py：取 registry
pod 的 SECRET_KEY 自签内部 token（iss=mcp-auth-server / aud=mcp-registry-ui /
token_use=mcp-registry-ui / groups=[mcp-registry-admin]，X-Internal-Token-
Registry 头），pod 内 curl 内网 7860 分页读 /api/skills。
口径同 bridge mapSkill：在册且 is_enabled !== false。
产出 _sources/skills.registry.json 快照。
"""
import base64
import hashlib
import hmac
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCES = Path(__file__).resolve().parent.parent / "_sources"


def kubectl(args: list[str]) -> str:
    out = subprocess.run(["kubectl", "-n", "mcp-registry", *args],
                         capture_output=True, text=True, timeout=90, check=False)
    if out.returncode != 0:
        raise RuntimeError(f"kubectl {' '.join(args)} failed: {out.stderr[:400]}")
    return out.stdout


def registry_pod() -> str:
    rows = kubectl(["get", "pods", "-o", "name"]).splitlines()
    pod = next((l.strip() for l in rows if "pod/registry-" in l and "auth" not in l), None)
    if not pod:
        raise RuntimeError("registry pod not found")
    return pod


def internal_token(key: str) -> str:
    b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=")
    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = b64(json.dumps({
        "iss": "mcp-auth-server", "aud": "mcp-registry-ui",
        "token_use": "mcp-registry-ui", "groups": ["mcp-registry-admin"],
    }).encode())
    sig = b64(hmac.new(key.encode(), header + b"." + payload, hashlib.sha256).digest())
    return (header + b"." + payload + b"." + sig).decode()


def pod_curl(pod: str, token: str, path: str) -> dict:
    raw = kubectl(["exec", pod, "--", "sh", "-c",
                   f"curl -s -m 15 -H 'X-Internal-Token-Registry: {token}' 'http://127.0.0.1:7860{path}'"])
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"non-JSON response for {path}: {raw[:200]}") from e


def fetch_all_skills(pod: str, token: str) -> list[dict]:
    items: list[dict] = []
    offset = 0
    limit = 100
    seen_first: set[str] = set()
    for page in range(100):
        doc = pod_curl(pod, token, f"/api/skills?limit={limit}&offset={offset}")
        rows = doc.get("items") or doc.get("skills") or []
        first = (rows[0].get("path") if rows else None)
        if page > 0 and first and first in seen_first:
            print(f"pagination stuck at page {page + 1}, stopping", file=sys.stderr)
            break
        if first:
            seen_first.add(first)
        items.extend(rows)
        total = doc.get("total_count")
        has_next = doc.get("has_next")
        if has_next is None:
            has_next = (len(items) < int(total)) if total is not None else (len(rows) >= limit)
        print(f"page {page + 1}: +{len(rows)} (total {len(items)}, has_next={has_next})", file=sys.stderr)
        if not has_next or not rows:
            break
        offset += len(rows)
    return items


def main() -> None:
    key = kubectl(["exec", registry_pod(), "--", "sh", "-c", "echo -n \"$SECRET_KEY\""]).strip()
    if not key:
        raise RuntimeError("SECRET_KEY unavailable in registry pod")
    token = internal_token(key)
    pod = registry_pod()
    skills = fetch_all_skills(pod, token)

    enabled = []
    for s in skills:
        if not s.get("path") or s.get("is_enabled") is False:
            continue
        name = str(s["path"]).rstrip("/").split("/")[-1]
        enabled.append({
            "name": name,
            "path": s["path"],
            "displayName": s.get("name") or name,
            "description": (s.get("description") or "")[:200],
            "tags": [str(t) for t in (s.get("tags") or [])],
            "author": s.get("author"),
            "version": s.get("version"),
            "repository_url": s.get("repository_url"),
        })

    snapshot = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "registry-live",
        "endpoint": "/api/skills",
        "filter": "is_enabled !== false (same as bridge mapSkill)",
        "total": len(enabled),
        "skills": sorted(enabled, key=lambda x: x["name"]),
    }
    SOURCES.mkdir(exist_ok=True)
    out = SOURCES / "skills.registry.json"
    out.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out} ({len(enabled)} skills)", file=sys.stderr)


if __name__ == "__main__":
    main()
