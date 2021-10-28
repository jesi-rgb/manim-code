from manimlib import *
import numpy as np

COLLATZ_RED = "#F23545"
COLLATZ_NAVY = "#010326"
COLLATZ_BLUE = "#1B21A6"
COLLATZ_SKY = "#2745F2"
COLLATZ_AQUA = "#6AD9D9"

METAL_COLOR = Color(hsl=(0.55, 0.075, 3 / 20))

COLLATZ_ODD = COLLATZ_RED
COLLATZ_EVEN = COLLATZ_AQUA


def map_num_range(x, input_start, input_end, output_start, output_end):
    return (x - input_start) / (input_end - input_start) * (
        output_end - output_start
    ) + output_start


class Node(VGroup):
    def __init__(self, text, iteration=None, color=METAL_COLOR):

        self.text = Text(str(text))
        txt_scale = map_num_range(len(str(text)), 1, 8, 0.7, 0.05)
        self.text.scale(txt_scale).set_color("#242424")

        self.circ = Circle(radius=0.5)
        self.circ.set_fill(color, opacity=1.0)

        self.cval = int(text)
        if iteration:
            self.iteration = iteration

        if self.cval % 2 == 0:
            self.circ.set_stroke(COLLATZ_AQUA, width=2)
            self.text.set_color(COLLATZ_AQUA)
        else:
            self.text.set_color(COLLATZ_RED)
            self.circ.set_stroke(COLLATZ_RED, width=2)

        super().__init__(self.circ, self.text)
        self.arrange(ORIGIN, buff=0)


class InfinityExplosion(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 200],
            y_range=[0, 500],
            height=6 * 3 * 1.33 * 2,
            width=12 * 3 * 2,
        )
        ax.add_coordinate_labels(font_size=12)

        # self.play(Write(ax.move_to(ORIGIN)))

        iterations = list(range(200))
        y_coord = [int(np.sin(n) * 10) for n in range(100)]
        y_coord.extend([(10) ** (n // 50) for n in range(100, 200)])

        print(y_coord)

        points_in_ax = VGroup(
            *[Node(y).move_to(ax.c2p(i, y)) for i, y in zip(iterations, y_coord)]
        )

        self.play(LaggedStartMap(Write, points_in_ax))
