from math import fabs
from manimlib import *
from numpy import cbrt, ndarray, sqrt


class VCube(VGroup):
    CONFIG = {
        "color": BLUE,
        "opacity": 1,
        "side_length": 2,
    }

    def __init__(
        self,
        side_length=2,
        fill_opacity=1,
        fill_color=BLUE,
        stroke_color=BLACK,
        stroke_width=3,
        **kwargs
    ):
        self.side_length = side_length
        super().__init__(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            **kwargs,
        )

    def init_points(self):
        for vect in IN, OUT, LEFT, RIGHT, UP, DOWN:
            face = (
                Square(
                    side_length=self.side_length,
                    # shade_in_3d=True,
                )
                .set_stroke(self.stroke_color, width=self.stroke_width)
                .set_opacity(self.fill_opacity)
                .set_fill(self.fill_color)
            )
            # face.flip()
            face.shift(self.side_length * OUT / 2.0)
            face.apply_matrix(z_to_vector(vect))

            self.add(face)


class VPrism(VCube):
    CONFIG = {"dimensions": [3, 2, 1]}

    def init_points(self):
        VCube.init_points(self)
        for dim, value in enumerate(self.dimensions):
            self.rescale_to_fit(value, dim, stretch=True)


class VCubeTest(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=-45 * DEGREES,
            phi=70 * DEGREES,
        )

        general_opacity = 1
        x = 2
        y = cbrt(-10 + 6 * sqrt(3))
        z = x + y
        x_cube = VCube(side_length=x).set_color(PURPLE).shift(ORIGIN).set_stroke(BLACK)
        y_cube = (
            VCube(side_length=y)
            .set_color(YELLOW_D)
            .next_to(x_cube, DOWN + OUT + LEFT, buff=0)
        ).set_opacity(general_opacity)

        z_cube_og = (
            VCube(side_length=z)
            .set_color(RED_C)
            .set_stroke(BLACK)
            .next_to(x_cube, buff=0, aligned_edge=IN + UP + LEFT, coor_mask=[0, 1, 1])
            .shift(LEFT * y / 2)
            .shift(IN * 0.02)  # to avoid glitches
        )

        # x, y, y prisms
        ####################################################
        x_y_y = (
            VPrism(dimensions=[x, y, y])
            .set_color(GREEN)
            .set_stroke(BLACK)
            .next_to(x_cube, OUT + DOWN, buff=0)
        ).set_opacity(general_opacity)

        x_y_y_1 = (
            (VPrism(dimensions=[x, y, y]).set_color(GREEN).set_stroke(BLACK))
            .rotate(PI / 2, Z_AXIS)
            .next_to(x_cube, OUT + LEFT, buff=0)
        ).set_opacity(general_opacity)

        x_y_y_2 = (
            VPrism(dimensions=[y, y, x])
            .set_color(GREEN)
            .set_stroke(BLACK)
            .rotate(0)
            .next_to(x_cube, LEFT + DOWN, buff=0)
        ).set_opacity(general_opacity)

        # x, x, y prisms
        ####################################################
        x_x_y = (
            VPrism(dimensions=[x, x, y])
            .set_color(BLUE_D)
            .next_to(x_cube, OUT, buff=0)
            .set_opacity(general_opacity)
        )
        x_x_y_1 = (
            (
                VPrism(dimensions=[x, x, y])
                .set_color(BLUE_D)
                .next_to(x_cube, LEFT, buff=0)
                .set_stroke(BLACK)
            ).set_opacity(general_opacity)
            # .rotate(-PI / 2, Y_AXIS)
        )

        x_x_y_2 = (
            VPrism(dimensions=[x, x, y])
            .set_color(BLUE_D)
            .rotate(PI / 2, X_AXIS)
            .next_to(x_cube, DOWN, buff=0)
        ).set_opacity(general_opacity)

        # self.play(
        #     # FadeIn(x_cube),
        #     # FadeIn(y_cube),
        #     FadeIn(x_x_y),
        #     FadeIn(x_x_y_1),
        #     FadeIn(x_x_y_2),
        # )

        prism = VPrism(dimensions=[2, 3, 4])
        # self.play(FadeIn(x_x_y_1))
        x_x_y_1 = x_x_y_1.rotate(PI / 2, Y_AXIS)

        self.play(x_x_y_1.animate.rotate(PI / 2, Y_AXIS))


class SquareTest(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=-45 * DEGREES,
            phi=70 * DEGREES,
        )
        sq1 = Square().set_stroke(BLACK, width=3).set_fill(BLUE).set_opacity(1)
        sq2 = (
            Square()
            .set_stroke(BLACK, width=3)
            .set_fill(RED)
            .set_opacity(1)
            .shift(LEFT * 0.5)
        )

        self.add(sq2, sq1)
        sq1.apply_matrix(z_to_vector(OUT))

        self.play(Rotate(sq2, PI / 2, X_AXIS), Rotate(sq1, -PI / 2, X_AXIS))
