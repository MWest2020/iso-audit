"""Miro REST-API-client met retry, rate-limit, en throttle.

Eén gedeelde laag voor alle `iso_audit.miro.*`-modules. Vervangt de
verspreide `_headers()` / `_post()` / `_haal_items_op()` patronen uit
`Ops_to_Biz/audit/miro_*.py`.

## Ontwerpkeuzes

- **Stateless client met token-fetch per request** — geen herauthenticatie-
  logica; token komt uit `MIRO_API_TOKEN` env-var en wordt elke request
  opgehaald zodat `.env`-wisselingen tijdens lange runs werken.
- **Rate-limit honored** — HTTP 429 leest `Retry-After`-header en slaapt;
  daarna één retry. Bij blijvend 429 → `MiroRateLimitError` (caller-keuze
  hoe verder).
- **Vriendelijke throttle** — vaste 0.15s na elke succesvolle write, gelijk
  aan de oude `miro_board_setup`-pacing. Reads hebben geen vaste throttle
  (Miro's GET-API is ruimer).
- **`droog`-mode** — POST's loggen alleen, geven `{"id": "dry-run"}` terug.
  GET's hebben geen `droog` (read is per definitie side-effect-free).
- **Pagination via `paginated_get`** — generator die alle items over `cursor`
  yieldt; voorkomt out-of-memory bij grote borden.

## Niet in scope

- Async / batching — Miro v2 ondersteunt geen batch-write; sequentieel is OK.
- Backoff-jitter — voor één-retry niet nodig; bij meer retries zou jitter
  verstandig zijn.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterator
from typing import Any

import requests

logger = logging.getLogger(__name__)

MIRO_API_BASE = "https://api.miro.com/v2"
MIRO_API_TOKEN_ENV = "MIRO_API_TOKEN"  # nosec B105 — env-var-naam, geen waarde
DEFAULT_TIMEOUT = 30.0
DEFAULT_THROTTLE_SECONDS = 0.15
DEFAULT_PAGE_SIZE = 50


class MiroError(RuntimeError):
    """Algemene Miro-API-fout."""


class MiroRateLimitError(MiroError):
    """Rate-limit blijft 429 geven na één retry."""


class MiroClient:
    """Stateless wrapper rond `requests` voor de Miro v2 API.

    Stateless: de client onthoudt geen sessie-info; elke call leest het
    token uit env. Test-friendly: gedrag is afhankelijk van de
    `requests`-module die met `unittest.mock.patch` is te vervangen.
    """

    def __init__(
        self,
        base_url: str = MIRO_API_BASE,
        timeout: float = DEFAULT_TIMEOUT,
        throttle_seconds: float = DEFAULT_THROTTLE_SECONDS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.throttle_seconds = throttle_seconds

    # ---------- helpers ----------

    def _headers(self, *, content_type_json: bool = False) -> dict[str, str]:
        """Bouw request-headers; voeg `Content-Type` toe voor write-requests."""
        token = os.environ.get(MIRO_API_TOKEN_ENV)
        if not token:
            raise MiroError(f"{MIRO_API_TOKEN_ENV} niet ingesteld in .env")
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if content_type_json:
            headers["Content-Type"] = "application/json"
        return headers

    def _url(self, endpoint: str) -> str:
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        return f"{self.base_url}/{endpoint}"

    @staticmethod
    def _retry_after(resp: requests.Response, fallback: int = 5) -> int:
        try:
            return int(resp.headers.get("Retry-After", fallback))
        except (TypeError, ValueError):
            return fallback

    # ---------- public API ----------

    def post(
        self,
        endpoint: str,
        body: dict[str, Any],
        droog: bool = False,
    ) -> dict[str, Any]:
        """POST naar `endpoint` met JSON-body. Eén retry bij 429.

        Returnt de JSON-respons. In `droog`-mode logt het bericht en
        geeft `{"id": "dry-run"}` zonder netwerkverkeer.
        """
        if droog:
            logger.debug("DRY-RUN POST %s: keys=%s", endpoint, list(body.keys()))
            return {"id": "dry-run"}
        resp = self._post_once(endpoint, body)
        if resp.status_code == 429:
            wait = self._retry_after(resp)
            logger.warning("Miro rate limit op POST %s — wacht %ds", endpoint, wait)
            time.sleep(wait)
            resp = self._post_once(endpoint, body)
            if resp.status_code == 429:
                raise MiroRateLimitError(
                    f"POST {endpoint} blijft 429 na één retry (Retry-After={wait}s)"
                )
        if not resp.ok:
            logger.error(
                "Miro API fout %d op POST %s: %s", resp.status_code, endpoint, resp.text[:200]
            )
            resp.raise_for_status()
        time.sleep(self.throttle_seconds)
        data: dict[str, Any] = resp.json()
        return data

    def _post_once(self, endpoint: str, body: dict[str, Any]) -> requests.Response:
        return requests.post(
            self._url(endpoint),
            json=body,
            headers=self._headers(content_type_json=True),
            timeout=self.timeout,
        )

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """GET-call. Eén retry bij 429."""
        resp = self._get_once(endpoint, params)
        if resp.status_code == 429:
            wait = self._retry_after(resp)
            logger.warning("Miro rate limit op GET %s — wacht %ds", endpoint, wait)
            time.sleep(wait)
            resp = self._get_once(endpoint, params)
            if resp.status_code == 429:
                raise MiroRateLimitError(
                    f"GET {endpoint} blijft 429 na één retry (Retry-After={wait}s)"
                )
        if not resp.ok:
            logger.error(
                "Miro API fout %d op GET %s: %s", resp.status_code, endpoint, resp.text[:200]
            )
            resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        return data

    def _get_once(self, endpoint: str, params: dict[str, Any] | None) -> requests.Response:
        return requests.get(
            self._url(endpoint),
            headers=self._headers(),
            params=params,
            timeout=self.timeout,
        )

    def paginated_get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Iterator[dict[str, Any]]:
        """Yield alle items over `cursor`-paginatie.

        Compatibel met de Miro `/boards/{id}/items`-shape: response heeft
        `data: [...]` en optioneel `cursor: "..."` voor de volgende pagina.
        """
        base_params = dict(params or {})
        base_params.setdefault("limit", page_size)
        cursor: str | None = None
        while True:
            # Nieuwe dict per call zodat eerder vastgelegde mock.call_args
            # niet door mutatie wijzigt — en omdat het netjes is.
            call_params = dict(base_params)
            if cursor:
                call_params["cursor"] = cursor
            data = self.get(endpoint, params=call_params)
            yield from data.get("data", [])
            cursor = data.get("cursor")
            if not cursor:
                break
