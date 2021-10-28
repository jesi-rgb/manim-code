"""

    Written by Jonny Hyman, July 2021 (www.jonnyhyman.com) for Veritasium
    - This file covers the Collatz / Brownian motion animations

    Please do not share this code unless given explicit permission by both
                    Jonny Hyman and Derek Muller

"""
# CUSTOM CONFIG
# font: "CMU Sans Serif"
#   background_color: "#010326"
import networkx as nx
import numpy as np
from manimlib import *

from numba import njit
from matplotlib import cm
import random

import pickle


from inspect import getsource

ps = lambda x: print(getsource(x))

# with help from:
# - https://github.com/zachvoll/Collatz/blob/master/collatz.py
# - https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-graphs-from-networkx-with-python-3
# - https://github.com/Xunius/Collatz/blob/master/collatz.py

# Run the following:
# manimgl .py class

# Flags to append:
# Use -s to skip to the end and just save the final frame
# Use -w to write the animation to a file
# Use -o to write it to a file and open it once done
# Use -n <number> to skip ahead to the n'th animation of a scene.
# more flags here: https://3b1b.github.io/manim/getting_started/configuration.html

COLLATZ_RED = "#F23545"
COLLATZ_NAVY = "#010326"
COLLATZ_BLUE = "#1B21A6"
COLLATZ_SKY = "#2745F2"
COLLATZ_AQUA = "#6AD9D9"

METAL_COLOR = Color(hsl=(0.55, 0.075, 3 / 20))

COLLATZ_ODD = COLLATZ_RED
COLLATZ_EVEN = COLLATZ_AQUA


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


"""
int -> int:int dictionary
collatz takes in a number and generates collatz sequeunces for numbers [1,n].
It utilizes a memoization dictionary to avoid having to repeat solving for previously found sequences.
e.g. if you already solved for 8 with the solution being 8:4, 4:2, 2:1, 1:1 and wanted 16 you'd
generate just 16:8, add it to the dictionary, and already have the answer for 8.
"""


def collatz(n):
    reldict = {1: 1}
    oldn = 1
    for i in range(2, n + 1):
        while i not in reldict:
            oldn = i
            if i % 2 == 0:
                i //= 2
            else:
                i = 3 * i + 1
            if oldn not in reldict:
                reldict[oldn] = i
    return reldict


def hierarchy_pos(G, root, levels=None, width=1.0, height=1.0):
    """If there is a cycle that is reachable from root, then this will see infinite recursion.
    G: the graph
    root: the root node
    levels: a dictionary
            key: level number (starting from 0)
            value: number of nodes in this level
    width: horizontal space allocated for drawing
    height: vertical space allocated for drawing"""

    TOTAL = "total"
    CURRENT = "current"

    def make_levels(levels, node=root, currentLevel=0, parent=None):
        """Compute the number of nodes for each level"""
        if not currentLevel in levels:
            levels[currentLevel] = {TOTAL: 0, CURRENT: 0}
        levels[currentLevel][TOTAL] += 1
        neighbors = G.neighbors(node)
        for neighbor in neighbors:
            if not neighbor == parent:
                levels = make_levels(levels, neighbor, currentLevel + 1, node)
        return levels

    def make_pos(pos, node=root, currentLevel=0, parent=None, vert_loc=0):
        dx = 1 / levels[currentLevel][TOTAL]
        left = dx / 2
        pos[node] = ((left + dx * levels[currentLevel][CURRENT]) * width, vert_loc)
        levels[currentLevel][CURRENT] += 1
        neighbors = G.neighbors(node)
        for neighbor in neighbors:
            if not neighbor == parent:
                pos = make_pos(
                    pos, neighbor, currentLevel + 1, node, vert_loc - vert_gap
                )
        return pos

    if levels is None:
        levels = make_levels({})
    else:
        levels = {l: {TOTAL: levels[l], CURRENT: 0} for l in levels}

    vert_gap = height / (max([l for l in levels]) + 1)

    return make_pos({})


# ------------------ CORAL STUFF


def CollatzNext(n):
    """Compute the next Collatz number

    Args:
        n (int): current number
    Returns:
        n//2 if n is even, 3*n+1 otherwise
    """
    return n // 2 if n % 2 == 0 else 3 * n + 1


def CollatzSeq(n, cache=None):
    """Get the Collatz sequence from a give positive int down to 1

    Args:
        n (int): current number.
    Kwargs:
        cache (dict): cache to store known sequences.
                      Key: give poistive int.
                      Value: Collatz sequence starting from the key. E.g.
                      cache[4] = [4, 2, 1].
    Returns:
        res (list): Collatz sequence starting from <n>.
        cache (dict): updated cache.
    """

    if n < 1 or int(n) != n:
        raise Exception("<n> needs to be a positive integer >= 1.")

    if cache is None:
        cache = {}

    if n in cache:
        return cache[n]

    res = [n]
    cur = n
    while res[-1] != 1:
        new = CollatzNext(cur)
        # see new number in cache or not, if so, extend the cached seq
        if new in cache:
            res.extend(cache[new])
        else:
            res.append(new)
            cur = new

    # update cache
    cache[n] = res

    return res, cache


def CollatzSeqCoords(seq, params, cache=None):
    """Compute coordinates of Collatz sequence for plotting

    Args:
        seq (list): a given Collatz sequence, with last element being 1.
    Kwargs:
        cache (dict): cache to store known sequence coordinates.
                      Key: give poistive int.
                      Value: Collatz sequence coordinates starting from the key.
    Returns:
        new_coords (ndarray): Nx3 ndarray of the coordinates of the Collatz sequence.
                              N is the length of <seq>.
                              Column 1: x-coordinates.
                              Column 2: y-coordinates.
                              Column 3: angle of line in degrees.
        cache (dict): updated cache.
    """

    dl = params["dl"]
    theta0 = params["theta0"]
    dtheta_odd = params["dtheta_odd"]
    dtheta_even = params["dtheta_even"]

    if cache is None:
        cache = {}

    if seq[0] in cache:
        return cache[seq[0]]

    # the root point 1
    if len(seq) == 1 and seq[0] == 1:
        res = np.array([[0, 0, theta0]])
        cache[1] = res
        return res, cache

    # find the known sub-sequence
    # E.g. seq = [8, 4, 2, 1]
    # 2 in cache, then known sub-sequence is [2, 1]
    cur = 0
    while True:
        if seq[cur] in cache:
            break
        cur += 1

    found_coords = cache[seq[cur]]  # coordinates of the known sequence
    remain_seq = seq[:cur][::-1]  # new numbers not known in cache, e.g. [4, 8]
    last_number = seq[cur]  # last known Collatz number, e.g. 2
    last = found_coords[0]  # coordinate of the last known Collatz number
    new_coords = []  # new coordinates

    def sigmoid(x):
        return 1.0 / (1 + np.exp(-x))

    for ii, nii in enumerate(remain_seq):

        lx, ly, ltheta = last  # last known point
        # compute rotation angle
        if (nii % 2) == 0:
            dtheta = dtheta_even
        else:
            dtheta = dtheta_odd

        # dtheta=dtheta*(1+sigmoid(abs(nii-last_number))) # scale up rotation

        # compute the coordinate for the current point
        newtheta = ltheta + dtheta
        newxii = lx + dl * np.cos(newtheta * np.pi / 180)
        newyii = ly + dl * np.sin(newtheta * np.pi / 180)
        new_coords.append((newxii, newyii, newtheta))

        # update the last known point
        last = (newxii, newyii, newtheta)
        last_number = nii

    new_coords = np.r_[np.array(new_coords)[::-1], found_coords]

    # update cache
    cache[seq[0]] = new_coords

    return new_coords, cache


