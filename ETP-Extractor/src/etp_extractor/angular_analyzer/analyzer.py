from __future__ import annotations

import re
from pathlib import Path

from etp_extractor.angular_analyzer.models import AngularAnalysisReport


API_ROUTE_RE = re.compile(r'["\'](/api/[A-Za-z0-9_./?=&:${}\-]+)["\']')
KEYWORDS = [
    "HttpInterceptor",
    "Authorization",
    "Bearer",
    "withCredentials",
    "manual/toc",
    "content/digital",
    "library",
    "cookie",
    "token",
]


class AngularAnalyzer:
    def __init__(self, input_dir: Path) -> None:
        self.input_dir = input_dir

    def analyze(self) -> AngularAnalysisReport:
        report = AngularAnalysisReport()

        for file_path in sorted(self.input_dir.rglob("*.js")):
            report.files_scanned.append(str(file_path))
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError as exc:
                report.errors.append(f"{file_path}: {exc}")
                continue

            report.api_routes.extend(API_ROUTE_RE.findall(content))

            for keyword in KEYWORDS:
                if keyword.lower() in content.lower():
                    report.keywords_found.setdefault(keyword, []).append(str(file_path))

            if "intercept(" in content or "HttpInterceptor" in content:
                report.possible_interceptors.append(str(file_path))

        report.api_routes = sorted(set(report.api_routes))
        report.possible_interceptors = sorted(set(report.possible_interceptors))
        report.keywords_found = {
            key: sorted(set(values)) for key, values in report.keywords_found.items()
        }
        return report
