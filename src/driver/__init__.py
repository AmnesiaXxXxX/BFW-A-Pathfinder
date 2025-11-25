from collections import deque
from typing import Callable, Any
from threading import Thread, Lock
import time


class Driver:
    def __init__(self):
        self.query: deque = deque()
        self.running = True
        self.lock = Lock()
        self.refresh_rate = 2400

    def create_task(self, task: Callable) -> None:
        with self.lock:
            self.query.append(task)

    def _work(self, *args: Any, **kwargs: Any) -> None:
        while self.running:
            task = None
            with self.lock:
                if self.query:
                    task = self.query.popleft()

            if task is not None:
                Thread(target=task, args=args, kwargs=kwargs, daemon=True).start()
            else:
                # когда задач нет — тоже спим
                time.sleep(1 / self.refresh_rate)

    def start(self) -> None:
        Thread(target=self._work, daemon=True).start()

    def stop(self) -> None:
        self.running = False
__all__ = ["Driver"]