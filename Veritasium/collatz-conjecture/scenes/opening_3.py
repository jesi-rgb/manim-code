"""

    Written by Jonny Hyman, July 2021 (www.jonnyhyman.com) for Veritasium
    Partially edited by Jesús Rascón
    - This file covers the Collatz / Brownian motion animations

    Please do not share this code unless given explicit permission by both
                    Jonny Hyman and Derek Muller

    

"""


import networkx as nx
import numpy as np
from manimlib import *

#from numba import njit
from matplotlib import cm

from inspect import getsource

import random

# CUSTOM CONFIG
# font: "CMU Sans Serif"
#   background_color: "#010326"
ps = lambda x: print(getsource(x))

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


def f2(z):
    if (z % 2) != 0:  # odd
        return 3 * z + 1
    else:
        return z // 2


def traj(x0, J):
    x = x0

    t = [x0]
    j = 0

    while True:
        x = f2(x)

        t.append(x)

        if x == 1 or x != x:
            if j < J:
                j += 1
            else:
                return t


# The node class was changed a tiny bit, including the iteration
# in the constructor
class Node(VGroup):
    def __init__(self, text, iteration=None, color=COLLATZ_BLUE):

        self.text = Tex(
            "\\textsf{" + str(text) + "}", font_size=40
        )  # , font="Andale Mono")
        # self.text = Tex(str(text), font_size=40)#, font="Andale Mono")

        self.circ = Circle(radius=0.5)
        self.circ.set_fill(color, opacity=1.0)
        self.circ.set_stroke(WHITE, width=0)  # (4/2) * 3.)

        self.cval = int(text)
        if iteration:
            self.iteration = iteration

        super().__init__(self.circ, self.text)
        self.arrange(ORIGIN, buff=0)

        # self.turn_off = self.animate.set_stroke(BLACK, width=0.0)
        # self.turn_on = self.animate.set_stroke(YELLOW_A, width=5)

    def set_state(self, state):
        if state:
            self.set_stroke(YELLOW_A, width=5)
        else:
            self.set_stroke(BLACK, width=0)


# class Coraline(Polygon):
#     def __init__(self,  *verts, color=BLUE_C):
#         verts = list(verts)
#         # verts += reversed(verts)
#
#         super().__init__(* verts,
#                                 stroke_width=13.0,
#                                 stroke_color = rgba_to_color(color),
#                                 joint_type='round')
#
#     def init_points(self):
#         verts = self.vertices
#         self.set_points_as_corners([*verts])
#
# def ends(self):
#
#     ends_group = VGroup()
#
#     c0 = Circle(radius = self.CONFIG['stroke_width']/2)
#     c0.set_fill(self.CONFIG['stroke_color'], opacity=1.0)
#     c0.set_stroke(self.CONFIG['stroke_color'], width=0.0, opacity=0.0)
#     c0.move_to(self.vertices[0])
#
#     c1 = Circle(radius = self.CONFIG['stroke_width']/2)
#     c1.set_fill(self.CONFIG['stroke_color'], opacity=1.0)
#     c1.set_stroke(self.CONFIG['stroke_color'], width=0.0, opacity=0.0)
#     c1.move_to(self.vertices[-1])
#
#     ends_group.add(c0,c1)
#
#     return ends_group


