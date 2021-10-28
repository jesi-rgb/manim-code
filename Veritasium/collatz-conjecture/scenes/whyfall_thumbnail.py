"""

    Written by Jesús Rascón for Veritasium (July 2021)
    - This file covers the Collatz / Brownian motion animations

    Please do not share this code unless given explicit permission by both
                    Jonny Hyman and Derek Muller

"""

from manimlib import *


# CUSTOM CONFIG
# font: "CMU Sans Serif"
#   background_color: "#010326"

COLLATZ_RED = "#F23545"
COLLATZ_NAVY = "#010326"
COLLATZ_BLUE = "#1B21A6"
COLLATZ_SKY = "#2745F2"
COLLATZ_AQUA = "#6AD9D9"

COLLATZ_GREY0 = "#d8d5cd"
COLLATZ_GREY1 = "#c8c5bd"
COLLATZ_GREY2 = "#c9cbc7"
COLLATZ_GREY3 = "#b8bdbe"
COLLATZ_GREY4 = "#ccced3"

COLLATZ_GREYS = [
    COLLATZ_GREY0,
    COLLATZ_GREY1,
    COLLATZ_GREY2,
    COLLATZ_GREY3,
    COLLATZ_GREY4,
]

METAL_COLOR = Color(hsl=(0.55, 0.075, 3 / 20))

stroke_width = 2
scale = 0.6


class Node(VGroup):
    def __init__(self, text, iteration=None, color=METAL_COLOR):

        self.text = Text(str(text))

        self.circ = Circle(radius=0.5)
        self.circ.set_fill(color, opacity=0.0)

        self.cval = int(text)
        if iteration:
            self.iteration = iteration

        if self.cval % 2 == 0:
            self.circ.set_stroke(COLLATZ_AQUA, width=stroke_width)
            self.text.set_color(COLLATZ_AQUA)
        else:
            self.text.set_color(COLLATZ_RED)
            self.circ.set_stroke(COLLATZ_RED, width=stroke_width)

        super().__init__(self.circ, self.text)
        self.arrange(ORIGIN, buff=0)

    def set_state(self, state):
        if state:
            self.set_stroke(YELLOW_A, width=5)
        else:
            self.set_stroke(BLACK, width=0)


class WhyFall(Scene):
    def construct(self):

        def calculate_pattern(node_list, scale=0.6):
            nodes = VGroup()
            for i in range(len(node_list.submobjects)):
                last_node = node_list[i]
                curr_vg = VGroup()

                while last_node.cval % 2 == 0:

                    n = (
                        Node(last_node.cval // 2)
                        .scale(scale)
                        .next_to(last_node, DOWN, buff=0.3)
                    )

                    l = Line(last_node, n, color=COLLATZ_AQUA)

                    curr_vg.add(l)
                    curr_vg.add(n)
                    last_node = n

                nodes.add(curr_vg)

            return nodes

        every_node = VGroup()

        odd_nodes = VGroup()
        odd_numbers = []

        initial_pos = LEFT * 7 + UP * 3.5
        max_number = 257
        powers = [2 ** n for n in range(2, int(math.log2(max_number - 1)))]
        print(powers)

        for i in range(1, max_number, 2):
            odd_numbers.append(i)
            n = Node(i).scale(scale).move_to(initial_pos + RIGHT * (i / 2))
            odd_nodes.add(n)

        self.wait(1)

        self.play(Write(odd_nodes), run_time=2)
        every_node.add(odd_nodes)

        first_iter_nodes = VGroup()
        first_iter_n = []

        for i in range(1, max_number, 2):
            first_iter_n.append(3 * i + 1)
            n = (
                Node(3 * i + 1)
                .scale(scale)
                .move_to(initial_pos + RIGHT * (i / 2) + DOWN)
            )
            first_iter_nodes.add(n)

        arrows = VGroup()
        for i in range(len(odd_nodes.submobjects)):
            l = Line(odd_nodes[i], first_iter_nodes[i], color=COLLATZ_AQUA)
            arrows.add(l)

        self.play(Write(first_iter_nodes), Write(arrows), run_time=4)
        every_node.add(first_iter_nodes, arrows)

        nodes_n = calculate_pattern(first_iter_nodes)
        div_2 = nodes_n[1::2]
        div_4 = nodes_n[::4]
        div_8 = nodes_n[6::8]
        div_16 = nodes_n[2::16]
        div_64 = nodes_n[10::64]

        self.wait(1)

        self.play(LaggedStartMap(Write, div_2), run_time=2)
        self.wait(1)
        # self.play(Transform(div_2, div_2.set_opacity(0.3)))

        self.play(LaggedStartMap(Write, div_4), run_time=2)
        self.wait(1)
        # self.play(Transform(div_4, div_4.set_opacity(0.3)))

        self.play(LaggedStartMap(Write, div_8), run_time=2)
        # self.play(Transform(div_8, div_8.set_opacity(0.3)))

        self.play(
            LaggedStartMap(Write, div_16.add(div_64)),
            run_time=2,
        )

        self.add(nodes_n)

        every_node.add(nodes_n)

        # (3/2)^(1/2)*(3/4)^(1/4)*(3/8)^(1/8)*(3/16)^(1/16)...= 3/4 < 1
        equation = (
            Tex(
                "\\frac{3}{2}^\\frac{1}{2} \ \\frac{3}{4}^\\frac{1}{4} \ \\frac{3}{8}^\\frac{1}{8} \ \\frac{3}{16}^\\frac{1}{16} \\dots = \\frac{3}{4}",
                " < 1",
            )
            .set_color(WHITE)
            .move_to(ORIGIN + DOWN * 2)
        )

        # zoom out
        self.play(
            Write(equation),
            ReplacementTransform(
                every_node,
                every_node.copy().scale(0.1).move_to(ORIGIN + 3.3 * UP),
            ),
            run_time=3,
        )

        # self.play(Write(equation[1]))
