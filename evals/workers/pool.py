from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Sequence
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


class BoundedRunner:
    """Run a coroutine factory over items concurrently, bounded by a semaphore.

    Results are returned in the same order as ``items`` (not completion order)
    so callers can correlate outputs to inputs without extra bookkeeping.
    """

    def __init__(self, max_concurrency: int) -> None:
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")
        self._max = max_concurrency

    async def run(
        self,
        coro_factory: Callable[[T], Awaitable[R]],
        items: Sequence[T],
    ) -> list[R]:
        semaphore = asyncio.Semaphore(self._max)

        async def _guarded(item: T) -> R:
            async with semaphore:
                return await coro_factory(item)

        return await asyncio.gather(*(_guarded(item) for item in items))
