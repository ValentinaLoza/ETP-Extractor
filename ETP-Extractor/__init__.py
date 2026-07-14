#!/usr/bin/env python3
"""Analizador autónomo de bundles ETP. Solo lectura; usa la biblioteca estándar."""

from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

ROUTE_RE = re.compile(r'["\'](/api/[A-Za-z0-9_./?=&:${}\-]+)["\']')


def snippet(text: str, offset: int, radius: int = 450) -> str:
    return text[max(0, offset-radius):min(len(text), offset+radius)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_dir", type=Path)
    parser.add_argument("--electron-dir", type=Path)
    parser.add_argument("--output", type=Path, default=Path("angular_analysis.json"))
    args = parser.parse_args()

    report = {
        "routes": {},
        "token_flow": {
            "interceptor_found": False,
            "query_parameter": None,
            "electron_channels": {},
            "storage": None,
            "evidence": [],
        },
        "files_scanned": [],
    }

    for path in args.bundle_dir.rglob("*.js"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        report["files_scanned"].append(str(path))
        for m in ROUTE_RE.finditer(text):
            report["routes"].setdefault(m.group(1), []).append({
                "file": str(path), "offset": m.start(), "snippet": snippet(text, m.start(), 220)
            })

        p = text.find('this.auth.state.token&&!t.params.get("token")')
        if p >= 0:
            report["token_flow"]["interceptor_found"] = True
            report["token_flow"]["query_parameter"] = "token"
            report["token_flow"]["evidence"].append({
                "file": str(path), "offset": p, "snippet": snippet(text, p, 650)
            })

    if args.electron_dir and args.electron_dir.exists():
        for path in args.electron_dir.rglob("*.js"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for channel in ("get-token", "set-token", "token-callback"):
                p = text.find(channel)
                if p >= 0:
                    report["token_flow"]["electron_channels"][channel] = str(path)
                    report["token_flow"]["evidence"].append({
                        "file": str(path), "offset": p, "snippet": snippet(text, p)
                    })
            p = text.find("Helpers.getInstance().token")
            if p >= 0:
                report["token_flow"]["storage"] = "Electron main-process memory (Helpers singleton)"

    report["routes"] = dict(sorted(report["routes"].items()))
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Informe: {args.output}")
    print(f"Rutas: {len(report['routes'])}")
    print(f"Interceptor token: {report['token_flow']['interceptor_found']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
