import asyncio
import string
from asyncio import Lock
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, HttpUrl


class UrlRecord(BaseModel):
    original_url: str
    short_code: str
    created: datetime
    expires: Optional[datetime] = None

class UrlRequest(BaseModel):
    url: HttpUrl
    expires: Optional[int] = None

class UrlResponse(BaseModel):
    code: str
    short_url: str
    expires: Optional[datetime]

class UrlShortenerService:
    def __init__(self):
        self.store: Dict[str, UrlRecord] = {}
        self._lock: Lock = asyncio.Lock()
        self._counter: int = 9999
        self._cleanup_task: Optional[asyncio.Task] = None
        self.base_url: str = "http://n.to:5000"

    async def create_code(self) -> str:
        async with self._lock:
            self._counter += 1
            return self.base62_encode(self._counter)

    async def create_short_url(self):
        return f'{self.base_url}/{self.create_code()}'

    def get_existing_code(self, url: str) -> str:
        return next((key for key, value in self.store.items() if self.match(value, url)), None)

    def expired(self, record: UrlRecord):
        return record.expires >= self.now()

    def get_short_url(self, code: str):
        return f'{self.base_url}/{code}'

    def get_existing_short_url(self, url: str):
        code: str = self.get_existing_code(url)

        if code:
            return f'{self.base_url}/{code}'
        return None

    def get_long_url(self, code: str):
        return self.store[code].original_url

    def match(self, record: UrlRecord, url:str):
        return url == record.original_url and not self.expired(record)

    @staticmethod
    def now():
        return datetime.now(timezone.utc)

    @staticmethod
    def base62_encode(num: int):
        base62chars: str = string.digits + string.ascii_letters
        if num == 0:
            return base62chars[0]

        result = ''
        while num > 0:
            num, rem = divmod(num, 62)
            print(f"num = {num} rem = {rem} encoded = {base62chars[rem]}")
            result = base62chars[rem] + result
        return result
