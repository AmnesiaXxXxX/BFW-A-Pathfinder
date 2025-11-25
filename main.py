from threading import Thread
import pygame
import sys
from src.driver import Driver
from src.objects.player import Player
from src.objects.cube import Rect, Rects
from random import randint

pygame.init()  # pylint: disable=no-member

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 700
CELL_SIZE = 10
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("BFW/A* Поиск пути в лабиринте")

rects: Rects = Rects([])


def gen_cubes():
    rects.clear()

    def _gen_cubes():

        # Сетку будем хранить как True = стена, False = проход
        is_wall = [[True for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

        # Стартовая ячейка для генерации лабиринта (ОДНА из проходимых)
        start_x, start_y = 1, 1
        is_wall[start_x][start_y] = False

        stack = [(start_x, start_y)]
        # Направления: шагаем сразу на 2 клетки, чтобы между ними была "стена"
        dirs = ((2, 0), (-2, 0), (0, 2), (0, -2))

        # --- генерация лабиринта (DFS с возвратом) ---
        while stack:
            _x, _y = stack[-1]

            neighbors = []
            for dx, dy in dirs:
                nx, ny = _x + dx, _y + dy
                # работаем только во внутренней области
                if 1 <= nx < GRID_WIDTH - 1 and 1 <= ny < GRID_HEIGHT - 1:
                    if is_wall[nx][ny]:
                        neighbors.append((nx, ny))

            if neighbors:
                nx, ny = neighbors[randint(0, len(neighbors) - 1)]

                # выбиваем стену между (x, y) и (nx, ny)
                mx = (_x + nx) // 2
                my = (_y + ny) // 2
                is_wall[mx][my] = False
                is_wall[nx][ny] = False

                stack.append((nx, ny))
            else:
                stack.pop()

        # --- делаем вход и выход (по желанию) ---
        # вход сверху слева
        is_wall[1][0] = False
        # выход снизу справа
        is_wall[GRID_WIDTH - 2][GRID_HEIGHT - 1] = False

        # --- из матрицы is_wall создаём препятствия (Rect) ---
        for _x in range(GRID_WIDTH):
            for _y in range(GRID_HEIGHT):

                # создаём прямоугольник только там, где стена
                if not is_wall[_x][_y]:
                    continue

                _rect = Rect((GRID_WIDTH, GRID_HEIGHT), CELL_SIZE)
                _rect.grid_x = _x
                _rect.grid_y = _y
                _rect.update_pixel_pos(CELL_SIZE)
                rects.append(_rect)

    thr = Thread(target=_gen_cubes, daemon=True)
    thr.start()
    thr.join()


driver = Driver()
driver.start()

player = Player((GRID_WIDTH, GRID_HEIGHT), CELL_SIZE)
running = True


def draw_grid(surface, cell_size: int) -> None:
    width, height = surface.get_size()

    # вертикальные линии
    for _x in range(0, width, cell_size):
        pygame.draw.line(surface, (200, 200, 200), (_x, 0), (_x, height))

    # горизонтальные линии
    for _y in range(0, height, cell_size):
        pygame.draw.line(surface, (200, 200, 200), (0, _y), (width, _y))


clock = pygame.time.Clock()  # чтобы ограничить FPS
gen_cubes()
while running:
    screen.fill((255, 255, 255))
    dt_ms = clock.tick(60)  # миллисекунды с прошлого кадра
    dt = dt_ms / 1000.0
    for event in pygame.event.get():
        match event.type:
            case pygame.KEYDOWN:  # pylint: disable=no-member
                if event.key == 32:
                    print(event.key)
                    player.grid_x, player.grid_y = (1, 0)
                    player.path.clear()
                    gen_cubes()
            case pygame.MOUSEBUTTONDOWN:  # pylint: disable=no-member
                mouse_x, mouse_y = event.pos
                grid_x = mouse_x // CELL_SIZE
                grid_y = mouse_y // CELL_SIZE
                player.build_path_to(grid_x, grid_y, rects)

        if event.type == pygame.QUIT:  # pylint: disable=no-member
            running = False
    draw_grid(screen, CELL_SIZE)
    Thread(target=player.update_position, args=(CELL_SIZE, dt)).start()
    pygame.draw.circle(screen, player.color, player.pos, player.size[0])
    if player.path is not None and len(player.path) > 0:
        Thread(target=player.move_path, args=(CELL_SIZE,)).start()
        for cell in player.path:
            cell_x = cell[0] * CELL_SIZE + CELL_SIZE // 2
            cell_y = cell[1] * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.rect(
                screen,
                (0, 0, 255),
                (
                    cell_x - CELL_SIZE / 4,
                    cell_y - CELL_SIZE / 4,
                    CELL_SIZE / 2,
                    CELL_SIZE / 2,
                ),
                2,
            )

    for rect in rects:
        x, y = rect.pos
        pygame.draw.rect(
            screen,
            rect.color,
            (
                x - (CELL_SIZE / 2),
                y - (CELL_SIZE / 2),
                CELL_SIZE,
                CELL_SIZE,
            ),
        )
    pygame.display.flip()
driver.stop()
pygame.quit()  # pylint: disable=no-member
sys.exit()