def update_all(i, line_params, ax):

    results = []
    for ii in range(len(line_params)):
        xx, yy, line = line_params[ii]
        line.set_data(xx[:i], yy[:i])
        results.append(line)
    return results


def grow_coral(params):
    """number is like `numbers=range(1,1200)`"""

    numbers = params["numbers"]

    # ------------Compute Collatz sequences------------
    cache = {}
    t1 = time.time()
    for i in numbers:
        aa, cache = CollatzSeq(i, cache=cache)
    t2 = time.time()
    print("Sequences took =", t2 - t1)

    # -------------Compute line coordinates-------------
    coord_cache = {}
    t1 = time.time()
    for i in numbers:
        sii = cache[i]
        _, coord_cache = CollatzSeqCoords(sii, params, cache=coord_cache)
    t2 = time.time()
    print("Coordinates took =", t2 - t1)

    return coord_cache


# --------------- MANIM TIME! ---------------


class Node(VGroup):
    def __init__(self, text, color=METAL_COLOR, stroke_width=6, font_color=WHITE):

        size = 30 / max(2, len(str(text)))

        self.text = Text(
            str(text), font="Andale Mono", font_size=size, color=font_color
        )

        self.circ = Circle(radius=0.5 / 2)
        self.circ.set_fill(color, opacity=1.0)
        self.circ.set_stroke(WHITE, width=stroke_width)

        if str(text).isnumeric():
            self.cval = int(text)
        else:
            self.cval = None

        super().__init__(self.circ, self.text)
        self.arrange(ORIGIN, buff=0)

        # created_at = self.time
        #
        # self.add_updater(
        #     lambda m: m.set_width(w0 * math.cos(self.time - now))
        # )


class Coraline(Polygon):
    def __init__(self, *verts, color=BLUE_C, stroke_width=13, stroke_opacity=1.0):
        verts = list(verts)
        # verts += reversed(verts)

        super().__init__(
            *verts,
            stroke_opacity=stroke_opacity,
            stroke_width=stroke_width,
            stroke_color=rgba_to_color(color),
            joint_type="round",
        )

    def init_points(self):
        verts = self.vertices
        self.set_points_as_corners([*verts])

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


def f2(z):

    if (z % 2) != 0:  # odd
        return 3 * z + 1
    else:
        return z // 2


class _13_WhyFall_Pt1(Scene):
    def construct(self):

        # -----------------------------------------------------------------
        # -------- Why fall to zero?
        # -----------------------------------------------------------------

        # If odd we’re multiplying by 3 and when even - only dividing by two

        x_ax = {}
        x_ax["include_tip"] = False
        # x_ax['tick_size'] = .05/2
        # x_ax['longer_tick_multiple'] = 3.0
        # x_ax['numbers_with_elongated_ticks'] = range(0,101,10)

        y_ax = {}
        y_ax["include_tip"] = False
        y_ax["tick_size"] = 0.05 / 2
        y_ax["longer_tick_multiple"] = 3.0
        y_ax["numbers_with_elongated_ticks"] = range(0, 101, 10)

        ax = Axes(
            x_range=[0, 100],
            y_range=[0, 80],
            width=12.22 * 3,
            x_axis_config=x_ax,
            y_axis_config=y_ax,
        )

        ax.add_coordinate_labels(
            range(0, 100 + 1, 1),
            range(0, 81, 10),
            font_size=12,
        )

        ax.next_to([-12.22 / 2, 0, 0])

        # self.play(Write(ax))
        self.add(ax)
        # self.remove(ax.y_axis)

        ANIMS_1 = []
        ANIMS_2 = []
        ANIMS_3 = []
        ANIMS_4 = []
        ANIMS_5 = []

        # self.embed()

        NUMBERS = {}

        for n in range(1, 100 + 1):

            c1 = n
            c2 = f2(c1)

            p1 = ax.c2p(n, c1)
            p2 = ax.c2p(n + 1, c2)

            n1 = Node(c1)
            n1.move_to(p1)
            # n1.scale(.66)

            n2 = Node(c2)
            n2.move_to(p2)
            n2.scale(0.5)

            a11 = Arrow(p1, p1, thickness=0.01, buff=0.125)
            a12 = Arrow(p1, p2, thickness=0.01, buff=0.125)

            NUMBERS[n] = VGroup(n1, n2, a12)

            # coloring circles
            for nx in [n1, n2]:
                if (nx.cval % 2) == 0:
                    nx.circ.set_stroke(COLLATZ_EVEN, width=1)

                else:
                    nx.circ.set_stroke(COLLATZ_ODD, width=1)

            # coloring lines
            if (c1 % 2) == 0:
                a12.set_color(COLLATZ_EVEN)
                a11.set_color(COLLATZ_EVEN)
            else:
                a12.set_color(COLLATZ_ODD)
                a11.set_color(COLLATZ_ODD)

            ANIMS_1 += [
                # n2.animate.scale(.66),
                Write(n1),
                n1.animate.scale(0.5),
            ]

            ANIMS_2 += [
                [
                    Transform(n1.copy(), n2, replace_mobject_with_target_in_scene=True),
                    Transform(a11, a12, replace_mobject_with_target_in_scene=True),
                ],
            ]

            if c1 % 2 == 0:  # not in [25]: # save these for later
                ANIMS_3 += [FadeOut(n1), FadeOut(n2), FadeOut(a12)]
                ANIMS_4 += [FadeIn(n1), FadeIn(n2), FadeIn(a12)]

            else:
                ANIMS_5 += [FadeOut(n1), FadeOut(n2), FadeOut(a12)]

        for i, a in enumerate(ANIMS_1):
            # print('...', i)
            if i > 35 * 2:
                if type(a) == Write:
                    self.add(a.mobject)
                else:
                    a.mobject.scale(0.5)
            else:
                self.play(a, run_time=0.1)

        for i, a in enumerate(ANIMS_2):
            # print('...', i)

            # a[1].mobject.add_updater(lambda m: self.bring_to_back(m))
            # a[1].target_mobject.add_updater(lambda m: self.bring_to_back(m))

            self.play(*a, run_time=0.5)

            if i == 24:
                #     self.play(
                #                 self.camera.frame.animate.shift(
                #                             RIGHT*12.22 + OUT*6 + UP*1.5
                #                 ),
                #     )
                #
                # if i == 71:

                r1 = Tex("3 \\times x + 1", font_size=300, color=COLLATZ_ODD)
                r1.move_to(UP * 10 + RIGHT * 3)

                r2 = Tex("x \\divisionsymbol 2", font_size=300, color=COLLATZ_EVEN)
                r2.move_to(RIGHT * 25 + DOWN * 1)

                # it feels like on average the sequence should grow!
                self.play(
                    self.camera.frame.animate.move_to(
                        ax.get_center() + OUT * 25 + UP * 5
                    ),
                    Write(r1),
                    Write(r2),
                )

        # Every time you multiply an odd number by 3 and then add one, it will always become even number.

        self.play(
            *ANIMS_3,
            FadeOut(r1),
            FadeOut(r2),
            self.camera.frame.animate.move_to(ax.c2p(17, 40)),
            run_time=0.75,
        )

        self.play(
            self.camera.frame.animate.move_to(ax.c2p(80, 250)),
            run_time=30.0,
        )

        self.wait()

        self.play(
            *ANIMS_4,
            *ANIMS_5,
            self.camera.frame.animate.move_to(ax.c2p(17, 40)),
            run_time=2.0,
        )

        self.play(
            self.camera.frame.animate.move_to(ax.c2p(40, 40)),
            run_time=15.0,
        )

        self.embed()


