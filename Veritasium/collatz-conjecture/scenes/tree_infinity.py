import networkx as nx
from manimlib import *
import random
import pickle

from networkx.drawing.nx_pydot import graphviz_layout
import networkx as nx

from matplotlib import cm

COLLATZ_RED = "#F23545"
COLLATZ_NAVY = "#010326"
COLLATZ_BLUE = "#1B21A6"
COLLATZ_SKY = "#2745F2"
COLLATZ_AQUA = "#6AD9D9"

METAL_COLOR = Color(hsl=(0.55, 0.075, 3 / 20))

COLLATZ_ODD = COLLATZ_RED
COLLATZ_EVEN = COLLATZ_AQUA


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


class _14_BuildTree_2(Scene):
    def construct(self):
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
        self.play(Write(ax))
        # self.add(ax)

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

        # for D in range(6, 18):
        for D in range(17, 18):

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
        # self.play(self.camera.frame.animate.shift(LEFT * 10))
        # self.play(self.camera.frame.animate.shift(RIGHT * 20))

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

        self.wait(5)
        self.play(self.camera.frame.animate.shift(RIGHT * 15), run_time=2)

        whole_tree = VGroup(*NODES.values(), *EDGES.values())

        uk_node = (
            Node("?")
            .next_to(whole_tree, RIGHT, buff=5)
            .set_stroke(PURPLE_B, width=2)
            .shift(DOWN * 7)
            .scale(1.5)
        )
        last_node = uk_node
        infinity_explosion = VGroup()

        # f(x) = (x - input_start) / (input_end - input_start) * (output_end - output_start) + output_start

        def map_num_range(x, input_start, input_end, output_start, output_end):
            return (x - input_start) / (input_end - input_start) * (
                output_end - output_start
            ) + output_start

        for i in range(1020):
            n = Node(i).set_stroke(PURPLE_B, width=3).next_to(last_node, UP, buff=0.3)
            l = Line(last_node, n, color=PURPLE_B)

            if i > 950:
                n.set_opacity(map_num_range(i, 950, 1015, 1, 0))
                l.set_opacity(map_num_range(i, 950, 1015, 1, 0))

            infinity_explosion.add(n)
            infinity_explosion.add(l)

            last_node = n

        self.play(Write(uk_node), run_time=0.5)
        self.wait()

        infinity_animation = Write(infinity_explosion)
        # infinity_animation.rate_func = rush_into

        camera_travelin = self.camera.frame.animate.shift(UP * 800)
        # camera_travelin.rate_func = smooth

        self.play(
            infinity_animation,
            camera_travelin,
            run_time=10,
            rate_func=rush_into,
            lag_ratio=0.5,
        )
        infinity_explosion.add(uk_node)

        self.wait(2)

        self.play(self.camera.frame.animate.shift(DOWN * 800))

        loop_uk_node = uk_node.copy().shift(RIGHT * 4)
        last_node = loop_uk_node
        huge_loop = VGroup()

        for i in range(100):
            n = last_node.copy().next_to(last_node, UP, buff=0.3)
            l = Line(last_node, n, color=PURPLE_B)

            huge_loop.add(n)
            huge_loop.add(l)

            last_node = n

        loop_arc = CurvedArrow(
            last_node.get_center() + RIGHT,
            loop_uk_node.get_center() + RIGHT,
            buff=0.08,
            angle=-PI / 10,
        ).set_color(PURPLE_B)

        self.play(infinity_explosion.animate.shift(LEFT), Write(loop_uk_node))
        self.wait()
        self.play(Write(huge_loop), run_time=1, rate_func=rush_into)
        self.play(Write(loop_arc))

        self.wait()

        self.play(self.camera.frame.animate.shift(OUT * 40))
        self.wait()
        self.play(self.camera.frame.animate.shift(UP * 100))
        self.wait()
        self.play(self.camera.frame.animate.shift(UP * -100 + IN * 40))
        self.wait()
