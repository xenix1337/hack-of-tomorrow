import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException


class HttpClient:
    def __init__(
        self,
        base_url: str = "",
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 60,
    ):
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout

    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> dict:
        full_url = f"{self.base_url}{url}"
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, headers=self.headers
            ) as client:
                response = await client.get(full_url, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"HTTP request error: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=response.status_code, detail=f"HTTP status error: {e}"
            )

    async def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> dict:
        full_url = f"{self.base_url}{url}"
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, headers=self.headers
            ) as client:
                response = await client.post(full_url, data=data, json=json)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"HTTP request error: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=response.status_code, detail=f"HTTP status error: {e}"
            )