class _13_WhyFall_Pt2(Scene):
    def construct(self):

        # If you land on a number like 1024, which is a power of 2, it’s a really quick fall
        # -- 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1.
        # The increases are more gradual, and the falls can be very sudden.

        ax = Axes(
            x_range=[0, 12], y_range=[0, 1024]
        )  # , height=6*3*1.33*2, width=12*3*2)
        # ax.add_coordinate_labels(font_size=12,)
        # self.add(ax)

        collz = traj(341, 0)
        verts = []

        NODES = VGroup()
        LINES = VGroup()

        for i, v in enumerate(collz):

            n = Node(v, color=METAL_COLOR)
            n.move_to(ax.c2p(i + 1, v))
            n.scale(1.5)

            NODES.add(n)

            if i > 0:
                a = Arrow(NODES[i - 1], NODES[i], thickness=0.05, buff=0.0125)

                LINES.add(a)

        rtime = lambda x: 2.0
        rfunc = smooth
        rstep = lambda x: 0

        # self.camera.frame.move_to(NODES[0].get_center() * IN*5)
        self.camera.frame.move_to(NODES)

        # We are going to apply two rules:
        for v in range(0, len(collz)):

            # Each iteration starts with a centered node, illuminated!
            c = collz[v]

            if c == 1024:
                self.wait()

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
                    NODES[v].animate.set_stroke(COLLATZ_ODD, width=1),
                    Write(RULE),
                    run_time=rtime(v) * tdist[0],
                )

                NEW = Node(3 * c, color=METAL_COLOR)
                NEW.move_to(ax.c2p(v + 2, 3 * c))
                NEW.scale(1.5)

                NLN = Arrow(
                    NODES[v].get_center(), NEW.get_center(), buff=0.5
                )  # , path_arc=45*DEGREES)

                self.play(
                    Transform(
                        RULE[0],
                        NLN,  # LINES[v],
                        replace_mobject_with_target_in_scene=True,
                    ),
                    # self.camera.frame.animate.move_to(NODES[v+1]),
                    Write(NEW),
                    RULE[1].animate.move_to(NEW.get_center() + RIGHT * 1.15),
                    run_time=rtime(v) * tdist[1],
                )

                TO = 2.0 * (NODES[v + 1].get_center() - NEW.get_center())

                self.play(
                    # NODES[v].animate.set_stroke(BLACK, width=0),
                    FadeOut(RULE[1], TO),
                    Transform(NLN, LINES[v], replace_mobject_with_target_in_scene=True),
                    Transform(NEW.circ, NODES[v + 1].circ),
                    # replace_mobject_with_target_in_scene=True),
                    # TransformMatchingTex(NEW.text, NODES[v+1].text,
                    #     replace_mobject_with_target_in_scene=True),
                    Transform(
                        NEW.text,
                        NODES[v + 1].text,
                        replace_mobject_with_target_in_scene=True,
                    ),
                    # Write(LINES[v]),
                    rate_func=rfunc,
                    run_time=rtime(v) * tdist[2],
                )

                # self.embed()

            else:  # ------------------------------------ EVEN

                # If the number is even, divide by two!
                print(">>>Even! ... iteration:", v, "... number:", c)

                RULE = Tex("\\divisionsymbol 2", font_size=75)
                RULE.next_to(NODES[v])

                self.play(
                    Write(RULE),
                    NODES[v].animate.set_stroke(COLLATZ_EVEN, width=1),
                    run_time=rtime(v) / 2,
                )

                self.play(
                    Transform(
                        RULE, LINES[v], replace_mobject_with_target_in_scene=True
                    ),
                    # self.camera.frame.animate.move_to(NODES[v+1]),
                    # Write(LINES[v]),
                    Write(NODES[v + 1]),
                    # NODES[v].animate.set_stroke(BLACK, width=0),
                    rate_func=rfunc,
                    run_time=rtime(v) / 2,
                )

        # self.play(self.camera.frame.animate.move_to(NODES))

        self.embed()


class _13_WhyFall_Pt2_NO_EQUATIONS(Scene):
    def construct(self):

        # If you land on a number like 1024, which is a power of 2, it’s a really quick fall
        # -- 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1.
        # The increases are more gradual, and the falls can be very sudden.

        ax = Axes(
            x_range=[0, 12], y_range=[0, 1024]
        )  # , height=6*3*1.33*2, width=12*3*2)
        # ax.add_coordinate_labels(font_size=12,)
        # self.add(ax)

        collz = traj(341, 0)
        verts = []

        NODES = VGroup()
        LINES = VGroup()

        for i, v in enumerate(collz):

            n = Node(v, color=METAL_COLOR)
            n.move_to(ax.c2p(i + 1, v))
            n.scale(1.5)

            NODES.add(n)

            if i > 0:
                a = Arrow(NODES[i - 1], NODES[i], thickness=0.05, buff=0.0125)

                LINES.add(a)

        rtime = lambda x: 2.0
        rfunc = smooth
        rstep = lambda x: 0

        # self.camera.frame.move_to(NODES[0].get_center() * IN*5)
        self.camera.frame.move_to(NODES)
        # self.camera.frame.move_to(LINES[0].get_center()+IN*2)

        # We are going to apply two rules:
        for v in range(0, len(collz)):

            # Each iteration starts with a centered node, illuminated!
            c = collz[v]

            if c == 1024:
                self.wait()
                # self.play(self.camera.frame.animate.move_to(NODES))

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
                    NODES[v].animate.set_stroke(COLLATZ_ODD, width=1),
                    # Write(RULE),
                    run_time=rtime(v) * tdist[0],
                )

                NEW = Node(3 * c, color=METAL_COLOR)
                NEW.move_to(ax.c2p(v + 2, 3 * c))
                NEW.scale(1.5)

                NLN = Arrow(
                    NODES[v].get_center(), NEW.get_center(), buff=0.5
                )  # , path_arc=45*DEGREES)

                # self.play(
                #             Transform(RULE[0], NLN,#LINES[v],
                #                 replace_mobject_with_target_in_scene=True),
                #
                #             # self.camera.frame.animate.move_to(NODES[v+1]),
                #
                #             Write(NEW),
                #
                #             RULE[1].animate.move_to(NEW.get_center() + RIGHT*1.15),
                #
                #             run_time = rtime(v) * tdist[1]
                # )

                TO = 2.0 * (NODES[v + 1].get_center() - NEW.get_center())

                self.play(
                    # NODES[v].animate.set_stroke(BLACK, width=0),
                    # FadeOut(RULE[1], TO),
                    Write(LINES[v]),
                    Write(NODES[v + 1]),
                    # Transform(NLN, LINES[v],
                    # replace_mobject_with_target_in_scene=True),
                    # Transform(NEW.circ, NODES[v+1].circ),
                    # replace_mobject_with_target_in_scene=True),
                    # TransformMatchingTex(NEW.text, NODES[v+1].text,
                    #     replace_mobject_with_target_in_scene=True),
                    # Transform(NEW.text, NODES[v+1].text,
                    #     replace_mobject_with_target_in_scene=True),
                    # Write(LINES[v]),
                    rate_func=rfunc,
                    run_time=1,  # rtime(v) * tdist[2]
                )

                # self.embed()

            else:  # ------------------------------------ EVEN

                # If the number is even, divide by two!
                print(">>>Even! ... iteration:", v, "... number:", c)

                RULE = Tex("\\divisionsymbol 2", font_size=75)
                RULE.next_to(NODES[v])

                self.play(
                    # Write(RULE),
                    NODES[v].animate.set_stroke(COLLATZ_EVEN, width=1),
                    run_time=0.5,  # rtime(v)/2
                )

                self.play(
                    # Transform(RULE, LINES[v],
                    #     replace_mobject_with_target_in_scene=True),
                    Write(LINES[v]),
                    # self.camera.frame.animate.move_to(NODES[v+1]),
                    # Write(LINES[v]),
                    Write(NODES[v + 1]),
                    # NODES[v].animate.set_stroke(BLACK, width=0),
                    rate_func=rfunc,
                    run_time=1,  # rtime(v)/2,
                )

        # self.play(self.camera.frame.animate.move_to(NODES))

        self.embed()


