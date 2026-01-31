import asyncio

from typing import (
    Callable,
    Awaitable,
)


class StopSignalWaiter:

    def __init__(
        self,
        max_time: int,
        poll_interval: float,
    ):
        self.time_elapsed = 0
        self.max_time = max_time
        self.poll_interval = poll_interval        

    
    async def run(
        self,
        stop_condition: Callable[[], Awaitable[bool]]
    ) -> bool:
        while self.time_elapsed < self.max_time:
            if await stop_condition():                
                return True
            
            await asyncio.sleep(self.poll_interval)
            self.time_elapsed += self.poll_interval

        return False
    

    def reset(self):
        self.time_elapsed = 0