class _3_Opening_3(Scene):
    def construct(self):

        # ax = Axes(x_range=[0, 25], y_range=[0, 50*2.5], height=6*3*1.33, width=12*3*2)

        ax = Axes(
            x_range=[0, 25],
            y_range=[0, 50 * 2.5 * 2],
            height=6 * 3 * 1.33 * 2,
            width=12 * 3 * 2,
        )
        ax.add_coordinate_labels(
            font_size=12,
        )

        c = 7
        J = 0  # num of loops

        collz = []
        verts = []

        NODES = VGroup()
        LINES = VGroup()

        # these groups serve as a reference for all the nodes and lines we g
        nodes_ref = VGroup()
        arrows_ref = VGroup()

        i = 1
        j = 0
        for v in traj(7, J):

            collz += [c]

            v = ax.c2p(i, c)
            verts.append(v)

            n = Node(c, iteration=i, color=METAL_COLOR)
            n.move_to(v)

            NODES.add(n)

            i += 1

            if c == 1:
                if j < J:
                    j += 1
                else:
                    break

            c = f2(c)

        for vi, v in enumerate(verts):

            if vi == 0:
                continue

            l = Arrow(verts[vi - 1], verts[vi], buff=0.5)  # , path_arc=45*DEGREES)

            LINES.add(l)

        nodes_ref.add(NODES)
        arrows_ref.add(LINES)

        # --------------------------------------------
        # Pick a number, any number.

        # self.add_sound("Opening VO")

        cards = VGroup()

        for n in range(1, 10):
            cards.add(Node(n, color=METAL_COLOR))

        cards.arrange(ORIGIN)
        cards.scale(0.5)

        self.camera.frame.move_to(cards)
        self.camera.frame.shift(RIGHT * 0.5)

        cards.shift(LEFT * 2)

        self.add(cards)
        self.play(cards.animate.arrange(RIGHT, center=False))

        self.wait()

        # 7 - good choice
        self.play(
            *[FadeOut(c, UP, rate_func=rush_from) for c in cards if c.cval != 7],
            cards[6].animate.set_stroke(YELLOW_A, width=5),
            run_time=2 * 1.5,
        )

        NODES[0].set_state(True)

        # ... If the number is odd...
        self.play(
            Transform(cards[6], NODES[0], replace_mobject_with_target_in_scene=True),
            self.camera.frame.animate.move_to(NODES[0]),
            run_time=2 * 2 * 1.5,
        )

        self.wait(2.0)

        rstep = lambda i: i < 2
        rfunc = smooth

        # def rtime(i):
        #     if i < 2:
        #         return 2.
        #     elif i < 13:
        #         return 1.5
        #     else:
        #         return 1.

        times = [
            14 - 6 - 1.5,  # 0
            18 - 14 - 1,  # 1
            25 - 18 - 1,  # 2
            28 - 25,  # 3
            5 - 0.65,  # 4
            21 - 19 + 1,  # 5
            25 - 21 + 1,  # 6
            28 - 25 + 2.85,  # 7
            34 - 28 - 0.5,  # 8
            37 - 34 - 0.5 - 1.225,  # 9
            40 - 37 - 0.5 - 0.5,  # 10
            46 - 40 - 1 - 0.5,  # 11
            49 - 46 - 1 - 0.5,  # 12
            50 - 49 - 0.15,  # 13
            52 - 50 - 0.435,  # 14
            56 - 52 - 1.25,  # 15
            60 - 56,
            # 62-60,
            # 63-62,
            # 65-63,
            # 68-65,
            # 69-68,
            # 70-69
        ]

        times = [t + (sum(times) / len(times) - t) * 0.25 for t in times]

        # self.embed()

        def rtime(i):
            # return .5

            if i < (len(times) - 1):
                print(f"... {i} >>> run_time:", times[i])
                return times[i]

            return 4

        # We are going to apply two rules:

        for v in range(0, len(collz)):

            # Each iteration starts with a centered node, illuminated!

            c = collz[v]

            if v >= len(collz) - 1:
                break

            if (c % 2) != 0:  # ------------------------------------ ODD

                print(">>> Odd! ... iteration:", v, "... number:", c)

                tdist = [1.75, 1.45, 0.3275]

                tdist = [t / sum(tdist) for t in tdist]

                # If the number is odd
                # multiply by three and add one.

                RULE = Tex("\\times 3", "+ 1", font_size=75)
                RULE.next_to(NODES[v])

                self.play(
                    NODES[v].animate.set_stroke(COLLATZ_RED, width=5),
                    Write(RULE),
                    run_time=2 * rtime(v) * tdist[0],
                )

                # self.embed()

                NEW = Node(3 * c, iteration=v + 2, color=METAL_COLOR)
                NEW.move_to(ax.c2p(v + 2, 3 * c))

                nodes_ref.add(VGroup(NEW))

                NLN = Arrow(
                    NODES[v].get_center(), NEW.get_center(), buff=0.5
                )  # , path_arc=45*DEGREES)

                arrows_ref.add(VGroup(NLN))

                self.play(
                    Transform(
                        RULE[0],
                        NLN,  # LINES[v],
                        replace_mobject_with_target_in_scene=True,
                    ),
                    self.camera.frame.animate.move_to(NODES[v + 1]),
                    Write(NEW),
                    RULE[1].animate.move_to(NEW.get_center() + RIGHT * 1.15),
                    run_time=2 * rtime(v) * tdist[1],
                )

                TO = 2.0 * (NODES[v + 1].get_center() - NEW.get_center())

                self.play(
                    NODES[v].animate.set_stroke(BLACK, width=0),
                    FadeOut(RULE[1], TO),
                    Transform(NLN, LINES[v], replace_mobject_with_target_in_scene=True),
                    Transform(NEW.circ, NODES[v + 1].circ),
                    # replace_mobject_with_target_in_scene=True),
                    TransformMatchingTex(
                        NEW.text,
                        NODES[v + 1].text,
                        replace_mobject_with_target_in_scene=True,
                    ),
                    # Write(LINES[v]),
                    rate_func=rfunc,
                    run_time=2 * rtime(v) * tdist[2],
                )

                # self.embed()

                if rstep(v):
                    self.wait()

            else:  # ------------------------------------ EVEN

                # If the number is even, divide by two!
                print(">>>Even! ... iteration:", v, "... number:", c)

                RULE = Tex("\\divisionsymbol 2", font_size=75)
                RULE.next_to(NODES[v])

                self.play(
                    Write(RULE),
                    NODES[v].animate.set_stroke(COLLATZ_AQUA, width=5),
                    run_time=2 * rtime(v) / 2,
                )

                self.play(
                    Transform(
                        RULE, LINES[v], replace_mobject_with_target_in_scene=True
                    ),
                    self.camera.frame.animate.move_to(NODES[v + 1]),
                    # Write(LINES[v]),
                    Write(NODES[v + 1]),
                    NODES[v].animate.set_stroke(BLACK, width=0),
                    rate_func=rfunc,
                    run_time=2 * rtime(v) / 2,
                )

                if rstep(v):
                    self.wait()

                # self.embed()

            # self.embed()

        # REITERATE RULES

        self.wait()

        # we're in a loop!
        loop = Arrow(verts[-1] + UP, verts[-3] + UP, buff=0.5, path_arc=90 * DEGREES)
        arrows_ref.add(VGroup(loop))

        RULE = Tex("\\times 3", "+ 1", font_size=75)
        RULE.next_to(NODES[-1])

        self.play(
            NODES[-1].animate.set_stroke(COLLATZ_RED, width=5),
            Write(RULE),
        )

        self.play(
            FadeOut(RULE),
            Write(loop),
            CounterclockwiseTransform(
                NODES[-1].copy(), NODES[-3], replace_mobject_with_target_in_scene=True
            ),
            self.camera.frame.animate.move_to(NODES[-3]),
            NODES[-1].animate.set_stroke(BLACK, width=0),
            NODES[-3].animate.set_stroke(COLLATZ_AQUA, width=5),
        )
        self.play(
            self.camera.frame.animate.move_to(NODES[-2]),
            NODES[-3].animate.set_stroke(BLACK, width=0),
            NODES[-2].animate.set_stroke(COLLATZ_AQUA, width=5),
        )
        self.play(
            self.camera.frame.animate.move_to(NODES[-1]),
            NODES[-2].animate.set_stroke(BLACK, width=0),
            NODES[-1].animate.set_stroke(COLLATZ_RED, width=5),
        )

        # loop!
        self.play(
            CounterclockwiseTransform(
                NODES[-1].copy(), NODES[-3], replace_mobject_with_target_in_scene=True
            ),
            self.camera.frame.animate.move_to(NODES[-3]),
            NODES[-1].animate.set_stroke(BLACK, width=0),
            NODES[-3].animate.set_stroke(COLLATZ_AQUA, width=5),
        )
        self.play(
            self.camera.frame.animate.move_to(NODES[-2]),
            NODES[-3].animate.set_stroke(BLACK, width=0),
            NODES[-2].animate.set_stroke(COLLATZ_AQUA, width=5),
        )
        self.play(
            self.camera.frame.animate.move_to(NODES[-1]),
            NODES[-2].animate.set_stroke(BLACK, width=0),
            NODES[-1].animate.set_stroke(COLLATZ_RED, width=5),
        )

        # self.embed()

        # self.play(self.camera.frame.animate.move_to(OUT*90))
        # self.play(self.camera.frame.animate.shift(UP*2 + OUT*10), Write(ax))

        self.play(
            self.camera.frame.animate.move_to(OUT * 70 + DOWN * 4)
        )  # , FadeOut(loop))
        self.play(Write(ax), NODES[-1].animate.set_stroke(BLACK, width=0))

        # --------------------------------------------

        # Now the conjecture is:
        # Every positive integer,
        # if you apply these rules,
        # will eventually end up in the 4-2-1 loop.

        text_n = Text("N: ").move_to(RIGHT * 14 + UP * 14).scale(3)
        current_n = Integer(number=0).next_to(text_n, RIGHT, buff=1).scale(3)

        text_iter = Text("Iterations: ").next_to(text_n, DOWN, buff=2).scale(2)
        current_iter = Integer(number=0).next_to(text_iter, RIGHT, buff=1).scale(2)

        self.play(
            FadeIn(text_n), FadeIn(current_n), FadeIn(text_iter), FadeIn(current_iter)
        )

        for K in range(1, 101):
            print(f"{K = }")

            c = K

            if K == 7:
                continue

            collz = []
            verts = []

            # change opacity so it feels less busy
            if K < 30:
                self.play(
                    LINES.animate.set_opacity(0.25),
                    NODES.animate.set_opacity(0.25),
                    loop.animate.set_opacity(0.25),
                    run_time=2 * 0.2,
                )
            else:
                self.play(
                    LINES.animate.set_opacity(0.15),
                    NODES.animate.set_opacity(0.15),
                    loop.animate.set_opacity(0.15),
                    run_time=2 * 0.2,
                )

            NODES = VGroup()
            LINES = VGroup()

            i = 1
            j = 0
            for v in traj(K, J):

                collz += [c]

                # vertex
                v = ax.c2p(i, c)
                verts.append(v)

                n = Node(c, iteration=i, color=METAL_COLOR)
                n.move_to(v)
                if K >= 30:
                    n.scale(0.7)

                NODES.add(n)

                i += 1

                if c == 1:
                    if j < J:
                        j += 1
                    else:
                        break

                c = f2(c)

            for vi, v in enumerate(verts):

                if vi == 0:
                    continue

                l = Arrow(verts[vi - 1], verts[vi], buff=1.0)

                LINES.add(l)

            LINES.set_opacity(1.0)
            NODES.set_opacity(1.0)

            self.play(
                Write(LINES, lag_ratio=0.5),
                Write(NODES, lag_ratio=0.5),
                ChangeDecimalToValue(current_n, K),
                ChangeDecimalToValue(current_iter, i),
                run_time=2 * (0.2 if K != 26 else 1.0),
            )

            # scaling of the axis when necessary
            nodes_ref.add(NODES)
            arrows_ref.add(LINES)

            # here we change the scaling of the axes. Of course, you may change it
            # to whatever you like.
            if K == 30:
                print("K == 30, lets zoom out")
                ax_zoom_1 = Axes(
                    x_range=[0, 150, 10],
                    y_range=[0, 500 * 2.5 * 2, 50],
                    height=6 * 3 * 1.33 * 2,
                    width=12 * 3 * 2,
                )
                ax_zoom_1.add_coordinate_labels(
                    font_size=12,
                )

                # Recalculate nodes position in new axes:

                # since we are changing the scale of the axis to be able to fit more
                # nodes on the screen, we should at least move those that are already drawn.
                # To do that, we've been keeping track of every node up until now in nodes_ref.
                # That allows us to recalculate the position they will have in the new set of axes,
                # and we can later ReplaceTransform them to our target value. We may customize the
                # animation itself too.
                nodes_ref_zoom = VGroup()
                for i in range(len(nodes_ref.submobjects)):
                    vg = nodes_ref[i]
                    vg_zoom = VGroup()
                    for i in range(len(vg.submobjects)):
                        curr_node = (
                            Node(
                                vg[i].cval, iteration=vg[i].iteration, color=METAL_COLOR
                            )
                            .set_opacity(0.05)
                            .scale(0.7)
                        )
                        new_coords = ax_zoom_1.c2p(vg[i].iteration, vg[i].cval)
                        curr_node.move_to([new_coords[0], new_coords[1], 0])
                        vg_zoom.add(curr_node)

                    nodes_ref_zoom.add(vg_zoom)

                # Finally, now that we now where everyone goes, lets transform them!
                self.play(
                    ReplacementTransform(ax, ax_zoom_1),
                    ReplacementTransform(nodes_ref, nodes_ref_zoom),
                    LaggedStartMap(FadeOut, arrows_ref),
                    runtime=2,
                )

                self.remove(arrows_ref, LINES)
                LINES = VGroup()

                # we now overwrite the axis so the following nodes are calculated in the new space.
                ax = ax_zoom_1

            # self.embed()

        self.wait(2)

        self.embed()