class _13_WhyFall_Pt3(Scene):
    def construct(self):
        # -----------------------------------------------------------------
        # -------- Why falling to 1 makes sense
        # -----------------------------------------------------------------
        # Consider what happens as you pass from one odd integer to another.
        # Roughly speaking, half the time
        # you’ll multiply by ~3/2 (that is, do (3x+1)/2);
        # but ¼ of the time the multiplicative factor will be (3/4),
        # and ⅛ of the time it’ll be ⅜, etc.
        # So the *multiplicative* factor is expected to be
        # (3/2)^(½)(¾)^(¼)(⅜)^(⅛)... = ¾, which is less than 1
        # ... this should be nested-function vibe - collapsing to simplified

        # c=1
        #
        # factors = []
        #
        # for r in range(2,12):
        #
        #     while True:
        #
        #         t = np.array(traj(c))
        #
        #         if ((t[0]%2)!=0) and all(t[1:r]%2==0) and ((t[r]%2)!=0) and (t[r]!=1):
        #             # print(c, 'has', r-1, 'width:')
        #             # print('...',t[:r+1])
        #             # print('...',t[r]/t[0], "ratio")
        #             # print()
        #             c=1
        #             factors.append(t[:r+1])
        #             break
        #         else:
        #             c +=1

        ax = Axes(x_range=[1, 10], y_range=[0, 12], width=24)
        # self.add(ax)

        factors = [3, 9, 13, 37, 53, 149, 213, 597, 853]  # ,2389]

        groups = {}
        group = VGroup()
        braces = VGroup()
        labels = VGroup()
        freqs = VGroup()
        freqs2 = VGroup()
        # arrows = VGroup()

        for i, seed in enumerate(factors):
            t = traj(seed, 0)[: i + 3]

            groups[i] = VGroup()

            for j, c in enumerate(t):
                n = Node(c)
                n.move_to(ax.c2p(i + 1, j + 1))
                n.scale(0.5)

                a = Arrow(
                    ax.c2p(i + 1, j + 1), ax.c2p(i + 1, j + 2), thickness=0.01, buff=0
                )

                if (n.cval % 2) == 0:
                    n.set_stroke(COLLATZ_EVEN, width=1)
                else:
                    n.set_stroke(COLLATZ_ODD, width=1)

                if j < len(t) - 1:
                    groups[i].add(a)

                groups[i].add(n)

            group.add(groups[i])

            b = Brace(groups[i], RIGHT)
            T = Tex(
                "{3 \\over " + str(2 ** (i + 1)) + "}",
                "\\times",
                str(t[0]),
                "\\approx",
                str(t[-1]),
                font_size=24,
            )
            T.next_to(b, RIGHT)
            T.set_color_by_tex_to_color_map(
                {
                    T[-1].tex_string: COLLATZ_ODD,
                    T[2].tex_string: COLLATZ_ODD,
                    T[0].tex_string: GOLD_A,
                }
            )

            braces.add(b)
            labels.add(T)

            F = Tex("{1 \\over " + str(2 ** (i + 1)) + "}", font_size=18)
            F.next_to(groups[i], DOWN)
            freqs.add(F)

            F2 = Text("of the time", font_size=18, font="Europa-Regular")
            F2.next_to(F, RIGHT)
            freqs2.add(F2)

        self.camera.frame.move_to(group[0].get_center() + IN * (5)),

        for i in range(len(factors)):
            print("...", i)

            self.play(
                self.camera.frame.animate.move_to(
                    groups[i].get_center() + IN * (5 - i)
                ),
            )

            self.play(
                Write(groups[i]),
                lag_ratio=0.5,
            )

            self.play(
                Write(braces[i]),
                Write(labels[i]),
                Write(freqs[i]),
                Write(freqs2[i]),
            )

            self.wait()

        self.play(
            self.camera.frame.animate.move_to(group.get_center() + OUT * 20),
        )

        s = []
        u = {}
        ttc = {}

        for i in range(len(factors)):
            m = 2 ** (i + 1)
            s += [  # "(",
                "{3 \\over " + str(m) + "}",
                "^",
                "{1 \\over " + str(m) + "}",
            ]  # ")"]

            ttc["{3 \\over " + str(m) + "}"] = GOLD_A

            if i < len(factors) - 1:
                s += ["\\times"]

        EQ = Tex(*s, font_size=75)
        EQ.set_color_by_tex_to_color_map(ttc)

        # Build the tex transforms
        tex_transforms = []

        for i, e in enumerate(EQ):
            for j, f in enumerate(freqs):
                if f.tex_string == e.tex_string:
                    # self.embed()
                    tex_transforms.append(Transform(freqs[j], EQ[i]))

            for j, f in enumerate(labels):
                if f[0].tex_string == e.tex_string:
                    # self.embed()
                    tex_transforms.append(Transform(labels[j][0], EQ[i]))

                    tex_transforms += [FadeOut(b) for b in labels[j][1:]]

        self.play(
            self.camera.frame.animate.move_to(EQ.get_center() + OUT * 20),
            FadeOut(freqs2),
            FadeOut(braces),
            FadeOut(group),
            *tex_transforms,
        )

        self.play(Write(EQ), run_time=0.5)

        t = Tex("\\approx {3 \\over 4}", font_size=75, color=GOLD_A)
        t.next_to(EQ, RIGHT)

        self.play(self.camera.frame.animate.shift(RIGHT), Write(t))
        self.wait()

        self.embed()


