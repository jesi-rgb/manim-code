from manimlib import *
from numpy import ndarray


class MoveNextTo(MoveToTarget):
    def __init__(
        self, mobject1: Mobject, mobject2: Mobject, direction: ndarray, buff=1, **kwargs
    ):
        mobject1.generate_target()
        mobject1.target.next_to(mobject2, direction, buff=buff)
        super().__init__(mobject1, **kwargs)


class Test(Scene):
    def construct(self):
        cube = Cube()
        cube_target = Cube().shift(LEFT * 2)
        # cube.generate_target()
        # cube.target.next_to(cube_target, LEFT, buff=0)
        # self.play(MoveToTarget(cube))

        self.play(
            MoveNextTo(cube, cube_target, LEFT, 4, kwargs={"coor_mask": [1, 0, 0]})
        )
