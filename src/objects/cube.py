from . import Abstract_Grid_Type, AbstractObject, AbstractObjectList


class Rect(AbstractObject):
    def __init__(self, GRID_SIZE: Abstract_Grid_Type, CELL_SIZE: int):
        super().__init__(GRID_SIZE=GRID_SIZE, CELL_SIZE=CELL_SIZE)
        self.size = (int(CELL_SIZE/4), int(CELL_SIZE/4))
        self.color = (255, 255, 0)
        self.visible = True
        self.moveable = True
        self.collidable = True


class Rects(AbstractObjectList):
    pass