class _13_WhyFall_Pt4(Scene):
    def construct(self):
        # -----------------------------------------------------------------
        # -------- Why fall to zero?
        # -----------------------------------------------------------------

        # If odd we’re multiplying by 3 and when even - only dividing by two

        x_ax = {}
        x_ax["include_tip"] = False
        # x_ax['tick_size'] = .05/2
        # x_ax['longer_tick_multiple'] = 3.0
        # x_ax['numbers_with_elongated_ticks'] = range(0,101,10)

        y_ax = {}
        y_ax["include_tip"] = False
        y_ax["tick_size"] = 0.05 / 2
        y_ax["longer_tick_multiple"] = 3.0
        y_ax["numbers_with_elongated_ticks"] = range(0, 101, 10)

        ax = Axes(
            x_range=[0, 100],
            y_range=[0, 80],
            width=12.22 * 3,
            x_axis_config=x_ax,
            y_axis_config=y_ax,
        )

        ax.add_coordinate_labels(
            range(0, 100 + 1, 1),
            range(0, 81, 10),
            font_size=12,
        )

        ax.next_to([-12.22 / 2, 0, 0])

        # self.play(Write(ax))
        self.add(ax)
        # self.remove(ax.y_axis)

        ANIMS_1 = []
        ANIMS_2 = []
        ANIMS_3 = []
        ANIMS_4 = []
        ANIMS_5 = []

        # self.embed()

        NUMBERS = {}

        for n in range(1, 100 + 1):

            converged_on_odd = False

            c1 = n
            p1 = ax.c2p(n, c1)

            n1 = Node(c1)
            n1.move_to(p1)
            n1.scale(0.5)

            NUMBERS[n] = VGroup(n1)

            if (n1.cval % 2) == 0:
                n1.circ.set_stroke(COLLATZ_EVEN, width=1)

            else:
                n1.circ.set_stroke(COLLATZ_ODD, width=1)

            i = 1

            while not converged_on_odd:

                c2 = f2(c1)
                p2 = ax.c2p(n + i, c2)

                if (c1 % 2) != 0 and (i) == 1:
                    # don't do top of diagonal
                    converged_on_odd = True

                n2 = Node(c2)
                n2.move_to(p2)
                n2.scale(0.5)

                # a11 = Arrow(p1,p1, thickness=.01, buff=.125) # proto-
                a12 = Arrow(p1, p2, thickness=0.01, buff=0.125)  # grows to

                NUMBERS[n].add(a12)
                NUMBERS[n].add(n2)

                # coloring circles
                if (n2.cval % 2) == 0:
                    n2.circ.set_stroke(COLLATZ_EVEN, width=1)

                else:
                    n2.circ.set_stroke(COLLATZ_ODD, width=1)
                    converged_on_odd = True

                # coloring lines
                if (c1 % 2) == 0:
                    a12.set_color(COLLATZ_EVEN)
                    # a11.set_color(COLLATZ_EVEN)
                else:
                    a12.set_color(COLLATZ_ODD)
                    # a11.set_color(COLLATZ_ODD)

                c1 = c2
                p1 = p2
                n1 = n2
                i += 1

        self.camera.frame.move_to(ax.get_center() + OUT * 25 + UP * 5)

        self.play(*[Write(g) for g in NUMBERS.values()])
        self.wait()

        self.play(
            self.camera.frame.animate.move_to(ax.c2p(17, 35)), FadeOut(ax), run_time=15
        )

        self.wait()

        self.play(
            self.camera.frame.animate.move_to(ax.c2p(80, 40) + OUT * 3), run_time=45
        )

        self.play(
            self.camera.frame.animate.move_to(ax.get_center() + OUT * 25 + UP * 3.5),
            run_time=45,
        )

        self.embed()


# imports

from networkx.drawing.nx_pydot import graphviz_layout
import networkx as nx

from matplotlib import cm


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


