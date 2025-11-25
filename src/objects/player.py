from . import Abstract_Grid_Type, AbstractObject


class Player(AbstractObject):
    def __init__(self, GRID_SIZE: Abstract_Grid_Type, CELL_SIZE: int):
        super().__init__(GRID_SIZE=GRID_SIZE, CELL_SIZE=CELL_SIZE)
        self.pos = (100, 100)
        self.size = (int(CELL_SIZE/2), int(CELL_SIZE/2))
        self.color = (0, 255, 0)
        self.visible = True
        self.moveable = True
        self.collidable = True
        self.grid_x, self.grid_y = 1, 0

    def move(
        self, dx: int, dy: int, grid_width: int, grid_height: int, cell_size: int
    ) -> None:
        """
        Двигаем игрока на dx, dy клеток с проверкой границ сетки.
        dx, dy = -1, 0 или 1.
        """
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if 0 <= new_x < grid_width and 0 <= new_y < grid_height:
            self.grid_x = new_x
            self.grid_y = new_y
            self.update_pixel_pos(cell_size)