class SkipStep(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 25],
            y_range=[0, 50 * 2.5 * 2],
            height=6 * 3 * 1.33 * 2,
            width=12 * 3 * 2,
        )
        ax.add_coordinate_labels(
            font_size=12,
        )

        c = 7
        J = 0  # num of loops

        collz = []
        verts = []

        NODES = VGroup()
        LINES = VGroup()

        i = 1
        j = 0
        for v in traj(7, J):

            collz += [c]

            # vertex
            v = ax.c2p(i, c)
            verts.append(v)

            n = Node(c, color=METAL_COLOR)
            n.move_to(v)

            NODES.add(n)

            i += 1

            if c == 1:
                if j < J:
                    j += 1
                else:
                    break

            c = f2(c)

        for vi, v in enumerate(verts):

            if vi == 0:
                continue

            l = Arrow(verts[vi - 1], verts[vi], buff=0.5)  # , path_arc=45*DEGREES)

            LINES.add(l)

        # --------------------------------------------
        # Pick a number, any number.

        # self.add_sound("Opening VO")

        cards = VGroup()

        for n in range(1, 10):
            cards.add(Node(n, color=METAL_COLOR))

        cards.arrange(ORIGIN)
        cards.scale(0.5)

        self.camera.frame.move_to(cards)
        self.camera.frame.shift(RIGHT * 0.5)

        cards.shift(LEFT * 2)

        self.add(cards)
        self.play(cards.animate.arrange(RIGHT, center=False))

        self.wait()

        # 7 - good choice
        self.play(
            *[FadeOut(c, UP, rate_func=rush_from) for c in cards if c.cval != 7],
            cards[6].animate.set_stroke(YELLOW_A, width=5),
            # run_time = 2* 1.5,
        )

        NODES[0].set_state(True)

        # ... If the number is odd...
        self.play(
            Transform(cards[6], NODES[0], replace_mobject_with_target_in_scene=True),
            self.camera.frame.animate.move_to(NODES[0]),
            # run_time = 2* 2* 1.5,
        )

        self.wait(2.0)

        rstep = lambda i: i < 2
        rfunc = smooth

        # def rtime(i):
        #     if i < 2:
        #         return 2.
        #     elif i < 13:
        #         return 1.5
        #     else:
        #         return 1.

        times = [
            14 - 6 - 1.5,  # 0
            18 - 14 - 1,  # 1
            25 - 18 - 1,  # 2
            28 - 25,  # 3
            5 - 0.65,  # 4
            21 - 19 + 1,  # 5
            25 - 21 + 1,  # 6
            28 - 25 + 2.85,  # 7
            34 - 28 - 0.5,  # 8
            37 - 34 - 0.5 - 1.225,  # 9
            40 - 37 - 0.5 - 0.5,  # 10
            46 - 40 - 1 - 0.5,  # 11
            49 - 46 - 1 - 0.5,  # 12
            50 - 49 - 0.15,  # 13
            52 - 50 - 0.435,  # 14
            56 - 52 - 1.25,  # 15
            60 - 56,
            # 62-60,
            # 63-62,
            # 65-63,
            # 68-65,
            # 69-68,
            # 70-69
        ]

        times = [t + (sum(times) / len(times) - t) * 0.25 for t in times]

        # self.embed()

        def rtime(i):
            return 1

            if i < (len(times) - 1):
                print(f"... {i} >>> run_time:", times[i])
                return times[i]

            return 4

        # We are going to apply two rules:

        for v in range(0, len(collz)):

            # Each iteration starts with a centered node, illuminated!

            c = collz[v]

            if v >= len(collz) - 1:
                break

            if (c % 2) != 0:  # ------------------------------------ ODD

                print(">>> Odd! ... iteration:", v, "... number:", c)

                tdist = [1.75, 1.45, 0.3275]

                tdist = [t / sum(tdist) for t in tdist]

                # If the number is odd
                # multiply by three and add one.

                RULE = Tex("\\times 3", "+ 1", font_size=75)
                RULE.next_to(NODES[v])

                self.play(
                    NODES[v].animate.set_stroke(COLLATZ_RED, width=5),
                    Write(RULE),
                    # run_time = 2* rtime(v) * tdist[0]
                )

                # self.embed()

                NEW = Node(3 * c, color=METAL_COLOR)
                NEW.move_to(ax.c2p(v + 2, 3 * c))

                NLN = Arrow(
                    NODES[v].get_center(), NEW.get_center(), buff=0.5
                )  # , path_arc=45*DEGREES)

                self.play(
                    Transform(
                        RULE[0],
                        NLN,  # LINES[v],
                        replace_mobject_with_target_in_scene=True,
                    ),
                    self.camera.frame.animate.move_to(NODES[v + 1]),
                    Write(NEW),
                    RULE[1].animate.move_to(NEW.get_center() + RIGHT * 1.15),
                    # run_time = 2* rtime(v) * tdist[1]
                )

                TO = 2.0 * (NODES[v + 1].get_center() - NEW.get_center())

                self.play(
                    NODES[v].animate.set_stroke(BLACK, width=0),
                    FadeOut(RULE[1], TO),
                    Transform(NLN, LINES[v], replace_mobject_with_target_in_scene=True),
                    Transform(NEW.circ, NODES[v + 1].circ),
                    # replace_mobject_with_target_in_scene=True),
                    TransformMatchingTex(
                        NEW.text,
                        NODES[v + 1].text,
                        replace_mobject_with_target_in_scene=True,
                    ),
                    # Write(LINES[v]),
                    rate_func=rfunc,
                    # run_time = 2* rtime(v) * tdist[2]
                )

                # self.embed()

                if rstep(v):
                    self.wait()

            else:  # ------------------------------------ EVEN

                # If the number is even, divide by two!
                print(">>>Even! ... iteration:", v, "... number:", c)

                RULE = Tex("\\divisionsymbol 2", font_size=75)
                RULE.next_to(NODES[v])

                self.play(
                    Write(RULE),
                    NODES[v].animate.set_stroke(COLLATZ_AQUA, width=5),
                    # run_time = 2* rtime(v)/2
                )

                self.play(
                    Transform(
                        RULE, LINES[v], replace_mobject_with_target_in_scene=True
                    ),
                    self.camera.frame.animate.move_to(NODES[v + 1]),
                    # Write(LINES[v]),
                    Write(NODES[v + 1]),
                    NODES[v].animate.set_stroke(BLACK, width=0),
                    rate_func=rfunc,
                    # run_time = 2* rtime(v)/2,
                )

                if rstep(v):
                    self.wait()

                # self.embed()

            # self.embed()

        # REITERATE RULES

        self.wait()

        # we're in a loop!
        loop = Arrow(verts[-1] + UP, verts[-3] + UP, buff=0.5, path_arc=90 * DEGREES)
        self.play(Write(loop))

        x = 0

        arro = Arrow(NODES[x], NODES[x + 2])
        texy = Tex("{3x+1 \\over 2}")
        texy.next_to(arro, ORIGIN)

        self.play(self.camera.frame.animate.move_to(arro))
        self.play(
            NODES[x].animate.set_stroke(COLLATZ_RED, width=5), Write(texy), run_time=3
        )
        self.play(ReplacementTransform(texy, arro), run_time=2)

        self.embed()
