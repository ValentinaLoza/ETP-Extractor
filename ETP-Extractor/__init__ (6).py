from __future__ import annotations

import re
from pathlib import Path

from etp_extractor.angular_analyzer.models import (
    AngularAnalysisReport,
    Evidence,
    RouteFinding,
    TokenFlow,
)


ROUTE_RE = re.compile(r'["\'](/api/[A-Za-z0-9_./?=&:${}\-]+)["\']')
HTTP_CALL_RE = re.compile(
    r'\.http\.(get|post|put|delete|patch)\((?:`|\")?([^,)"`]+)',
    re.IGNORECASE,
)

KEYWORDS = [
    "HttpInterceptor",
    "intercept(",
    "Authorization",
    "Bearer",
    "withCredentials",
    "manual/toc",
    "content/digital",
    "/api/library",
    "/api/auth",
    "localStorage",
    "getToken",
    "setToken",
    "onToken",
    "token-callback",
]


def context(text: str, offset: int, radius: int = 550) -> str:
    start = max(0, offset - radius)
    end = min(len(text), offset + radius)
    return text[start:end]


class AngularAnalyzer:
    def __init__(self, input_dir: Path, electron_dir: Path | None = None) -> None:
        self.input_dir = input_dir
        self.electron_dir = electron_dir

    def analyze(self) -> AngularAnalysisReport:
        report = AngularAnalysisReport()
        route_map: dict[str, RouteFinding] = {}

        for file_path in sorted(self.input_dir.rglob("*.js")):
            report.files_scanned.append(str(file_path))
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                report.errors.append(f"{file_path}: {exc}")
                continue

            for match in ROUTE_RE.finditer(content):
                route = match.group(1)
                finding = route_map.setdefault(route, RouteFinding(route=route))
                finding.evidence.append(
                    Evidence(
                        file=str(file_path),
                        offset=match.start(),
                        snippet=context(content, match.start(), 260),
                    )
                )

            for keyword in KEYWORDS:
                if keyword.lower() in content.lower():
                    report.keywords_found.setdefault(keyword, []).append(str(file_path))

            # Custom authentication interceptor found in ETP client.
            token_pattern = 'this.auth.state.token&&!t.params.get("token")'
            pos = content.find(token_pattern)
            if pos >= 0:
                ev = Evidence(
                    file=str(file_path),
                    offset=pos,
                    snippet=context(content, pos, 700),
                )
                report.possible_interceptors.append(ev)
                report.token_flow.interceptor_found = True
                report.token_flow.query_parameter = "token"
                report.token_flow.evidence.append(ev)

            # Angular auth store receives the token from Electron IPC.
            for pattern in ("this.ipc.api.getToken()", "this.ipc.api.setToken(t)", "this.ipc.api.onToken"):
                pos = content.find(pattern)
                if pos >= 0:
                    report.token_flow.evidence.append(
                        Evidence(
                            file=str(file_path),
                            offset=pos,
                            snippet=context(content, pos, 500),
                        )
                    )

        if self.electron_dir and self.electron_dir.exists():
            self._analyze_electron(report)

        report.routes = sorted(route_map.values(), key=lambda item: item.route)
        for values in report.keywords_found.values():
            values[:] = sorted(set(values))
        return report

    def _analyze_electron(self, report: AngularAnalysisReport) -> None:
        channel_map = {
            "GET_TOKEN": "get-token",
            "SET_TOKEN": "set-token",
            "TOKEN_CALLBACK": "token-callback",
        }

        for file_path in sorted(self.electron_dir.rglob("*.js")):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for label, value in channel_map.items():
                pos = content.find(value)
                if pos >= 0:
                    evidence = Evidence(
                        file=str(file_path),
                        offset=pos,
                        snippet=context(content, pos, 420),
                    )
                    report.ipc_findings.append(evidence)
                    report.token_flow.evidence.append(evidence)
                    if label == "GET_TOKEN":
                        report.token_flow.electron_get_channel = value
                    elif label == "SET_TOKEN":
                        report.token_flow.electron_set_channel = value
                    else:
                        report.token_flow.electron_callback_channel = value

            pos = content.find("Helpers.getInstance().token")
            if pos >= 0:
                report.token_flow.storage = "Electron main-process memory (Helpers singleton)"
                evidence = Evidence(
                    file=str(file_path),
                    offset=pos,
                    snippet=context(content, pos, 520),
                )
                report.ipc_findings.append(evidence)
                report.token_flow.evidence.append(evidence)