def inv_f2(n):
    if (n % 6) in [0, 1, 2, 3, 5]:
        return (2 * n,)

    elif (n % 6) == 4:
        return (2 * n, (n - 1) // 3)


def build_tree(ns, G, max_depth, depth=0, debug=False):

    depth += 1

    if depth > max_depth:
        return

    for i, n in enumerate(ns):

        to = inv_f2(n)

        if len(to) == 1:

            (to,) = to

            if debug:
                print(i, depth, "...", to, "-->", n)

            if to not in G:
                G.add_edge(to, n)

            build_tree((to,), G, max_depth, depth=depth)

        else:

            for i, ti in enumerate(to):

                if ti not in G:
                    G.add_edge(ti, n)

                build_tree((ti,), G, max_depth, depth=depth)


def build_collatz_tree(DEPTH):

    # TODO: Load if already calculateda and save if not saved
    saveto = Path(f"nodetree_{DEPTH}.pickle")

    if saveto.exists():

        with open(saveto, "rb") as f:
            G, P = pickle.load(f)
            return G, P

    else:
        G = nx.MultiDiGraph()
        build_tree((1,), G, DEPTH)
        P = graphviz_layout(G, prog="dot")

        with open(saveto, "wb") as f:
            pickle.dump([G, P], f)

        return G, P


class _14_BuildTree_2(ThreeDScene):
    def construct(self):
        CONFIG = {
            "start_phi": 70 * DEGREES,
            "start_theta": -140 * DEGREES,
        }

        def keep_back(m):
            self.bring_to_back(m)

        # -----------------------------------------------------------------
        # -------- Build a tree
        # 1. Line plot to verticals, merge into a tree
        # 2. Build tree to depth
        # 3. Re-write the tree in a river-ly way
        # 4. Show negative loops and things that break it, like 186 billion long loop and infinite loop
        # 5. Convert the tree into a coral (fade out negative and breaking loops) and explain how to do that
        # -----------------------------------------------------------------

        # 1. Line plot to verticals
        axis_config = {}
        axis_config["include_tip"] = False
        axis_config["numbers_to_exclude"] = [0]

        y_ax = {}
        y_ax["include_tip"] = False
        y_ax["tick_size"] = 0.05 / 2
        y_ax["longer_tick_multiple"] = 3.0
        y_ax["numbers_with_elongated_ticks"] = range(0, 101, 10)

        ax = Axes(
            x_range=[0, 7],
            y_range=[0, 80],
            axis_config=axis_config,
            y_axis_config=y_ax,
        )
        ax.add_coordinate_labels(
            range(0, 8, 1),
            range(0, 81, 10),
            font_size=12,
        )
        self.begin_ambient_camera_rotation(rate=0.7)
        self.play(Write(ax))

        NODES_L = {}
        EDGES_L = {}
        ANIMS_L = []

        EDGES_L_GROUP = VGroup()

        for K in [64, 10]:

            verts = []
            collz = []

            NODES_L[K] = {}
            EDGES_L[K] = {}

            for i, c in enumerate(traj(K, 0)):

                collz += [c]
                n = Node(c, color=METAL_COLOR)
                n.circ.set_stroke(WHITE, width=0)

                v = ax.c2p(i + 1, c)
                n.move_to(v)

                verts += [v]
                NODES_L[K][c] = n

                ANIMS_L.append(Write(NODES_L[K][c]))

            for vi, v in enumerate(verts):

                if vi == 0:
                    continue

                a = collz[vi]
                b = collz[vi - 1]

                s = f"{a}<--{b}"

                EDGES_L[K][s] = Line(
                    NODES_L[K][b], NODES_L[K][a], buff=0.1, color=COLLATZ_AQUA
                )
                EDGES_L[K][s].set_opacity(0.25)
                EDGES_L[K][s]._a = a
                EDGES_L[K][s]._b = b
                EDGES_L[K][s]._K = K

                def keep(m):
                    m.set_points_by_ends(
                        NODES_L[m._K][m._b].get_center(),
                        NODES_L[m._K][m._a].get_center(),
                    )
                    # self.bring_to_back(m)

                EDGES_L[K][s].add_updater(keep)

                EDGES_L_GROUP.add(EDGES_L[K][s])

                ANIMS_L = [Write(EDGES_L[K][s])] + ANIMS_L

        self.play(
            *ANIMS_L,
            lag_ratio=0.5,
        )

        self.wait()

        # -------- 2 VERTICALS
        # ANIMS_L = []
        #
        # for KI, K in enumerate(EDGES_L):
        #     for cn, c in enumerate(NODES_L[K]):
        #         ANIMS_L += [NODES_L[K][c].animate.move_to(ORIGIN + RIGHT*(KI*2-1) + 1*DOWN*(cn) + UP*3 )]

        # self.play(FadeOut(ax), *ANIMS_L)
        # self.wait()
        # self.clear()

        old_ax = ax

        ax = Axes(x_range=[-600, 600], y_range=[0, 500], include_tip=False)

        NODES = {}
        EDGES = {}

        # cmap = cm.get_cmap("viridis")
        # cmap_ = cm.get_cmap("PuBu")
        cmap_ = cm.get_cmap("YlGnBu")
        cmap = lambda x: cmap_(1 - 0.75 * (x) ** 0.25)

        # self.camera.frame.move_to(OUT*16 + UP*6)

        FIRST = True

        print(">>> Reminder: swap out the D in range(6,18) before final renders! 💜")

        for D in range(6, 18):
            # for D in range(17, 18):

            # 2. Build tree to depth
            print(">>> DEPTH:", D)

            G, P = build_collatz_tree(D)
            Pmax = max(P)

            root = ax.c2p(*P[1])

            ANIMS = []

            for p in P:
                n = Node(
                    p,
                    color=METAL_COLOR,
                    # color=rgba_to_color(cmap((p / Pmax)**.25)),
                    stroke_width=max(min(6, 12 / len(P)), 0.01),
                )
                n._move_to = ax.c2p(*P[p]) - root
                n.move_to(n._move_to)

                if p in NODES:
                    ANIMS.append(Transform(NODES[p], n))
                else:
                    ANIMS.append(Write(n))
                    NODES[p] = n

            for e in G.edges():

                s = f"{e[1]}<--{e[0]}"

                if s in EDGES:
                    # ANIMS.append(Transform(EDGES[s], a)) # superceded by updater
                    continue

                else:

                    a = Line(NODES[e[1]], NODES[e[0]], color=WHITE)
                    # a.set_opacity(.1)
                    a._a0 = e[1]
                    a._a1 = e[0]

                    def keep(m):
                        m.set_points_by_ends(
                            NODES[m._a0].get_center(),
                            NODES[m._a1].get_center(),
                        )

                    a.add_updater(keep)

                    ANIMS = [Write(a)] + ANIMS

                    EDGES[s] = a

            EDGEG = VGroup(*EDGES.values())
            NODEG = VGroup(*NODES.values())

            for anim in ANIMS:
                anim.rate_func = rush_into

            if FIRST:

                # ONLY HAPPENS ONCE
                # 1. Merge into a tree

                ANIMS = []

                for c in NODES_L:
                    for n in NODES_L[c]:
                        ANIMS += [ReplacementTransform(NODES_L[c][n], NODES[n])]

                for e in EDGES_L:
                    for s in EDGES_L[e]:
                        ANIMS += [ReplacementTransform(EDGES_L[e][s], EDGES[s])]

                # self.embed()

                self.play(
                    *ANIMS,
                    FadeOut(old_ax),
                    self.camera.frame.animate.move_to(NODEG.get_center() + OUT * D),
                    run_time=3,
                    lag_ratio=0,
                    # lag_ratio = .5,
                )

                # self.wait()
                # self.remove(EDGES_L_GROUP) # replaced by EDGES dict

            # add the bring to back updater for all lines now that everythings visible
            EDGEG.add_updater(keep_back)

            if FIRST:
                FIRST = False

                LOOP = Arrow(
                    NODES[1].get_center() + 0.20 * RIGHT,
                    NODES[4].get_center() + 0.20 * RIGHT,
                    buff=0.05,
                    color=rgba_to_color(cmap((1 / Pmax))),
                    path_arc=179 * DEGREES,
                    thickness=0.033,
                )

                self.play(Write(LOOP))

                continue

            self.play(
                *ANIMS,
                self.camera.frame.animate.move_to(NODEG.get_center() + OUT * D),
                run_time=1.25,
                lag_ratio=0,
                # lag_ratio = .5,
            )

            self.wait(0.15)

            # self.embed()
            # self.embed()

        self.wait()  # 24
        # self.play(self.camera.frame.animate.shift(LEFT*10))
        # self.play(self.camera.frame.animate.shift(RIGHT*20))

        # remove keep back updater, it's  no longer needed, they're about to fade
        EDGEG.remove_updater(keep_back)

        # -----------------------------------------------------------------
        # -------- River
        # 3. Re-write the tree in a river-ly way
        # -----------------------------------------------------------------
        self.play(FadeOut(EDGEG), FadeOut(NODEG), FadeOut(LOOP), rate_func=rush_into)
        # self.play(FadeIn(EDGEG), FadeIn(NODEG), rate_func=rush_into)
        # self.play(FadeOut(EDGEG), FadeOut(NODEG), rate_func=rush_into)

        # figure out the deepest nodes to "river rain" from
        deepest = [v for v, d in G.in_degree() if d == 0]
        anims_r = {}
        anims_s = {}

        random.shuffle(deepest)

        for d in deepest:

            # print(d,'...',river_n)
            river_n = nx.dfs_tree(G, d).nodes

            for n in river_n:
                if n not in anims_r:
                    # print('... ...',n)

                    color = rgba_to_color(cmap((n / Pmax)))

                    if n != 1:
                        e = list(G.edges(n))[0]
                        s = f"{e[1]}<--{e[0]}"

                        anims_s[n] = FadeIn(EDGES[s])
                        EDGES[s].set_stroke(color=color)

                    anims_r[n] = FadeIn(NODES[n])
                    NODES[n].circ.set_color(color)

        # TODO: make cooler playback sequence with interleaving
        # self.play(*anims_s.values(), *anims_r.values(), run_time=5, rate_func=rush_from)
        for i in anims_r:
            if i in anims_s:
                self.bring_to_back(anims_s[i].mobject)
                self.play(anims_s[i], anims_r[i], run_time=0.1)
            else:
                self.play(anims_r[i], run_time=0.1)

        LOOP_421 = Arrow(
            NODES[1].get_center() + 0.20 * RIGHT,
            NODES[4].get_center() + 0.20 * RIGHT,
            buff=0.08,
            path_arc=179 * DEGREES,
            thickness=0.033,
        )

        LOOP_421.set_color(color=rgba_to_color(cmap(0.25)))

        self.play(
            Write(LOOP_421),
            run_time=3,
        )

        self.wait(3)

        # 4. Show negative loops and things that break it, like 186 billion long loop and infinite loop

        self.play(
            self.camera.frame.animate.move_to(NODEG.get_center() + OUT * D + DOWN * 7)
        )

        # inherit spacings from the tree above
        dx = (NODES[20].get_center() - NODES[3].get_center())[0]
        dy = (NODES[1].get_center() - NODES[2].get_center())[1]

        b = [-1, -2]  # -1
        c = [-5, -14, -7, -20, -10]  # -5
        a = [
            -17,
            -50,
            -25,
            -74,
            -37,
            -110,
            -55,
            -164,
            -82,
            -41,
            -122,
            -61,
            -182,
            -91,
            -272,
            -136,
            -68,
            -34,
        ]  # -17

        for i in [a, b, c]:
            for j in range(len(i)):

                if j == 0:
                    continue

                check = f2(i[j - 1])

                if check != i[j]:
                    AssertionError(f"Sequence {i} is not Collatz-correct at {j}")

        NLOOPS = [VGroup(), VGroup(), VGroup()]
        LLOOPS = [VGroup(), VGroup(), VGroup()]
        ALOOPS = [
            None,
        ] * 3

        for L, loop in enumerate([a, b, c]):

            Pmax = min(loop)

            for P, p in enumerate(loop):

                d = L - 1
                x = dx * (L - 1)
                y = dy * (P - 1) + dy * 3

                n = Node(
                    p,
                    # color = METAL_COLOR,
                    color=WHITE,
                    font_color=BLACK,
                    # color=rgba_to_color(cmap(p / Pmax)),
                    stroke_width=0,  # max(min(6, 12/len(P)), .01),
                )

                n.move_to([x, y, 0])

                NLOOPS[L].add(n)

            for i in range(len(NLOOPS[L])):

                if i == 0:
                    continue

                try:
                    a = Line(NLOOPS[L][i - 1], NLOOPS[L][i], color=WHITE)
                    LLOOPS[L].add(a)
                except IndexError as e:
                    print(e)
                    self.embed()

            DIREC = RIGHT if L < 2 else LEFT
            THICC = 0.033 if L > 0 else 0.1
            ANGLE = 90 if L < 2 else -90

            LOOP = Arrow(
                NLOOPS[L][-1].get_center() + 0.20 * DIREC,
                NLOOPS[L][0].get_center() + 0.20 * DIREC,
                path_arc=ANGLE * DEGREES,
                thickness=THICC,
            )

            LOOP.set_color(color=rgba_to_color(cmap(0.25)))

            ALOOPS[L] = LOOP

        for n in [1, 0, 2]:
            self.play(
                Write(LLOOPS[n]),
                Write(NLOOPS[n]),
                self.camera.frame.animate.move_to(NLOOPS[n][0]),
            )
            self.play(
                self.camera.frame.animate.move_to(NLOOPS[n][-1]),
                # rate_func=double_smooth,
                run_time=len(NLOOPS[n]),
            )
            self.play(Write(ALOOPS[n]), self.camera.frame.animate.move_to(NLOOPS[n][0]))

            self.wait()

        # self.wait()

        self.play(self.camera.frame.animate.move_to(NODES[1].get_center() + OUT * 30))

        self.wait()

        # There are two ways this conjecture could be false --
        # a number could go to infinity, not connected to the tree at all,
        # - infinitely many numbers go to infinity (all numbers in that chain) or end up in a loop.

        # GOTO INF

        qsL = VGroup()  # loop questions
        qsI = VGroup()  # infinity questions

        q = Node("?")
        q.circ.set_stroke(PURPLE_B, width=2)

        qsL.add(*[q.copy() for _ in range(50)])
        qsI.add(*[q.copy() for _ in range(350)])

        qsL.arrange(RIGHT)
        qsL.next_to([-dx * 4, 0, 0])
        qsI.arrange(RIGHT)
        qsI.next_to([-dx * 4, 0, 0])
        qsI.shift(DOWN)

        LOOP = CurvedArrow(
            qsL[-1].get_center() + 0.30 * UP, qsL[0].get_center() + 0.30 * UP
        )
        # thickness=.1)

        LOOP.set_color(color=PURPLE_B)  # rgba_to_color(cmap(.25)))
        qsL.add(LOOP)

        self.play(
            self.camera.frame.animate.move_to(qsL[0].get_center()),
            Write(qsL[0]),
        )

        self.play(
            Write(qsL[1:-1]),
            self.camera.frame.animate.move_to(qsL[-2].get_center()),
            run_time=3,
        )

        self.wait()
        self.play(
            Write(qsL[-1]),
            self.camera.frame.animate.move_to(qsL[0].get_center()),
            run_time=3,
        )

        self.wait()
        self.play(
            self.camera.frame.animate.move_to(qsI[0].get_center()),
            Write(qsI[0]),
        )

        self.play(
            Write(qsI[1:]),
            self.camera.frame.animate.move_to(qsI[150].get_center()),
            run_time=3,
        )

        self.wait()
        self.play(
            self.camera.frame.animate.move_to(qsI[0].get_center()),
            run_time=3,
        )

        self.play(
            self.camera.frame.animate.move_to(NODEG.get_center() + OUT * D),
            # clear out infinite loops and negative loops (prep for coral)
            FadeOut(qsI),
            FadeOut(qsL),
            *[FadeOut(a) for a in NLOOPS],
            *[FadeOut(a) for a in LLOOPS],
            *[FadeOut(a) for a in ALOOPS],
        )

        self.wait()

        # -----------------------------------------------------------------
        # -------- Coral
        # (fade out negative and breaking loops)
        # 5. Convert the tree into a coral and explain how to do that
        # -----------------------------------------------------------------

        # # positive angles >>> CCW,
        # # negative angles >>> CW... like trig class!
        # # even numbers dominate the initial expansion

        # # rotation angle for an even Collatz number, in degrees
        dtheta_even = -8

        # # rotation angle for an odd Collatz number, in degrees
        dtheta_odd = 20

        # step length
        step_length = 0.75

        self.play(
            FadeOut(LOOP_421),
            self.camera.frame.animate.move_to(NODES[1].get_center() + IN * 8),
            run_time=5,
        )  # 203

        def rotate_anim(ROT_NODE, CTR_NODE, ANGLE):
            return ROT_NODE.animate.rotate(
                ANGLE, about_point=CTR_NODE.get_center(), works_on_bounding_box=True
            )

        def nodes_above(A):

            edges = list(nx.edge_dfs(G, A, orientation="reverse"))

            if len(edges) == 0:
                return []

            # above =  [edges[0][0], edges[0][1]]
            # above += [e[0] for e in edges]
            above = [e[0] for e in edges]

            return above

        def rotate_above(C, angle):
            """rotate every node above `C` around `C` by `angle`"""

            above = nodes_above(C.cval)

            anims = []
            for n in above:

                a = C.cval
                b = nx.shortest_path(G, source=n, target=a)

                if n == a or len(b) == 0:
                    continue

                b = b[-2]

                c = list(G.successors(C.cval))

                if len(c) == 0:
                    # only 1 hasn't a successor
                    undo = 0
                else:
                    c = c[0]
                    undo = (
                        EDGES[f"{a}<--{b}"].get_angle()
                        - EDGES[f"{c}<--{a}"].get_angle()
                    )
                    # undo = EDGES[f"{a}<--{b}"].get_angle() - EDGES[f"{c}<--{a}"].get_angle()

                # self.embed()

                temp = NODES[n].copy()
                temp.rotate(angle - undo, about_point=C.get_center())

                D = nx.shortest_path_length(G, n, C.cval)

                v = normalize(temp.get_center() - C.get_center()) * step_length * D
                v += C.get_center()
                self.remove(temp)

                anims += [NODES[n].animate.move_to(v)]
                # anims += [rotate_anim(NODES[n], C, angle - undo)]

            return anims

        already_rotated = []

        # TUTORIAL of what CORAL does
        # GOTO CORAL

        for n1 in [1, 2]:  # nodes_above(1)[1:]:

            if n1 in already_rotated:
                continue

            already_rotated += [n1]

            n0 = list(G.predecessors(n1))

            if len(n0) == 0:
                continue
            else:
                n0 = n0[0]

            if (n1 % 2) == 0:
                dtheta = dtheta_even
            else:
                dtheta = dtheta_odd

            edge = EDGES[f"{n1}<--{n0}"]

            ref_line = Line(edge.get_start(), edge.get_start() + edge.get_unit_vector())

            ref_arc = ArcBetweenPoints(ORIGIN, ORIGIN + RIGHT)

            f_always(
                ref_arc.put_start_and_end_on,
                lambda: ref_line.get_center(),
                lambda: EDGES[f"{n1}<--{n0}"].get_center(),
            )

            self.play(
                Write(ref_line),
            )

            self.add(ref_arc)

            if n1 == 2:
                ref_arc.flip()

            self.play(
                *rotate_above(NODES[n1], dtheta * DEGREES),
            )

            if n1 == 1:
                ref_tex = Tex(f"{dtheta_odd}^{{\\circ}}")
                ref_tex.set_stroke(BLACK, width=0.3)
                ref_tex.scale(0.5)
                ref_tex.move_to(ref_arc.point_from_proportion(0.5) * 1.5)

            elif n1 == 2:
                ref_tex = Tex(f"{dtheta_even}^{{\\circ}}")
                ref_tex.scale(0.5)
                # ref_tex.move_to(ref_arc.point_from_proportion(1)*1.5)
                ref_tex.next_to(ref_arc, RIGHT)

            self.play(FadeIn(ref_tex, scale=2))

            self.wait()

            to = n0 if (n1 != 2) else n1

            self.play(
                FadeOut(ref_arc),
                FadeOut(ref_line),
                FadeOut(ref_tex),
                self.camera.frame.animate.move_to(NODES[n0].get_center() + IN * 8),
            )

            # else:
            #
            #     self.play(
            #                 *rotate_above(NODES[n1], dtheta*DEGREES),
            #                 self.camera.frame.animate.move_to(NODES[n0].get_center()),
            #     )

        anims = []

        self.play(
            self.camera.frame.animate.move_to(NODES[1].get_center() + OUT * D + UP * 5)
        )

        successors = [e[0] for e in nx.edge_bfs(G, source=2, orientation="reverse")]
        print(successors)
        for n1 in sorted(nodes_above(1)):
            # for n1 in successors:
            if n1 in already_rotated:
                continue

            already_rotated += [n1]

            if (n1 % 2) == 0:
                dtheta = dtheta_even
            else:
                dtheta = dtheta_odd

            print("... propagating coral from", n1)
            anims = rotate_above(NODES[n1], dtheta * DEGREES)
            if len(anims):
                self.play(*anims, run_time=1.0)

        # self.wait()
        # self.play()

        # 344

        params = {
            "numbers": range(1, 1024 + 1),
            # line segment length
            "dl": step_length,
            # line orientation of the starting point/root point (i.e. 1)
            "theta0": 90,  # +90+45
            # rotation angle for an even Collatz number, in degrees
            "dtheta_even": dtheta_even,
            # rotation angle for an odd Collatz number, in degrees
            "dtheta_odd": dtheta_odd,
        }

        try:
            C = grow_coral(params)

        except Exception as e:
            print(e)
            self.embed()

        self.play(
            FadeOut(NODEG),
            FadeOut(EDGEG),
            self.camera.frame.animate.shift(OUT * 2 * 4),
        )

        # self.play(self.camera.frame.animate.move_to(NODES[1].get_center()+OUT*D+UP*5+RIGHT*3+DOWN*2))

        # last = []
        corals = VGroup()

        for v in C:

            if v in already_rotated:
                continue

            C[v][:, 2] = 0
            c = Coraline(*C[v], color=cmap(random.random()))
            corals.add(c)

        self.play(
            ShowCreation(corals),
            self.camera.frame.animate.shift(OUT * 2 * 4 * 9 + UP * 5),
            lag_ratio=7.5,
            run_time=30,
        )

        self.embed()


class TREE_BROLL(Scene):
    def construct(self):

        ax = Axes(x_range=[-600, 600], y_range=[0, 500], include_tip=False)

        cmap_ = cm.get_cmap("YlGnBu")
        cmap = lambda x: cmap_(1 - 0.75 * (x) ** 0.25)

        D = 17

        # 2. Build tree to depth
        print(">>> DEPTH:", D)

        G, P = build_collatz_tree(D)
        Pmax = max(P)

        root = ax.c2p(*P[1])

        ANIMS = []
        NODES = {}
        EDGES = {}

        for p in P:
            n = Node(
                p,
                # color = METAL_COLOR,
                color=rgba_to_color(cmap((p / Pmax))),
                stroke_width=0,  # max(min(6, 12/len(P)), .01),
            )
            n._move_to = ax.c2p(*P[p]) - root
            n.move_to(n._move_to)

            NODES[p] = n

        for e in G.edges():

            s = f"{e[1]}<--{e[0]}"

            if s in EDGES:
                continue

            else:

                a = Line(NODES[e[1]], NODES[e[0]], color=WHITE)
                # a.set_opacity(.1)
                a._a0 = e[1]
                a._a1 = e[0]

                def keep(m):
                    m.set_points_by_ends(
                        NODES[m._a0].get_center(),
                        NODES[m._a1].get_center(),
                    )

                a.add_updater(keep)

                ANIMS = [FadeIn(a)] + ANIMS

                EDGES[s] = a
                EDGES[s].set_stroke(color=rgba_to_color(cmap(e[0] / Pmax)))

        EDGEG = VGroup(*EDGES.values())
        NODEG = VGroup(*NODES.values())

        for anim in ANIMS:
            anim.rate_func = rush_into

        # add the bring to back updater for all lines now that everythings visible

        RUN_TIME = 30

        # ------
        self.camera.frame.move_to(NODEG.get_center() + OUT * (D))
        EDGEG.add_updater(lambda m: self.bring_to_back(m))

        self.play(
            Write(NODEG),
            *ANIMS,
            self.camera.frame.animate.move_to(NODEG.get_center() + OUT * (D - 1)),
            lag_ratio=0.5,
            run_time=RUN_TIME,
        )

        EDGEG.clear_updaters()

        self.wait()

        # self.clear()

        # ------
        self.camera.frame.move_to(NODES[Pmax].get_center() + IN * 8)
        EDGEG.add_updater(lambda m: self.bring_to_back(m))

        self.play(
            Write(NODEG),
            *ANIMS,
            self.camera.frame.animate.move_to(NODEG.get_center() + OUT * (D)),
            lag_ratio=0.5,
            run_time=RUN_TIME,
        )

        EDGEG.clear_updaters()

        self.wait()

        # ------
        self.camera.frame.move_to(NODES[1].get_center() + IN * 8)

        self.play(
            self.camera.frame.animate.move_to(NODEG.get_center() + OUT * (D)),
            lag_ratio=0.5,
            run_time=RUN_TIME,
        )

        self.play(
            self.camera.frame.animate.move_to(
                NODES[Pmax].get_center() + IN * 4 + RIGHT * 4 + DOWN * 2
            ),
            run_time=RUN_TIME,
        )
        self.play(
            self.camera.frame.animate.move_to(
                NODES[3072].get_center() + IN * 4 + LEFT * 4 + DOWN * 2
            ),
            run_time=RUN_TIME,
        )

        self.embed()
