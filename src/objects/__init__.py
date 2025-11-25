from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from hashlib import sha224
from threading import Thread, Lock
import time
from typing_extensions import Self
from random import randint
from abc import ABC
from typing import Dict, List, Tuple
from collections import deque

PATHFINDING_EXECUTOR = ThreadPoolExecutor(max_workers=8)
Abstract_Grid_Type = Tuple[int, int]


class AbstractObject(ABC):
    _path_cache: Dict[Tuple[int, int, int, int], List[Tuple[int, int]]] = {}
    _path_cache_lock = Lock()

    def __new__(cls, *args, **kwargs) -> Self:
        obj = super().__new__(cls)
        obj.id = sha224(f"{time.time()}{randint(1, 30000)}".encode()).hexdigest()
        return obj

    def __init__(self, *, GRID_SIZE: Abstract_Grid_Type, CELL_SIZE: int) -> None:

        self.pos: tuple[int, int]
        self.size: tuple[int, int] = (CELL_SIZE, CELL_SIZE)
        self.color: tuple[int, int, int]
        self.id: str
        self.visible: bool = True
        self.moveable: bool = True
        self.collidable: bool = True
        self.cell_size: int = CELL_SIZE
        self.path: List[Tuple[int, int]] = []
        self.grid_x, self.grid_y = 0, 0
        self.velocity: tuple[float, float] = (0.0, 0.0)
        self.GRID_WIDTH, self.GRID_HEIGHT = GRID_SIZE
        self.lock = Lock()

    @classmethod
    def clear_path_cache(cls) -> None:
        """Сбросить кеш путей (например, при регенерации лабиринта)."""
        with cls._path_cache_lock:
            cls._path_cache.clear()

    def update_pixel_pos(self, cell_size: int) -> None:
        """Обновляем пиксельную позицию (центр клетки) на основании grid_x/grid_y."""

        x = self.grid_x * cell_size + cell_size // 2
        y = self.grid_y * cell_size + cell_size // 2
        self.pos = (x, y)

    def move_path(self, cell_size: int) -> None:
        """Перемещаем объект в указанные координаты сетки."""

        def _move_path(self: "AbstractObject", cell_size: int) -> None:
            while self.path and self.moveable:
                try:
                    with self.lock:
                        self.grid_x, self.grid_y = self.path.pop(0)
                        self.update_pixel_pos(cell_size)
                except IndexError:
                    break
                time.sleep(0.02)

        Thread(target=_move_path, args=(self, cell_size), daemon=True).start()

    def build_path_to(
        self,
        grid_x: int,
        grid_y: int,
        *objects,  # например, rects
    ) -> None:
        """Асинхронно построить путь от текущих координат до (grid_x, grid_y)."""

        def _build_path_to(obj: "AbstractObject", gx: int, gy: int, objects_tuple):
            start = (obj.grid_x, obj.grid_y)
            goal = (gx, gy)

            # --- 1. Проверка кеша пути ---
            cache_key = (start[0], start[1], goal[0], goal[1])
            with obj._path_cache_lock:
                cached = obj._path_cache.get(cache_key)
            if cached is not None:
                obj.path = cached
                return

            max_x, max_y = obj.GRID_WIDTH, obj.GRID_HEIGHT

            # --- 2. Кешируем коллизии ---
            @lru_cache(maxsize=None)
            def is_blocked(x: int, y: int) -> bool:
                # objects_tuple — тот самый *objects, превращённый в tuple
                return any(group.check_collision(x, y) for group in objects_tuple)

            # если старт или цель заняты — смысла искать путь нет
            if is_blocked(*start) or is_blocked(*goal):
                obj.path = []
                return

            # --- 3. Кешируем соседей (возвращаем НЕ генератор, а tuple) ---
            @lru_cache(maxsize=None)
            def get_neighbors(x: int, y: int) -> Tuple[Tuple[int, int], ...]:
                neighbors: List[Tuple[int, int]] = []
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy

                    if not (0 <= nx < max_x and 0 <= ny < max_y):
                        continue

                    if is_blocked(nx, ny):
                        continue

                    neighbors.append((nx, ny))

                # lru_cache нормально кеширует именно неизменяемые структуры
                return tuple(neighbors)

            # --- 4. BFS ---
            queue = deque([start])
            came_from = {start: None}
            found = False

            while queue:
                current = queue.popleft()

                if current == goal:
                    found = True
                    break

                for neighbor in get_neighbors(*current):
                    if neighbor not in came_from:
                        came_from[neighbor] = current  # pyright: ignore[reportArgumentType]
                        queue.append(neighbor)

            if not found:
                obj.path = []
                return

            # --- 5. Восстановление пути ---
            path: List[Tuple[int, int]] = []
            cur = goal
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]

            path.reverse()
            obj.path = path

            # --- 6. Сохраняем в кеш ---
            with obj._path_cache_lock:
                obj._path_cache[cache_key] = path

        # Превращаем *objects в tuple, чтобы его можно было захватывать в замыкание
        objects_tuple = tuple(objects)
        PATHFINDING_EXECUTOR.submit(_build_path_to, self, grid_x, grid_y, objects_tuple)

    def update_position(
        self,
        cell_size: int,
        dt: float = 1.0,  # pylint: disable=unused-argument
    ) -> None:
        """
        Переопределяем метод из AbstractObject.
        Здесь движение дискретное, поэтому dt можно игнорировать,
        но оставляем сигнатуру ради совместимости.
        """
        self.update_pixel_pos(cell_size)


class AbstractObjectList(List[AbstractObject]):
    def check_collision(self, grid_x: int, grid_y: int) -> bool:
        """Проверяет, есть ли объект в указанных координатах сетки."""
        for rect in self:
            if rect.grid_x == grid_x and rect.grid_y == grid_y:
                return True
        return False


__all__ = ["AbstractObject"]
