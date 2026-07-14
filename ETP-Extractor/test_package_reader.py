from __future__ import annotations

from bs4 import BeautifulSoup

from etp_extractor.content_parser.models import ParsedDocument


class IPCParser:
    """Parser inicial de IPC.

    Se completará cuando tengamos muestras reales del HTML/XML devuelto por ETP.
    """

    def parse_html(self, html: str) -> ParsedDocument:
        soup = BeautifulSoup(html, "lxml")
        title = soup.title.get_text(strip=True) if soup.title else None
        return ParsedDocument(title=title)
