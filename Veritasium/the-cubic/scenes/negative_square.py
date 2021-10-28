from math import sqrt
from manimlib import *
from numpy import right_shift


class DashedRectangle(VGroup):
    CONFIG = {"num_dashes": 30, "positive_space_ratio": 0.5, "width": 5, "height": 4}

    def __init__(self, *args, **kwargs):
        VGroup.__init__(self, *args, **kwargs)
        h1 = [ORIGIN, UP * self.height]
        w1 = [UP * self.height, UP * self.height + RIGHT * self.width]
        h2 = [UP * self.height + RIGHT * self.width, RIGHT * self.width]
        w2 = [RIGHT * self.width, ORIGIN]
        alpha = self.width / self.height
        divs = self.num_dashes

        n_h = int(divs / (2 * (alpha + 1)))
        n_w = int(alpha * n_h)
        dashedrectangle = VGroup()
        for n, l in zip([n_w, n_h], [[w1, w2], [h1, h2]]):
            for side in l:
                line = VMobject()
                line.set_points_as_corners(side)
                dashedrectangle.add(
                    DashedVMobject(
                        line,
                        num_dashes=n,
                        positive_space_ratio=self.positive_space_ratio,
                    )
                )
        self.add(
            dashedrectangle[0],
            dashedrectangle[3],
            dashedrectangle[1],
            dashedrectangle[2],
        )


class NegativeSquare(Scene):
    def construct(self):
        #  x^2+10x=39

        self.play(self.camera.frame.animate.shift(OUT * 4))

        x = 3
        x_term = 10
        equals = 39

        main_sq = Square(x).set_color(BLACK)

        rect_half_1 = (
            Rectangle(x_term / 2, x)
            .set_color(BLUE_E)
            .shift(DOWN * 3 + LEFT * x_term / 4)
            .next_to(main_sq, LEFT, buff=0)
        )
        rect_half_2 = (
            Rectangle(x_term / 2, x)
            .set_color(BLUE_E)
            .shift(DOWN * 3 - LEFT * x_term / 4)
            .rotate(PI / 2)
            .next_to(main_sq, DOWN, buff=0)
        )
        square_gap = (
            Square(x_term / 2).set_color(RED_C).next_to(rect_half_1, DOWN, buff=0)
        )

        negative_side = abs(
            -int(math.sqrt(equals + (x_term // 2) ** 2)) - (x_term // 2)
        )
        negative_sq = (
            DashedRectangle(width=negative_side, height=negative_side)
            .set_color(BLACK)
            .next_to(main_sq, UR, buff=0)
        )

        vg_squares = (
            VGroup(main_sq, rect_half_1, rect_half_2, square_gap, negative_sq)
            .shift(RIGHT * 5)
            .scale(0.7)
        )

        self.play(
            Write(main_sq), Write(rect_half_1), Write(rect_half_2), Write(square_gap)
        )

        eq_step_1 = (
            Tex(
                f"(x + ",
                f"{x_term//2}",
                f") ^ 2 =",
                f"{equals}",
                f" + {(x_term//2) ** 2}",
                isolate=[f"x + {x_term//2}", f"{(x_term//2) ** 2}", f"{equals}", "^2"],
            )
            .shift(RIGHT * 6 + UP * 3)
            .set_color(BLACK)
            .scale(1.5)
        )
        eq_step_1.set_color_by_tex(f"{(x_term//2) ** 2}", RED_C)
        eq_step_1[1].set_color(BLUE_E)

        eq_step_2 = (
            Tex(
                f"(x + ",
                f"{x_term//2}",
                f") ^ 2",
                f" = ",
                f"{equals + (x_term // 2) ** 2}",
                isolate=[f"{x_term // 2}"],
            )
            .next_to(eq_step_1, DOWN, buff=1, aligned_edge=RIGHT)
            .set_color(BLACK)
            .scale(1.5)
        )
        eq_step_2[1].set_color(BLUE_E)

        eq_step_3 = (
            Tex(
                f"x + {x_term // 2} = \pm {int(math.sqrt(equals + (x_term // 2) ** 2))}",
                isolate=[f"{x_term // 2}"],
            )
            .next_to(eq_step_2, DOWN, buff=1, aligned_edge=LEFT)
            .set_color(BLACK)
            .scale(1.5)
        )
        eq_step_3.set_color_by_tex(f"{x_term//2}", BLUE_E)

        eq_step_4 = (
            Tex(f"x = {int(math.sqrt(equals + (x_term // 2) ** 2)) - (x_term // 2)}")
            .next_to(eq_step_3, DOWN, buff=1, aligned_edge=LEFT)
            .set_color(BLACK)
            .scale(1.5)
        )
        eq_step_5 = (
            Tex(f"x_2 = {-int(math.sqrt(equals + (x_term // 2) ** 2)) - (x_term // 2)}")
            .next_to(eq_step_4, DOWN, buff=1, aligned_edge=LEFT)
            .set_color(BLACK)
            .scale(1.5)
        )

        vg_eqs = (
            VGroup(eq_step_1, eq_step_2, eq_step_3, eq_step_4, eq_step_5)
            .arrange_in_grid(n_cols=1, aligned_edge=LEFT)
            .scale(1)
            .shift(UP + LEFT * 5)
        )

        # animations
        self.play(Write(eq_step_1))

        self.wait(1)

        self.play(Write(eq_step_2))

        self.wait(1)

        self.play(Write(eq_step_3))

        self.wait(1)

        self.play(Write(eq_step_4))

        self.wait(2)

        eq_4_target = eq_step_4.copy().next_to(main_sq, UP, buff=0.2)
        self.play(ReplacementTransform(eq_step_4, eq_4_target))

        self.wait(4)

        self.play(Write(eq_step_5))

        self.wait(2)

        self.play(
            self.camera.frame.animate.shift(OUT * 26 + RIGHT * 7 + UP * 3),
            ReplacementTransform(
                eq_step_5, eq_step_5.copy().next_to(negative_sq, DOWN, buff=0.2)
            ),
            GrowFromPoint(negative_sq, negative_sq.get_corner(DL)),
            ShrinkToCenter(eq_4_target),
            main_sq.scale,
            0,
            {"about_point": main_sq.get_corner(UR)},
            run_time=4,
        )

        error_text = (
            Text(
                R"""
Traceback (most recent call last):
File "quadratic_solution.py", line 5, in <module>
    Square(side_length=solution_2)
ValueError: squares cannot have negative sides
        """,
                font="SF Mono",
                font_size=12,
            )
            .set_color("#FF0000")
            .scale(10)
            .shift(RIGHT * 6 + UP * 9)
        )

        anims = []
        for i in range(10):
            if i % 2 == 0:
                self.play(FadeIn(error_text, run_time=1 / 2))
            else:
                self.play(FadeOut(error_text, run_time=1 / 4))

        # self.play(*anims)
