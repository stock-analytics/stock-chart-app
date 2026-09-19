from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from typing import Any, Literal
import math

@dataclass(frozen=True)
class Bar:
    session_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int | None = None
    adj_close: float | None = None
    session_close_at: datetime | None = None
    available_at: datetime | None = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    provider_timestamp: datetime | None = None
    is_final: bool = True

    def validate(self) -> None:
        prices=(self.open,self.high,self.low,self.close)
        if not all(math.isfinite(v) and v>0 for v in prices): raise ValueError("invalid_price")
        if not self.low <= min(self.open,self.close) <= max(self.open,self.close) <= self.high: raise ValueError("invalid_ohlc")
        if self.volume is not None and self.volume < 0: raise ValueError("invalid_volume")

@dataclass(frozen=True)
class Pivot:
    index: int
    kind: Literal['high','low']
    price: float
    pivot_at: date
    known_at: date

@dataclass
class ProviderResult:
    bars: list[Bar]
    actions: list[dict[str,Any]]
    provider: str
    fetched_at: datetime
    provider_timestamp: datetime | None = None
    warnings: list[str] = field(default_factory=list)
    capabilities: dict[str,Any] = field(default_factory=dict)
