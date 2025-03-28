import asyncio
import time

from services.room.strategies import GameLoopStrategy


class GameLoop:
    def __init__(self, strategy: GameLoopStrategy):
        self._strategy = strategy
        self._task: asyncio.Task = asyncio.create_task(self._loop())
        self._current_turn: int = 0
        self._should_stop: bool = False
        self._start_loop: asyncio.Event = asyncio.Event()

    @property
    def current_turn(self) -> int:
        return self._current_turn

    async def start(self) -> None:
        self._start_loop.set()

    async def stop(self) -> None:
        self._should_stop = True
        if self._task and not self._task.done():
            self._task.cancel()

    async def wait(self) -> None:
        if self._task and not self._task.done():
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        await self._start_loop.wait()
        while not self._should_stop and not self._strategy.is_game_done():
            self._current_turn += 1
            start = time.perf_counter()
            await self._strategy.init_turn(self._current_turn)
            self._strategy.make_turn()
            await self._strategy.finish_turn()
            elapsed = time.perf_counter() - start
            await asyncio.sleep(max(0.7 - elapsed, 0))

        await self._strategy.finish_game()
