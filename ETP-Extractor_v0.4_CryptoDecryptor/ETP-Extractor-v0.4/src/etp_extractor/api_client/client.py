from __future__ import annotations

import httpx


class ETPApiClient:
    """Cliente local de solo lectura para ETP.

    Los endpoints y headers definitivos deben validarse antes de su uso.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 13374,
        verify_tls: bool = False,
        timeout: float = 15.0,
    ) -> None:
        self.base_url = f"https://{host}:{port}"
        self.client = httpx.Client(
            base_url=self.base_url,
            verify=verify_tls,
            timeout=timeout,
            follow_redirects=False,
        )

    def get(self, path: str, params: dict | None = None) -> httpx.Response:
        if not path.startswith("/"):
            path = "/" + path
        return self.client.get(path, params=params)

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "ETPApiClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
