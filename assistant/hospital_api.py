"""Client for the hospital API (api/servidor.py): every route is a GET that answers JSON."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_URL = "http://localhost:8765"


class HospitalApi:
    def __init__(self, base_url: str | None = None, timeout: float = 10.0):
        self.base_url = (base_url or os.environ.get("HOSPITAL_API_URL") or DEFAULT_URL).rstrip("/")
        self.timeout = timeout

    def get(self, route: str, **params: str) -> str:
        """The route's JSON body as text, verbatim, error responses (4xx with the valid options) included."""
        query = urllib.parse.urlencode({key: value for key, value in params.items() if value is not None})
        url = f"{self.base_url}{route}" + (f"?{query}" if query else "")
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            return error.read().decode("utf-8")

    def options(self, route: str) -> list[str]:
        """The valid names of a parameterized route, as the API lists them when the parameter is missing."""
        body: dict[str, Any] = json.loads(self.get(route))
        return list(body.get("opciones", []))
