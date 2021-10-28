from itertools import product
from manimlib import *
import colorsys
from numpy import ndarray


class JLine3D(Prism):
    CONFIG = {"width": 0.05, "resolution": (21, 25)}

    def __init__(self, start, end, **kwargs):
        digest_config(self, kwargs)
        axis = end - start
        super().__init__(height=get_norm(axis), radius=self.width / 2, axis=axis)
        self.shift((start + end) / 2)


def xor(tup_a, tup_b):
    return tuple(a ^ b for a, b in zip(tup_a, tup_b))


def scale_lightness(rgb, scale_l):

    if isinstance(rgb, str):
        rgb = hex_to_rgb(rgb)
    # convert rgb to hls
    h, l, s = colorsys.rgb_to_hls(*rgb)
    # manipulate h, l, s values and return as rgb
    return rgb_to_hex(colorsys.hls_to_rgb(h, min(1, l * scale_l), s=s))


class JPrism(Group):
    def __init__(self, dimensions=[1, 2, 3], fill_color=BLUE, stroke_color=BLACK):
        self.prism = Prism(dimensions=dimensions).set_color(fill_color)

        vertices = list(product([0, 1], repeat=3))

        edges = []

        for v1 in vertices:
            for v2 in vertices:
                if v1 != v2 and sum(xor(v1, v2)) < 2:

                    l = (
                        Line3D(
                            start=self.prism.get_corner(np.array(v1)),
                            end=self.prism.get_corner(np.array(v2)),
                            width=0.002,
                            gloss=-1,
                        )
                        .set_color(
                            scale_lightness(fill_color, 0.3)
                            if stroke_color is None
                            else stroke_color
                        )
                        .set_gloss(-1, recurse=True)
                    )

                    edges.append(l)

        self.edges = Group(*edges)
        for dim, value in enumerate(self.prism.dimensions):
            self.edges.rescale_to_fit(value + 0.0050, dim, stretch=True)

        self.edges.move_to(self.prism.get_center())

        super().__init__(self.prism, *self.edges)


class JCube(JPrism):
    def __init__(self, side_length=2, fill_color=BLUE, stroke_color=BLACK):
        super().__init__(
            dimensions=[side_length, side_length, side_length],
            fill_color=fill_color,
            stroke_color=stroke_color,
        )


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
        **kwargs,
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


class RotatingAndMove(Animation):
    CONFIG = {
        "axis": OUT,
        "radians": TAU,
        "run_time": 2,
        "rate_func": smooth,
        "about_point": None,
        "about_edge": None,
    }

    def __init__(self, mobject, direction, **kwargs):
        assert isinstance(mobject, Mobject)
        digest_config(self, kwargs)
        self.mobject = mobject
        self.direction = direction

    def interpolate_mobject(self, alpha):
        self.mobject.become(self.starting_mobject)
        self.mobject.rotate(
            alpha * self.radians,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )
        self.mobject.shift(alpha * self.direction)


class RotatingAndMoveToTarget(Animation):
    CONFIG = {
        "axis": OUT,
        "radians": TAU,
        "run_time": 2,
        "rate_func": smooth,
        "about_point": None,
        "about_edge": None,
    }

    def __init__(
        self,
        mobject: Mobject,
        target: Mobject,
        direction: ndarray,
        # path: Mobject = None,
        aligned_edge=ORIGIN,
        buff=0,
        coor_mask=np.array([1, 1, 1]),
        **kwargs,
    ):
        assert isinstance(mobject, Mobject)
        digest_config(self, kwargs)
        self.mobject = mobject
        self.target = target
        self.direction = direction
        self.buff = buff
        self.aligned_edge = aligned_edge
        self.coor_mask = coor_mask
        # if path is None:
        #     self.path = Line(mobject.get_center(), target.get_center())
        # else:
        #     self.path = path

    def interpolate_mobject(self, alpha):
        self.mobject.become(self.starting_mobject)
        self.mobject.rotate(
            alpha * self.radians,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )
        if isinstance(self.target, Mobject):
            mob = self.target
            target_point = mob.get_bounding_box_point(
                self.aligned_edge + self.direction
            )

        aligner = self.mobject
        point_to_align = aligner.get_bounding_box_point(
            self.aligned_edge - self.direction
        )

        # next_point = self.path.point_from_proportion(alpha)

        # if alpha < 0.8:
        #     self.mobject.move_to(next_point)
        # else:
        self.mobject.shift(
            (target_point - point_to_align + self.buff * self.direction)
            * self.coor_mask
            * alpha
        )


# scenes
class _17_CubicExplanation(ThreeDScene):
    def construct(self):

        frame = self.camera.frame
        frame.set_euler_angles(
            theta=-45 * DEGREES,
            phi=70 * DEGREES,
        )

        # x^3 + 9x = 26 -> x = 2, y = 1

        general_opacity = 1

        x = 2
        y = 1
        z = x + y
        x_cube = JCube(side_length=x, fill_color=PURPLE).shift(ORIGIN)
        y_cube = JCube(side_length=y, fill_color=YELLOW_D).next_to(
            x_cube, DOWN + OUT + LEFT, buff=0
        )

        z_cube_og = (
            JCube(side_length=z, fill_color=RED_C)
            .next_to(x_cube, buff=0, aligned_edge=IN + UP + LEFT, coor_mask=[0, 1, 1])
            .shift(LEFT * y / 2)
            .shift(IN * 0.02)  # to avoid glitches
        )

        # x, y, y prisms
        ####################################################
        x_y_y = (
            JPrism(dimensions=[x, y, y], fill_color=GREEN).next_to(
                x_cube, OUT + DOWN, buff=0
            )
        ).set_opacity(general_opacity)

        x_y_y_1 = (
            (JPrism(dimensions=[x, y, y], fill_color=GREEN))
            .rotate(PI / 2, Z_AXIS)
            .next_to(x_cube, OUT + LEFT, buff=0)
        ).set_opacity(general_opacity)

        x_y_y_2 = (
            JPrism(dimensions=[y, y, x], fill_color=GREEN)
            .rotate(0)
            .next_to(x_cube, LEFT + DOWN, buff=0)
        ).set_opacity(general_opacity)

        # x, x, y prisms
        ####################################################
        x_x_y = (
            JPrism(dimensions=[x, x, y], fill_color=BLUE_D)
            .next_to(x_cube, OUT, buff=0)
            .set_opacity(general_opacity)
        )
        x_x_y_1 = (
            JPrism(dimensions=[x, x, y], fill_color=BLUE_D)
            .rotate(PI / 2, Y_AXIS)
            .next_to(x_cube, LEFT, buff=0)
        ).set_opacity(general_opacity)

        x_x_y_2 = (
            JPrism(dimensions=[x, x, y], fill_color=BLUE_D)
            .rotate(PI / 2, X_AXIS)
            .next_to(x_cube, DOWN, buff=0)
        ).set_opacity(general_opacity)

        # begin animations
        ####################################################

        self.wait(1)
        self.play(FadeIn(x_cube))

        def create_three_axis_brace(
            mobject: Mobject, color, width_tag, height_tag, depth_tag, stroke_w=1.2
        ):
            rot_mob = mobject.copy().rotate(PI / 2, X_AXIS)
            braces = [
                Brace(mobject, DOWN).next_to(IN, coor_mask=[0, 0, 1]).set_color(color),
                Brace(mobject, LEFT)
                .set_color(color)
                .shift(IN * mobject.get_height() / 2)
                .next_to(IN, coor_mask=[0, 0, 1]),
                Brace(rot_mob, LEFT)
                .set_color(color)
                .rotate(PI / 2 - 0.0001, X_AXIS)
                .next_to(mobject, LEFT)
                .shift(UP * mobject.get_height() / 2),
            ]

            w_tag = Tex(str(width_tag)).set_color(color)
            h_tag = Tex(str(height_tag)).set_color(color)
            d_tag = Tex(str(depth_tag)).set_color(color)
            tags = [
                w_tag.copy().next_to(braces[0], DOWN),
                h_tag.copy().next_to(braces[1], LEFT),
                d_tag.copy().next_to(braces[2], LEFT).rotate(PI / 2 - 0.0001, X_AXIS)
                # .shift(UP * mobject.get_depth() / 2 + OUT * mobject.get_height() / 2),
            ]

            [b.set_stroke(width=stroke_w) for b in braces]
            [b.set_stroke(width=stroke_w) for b in tags]

            return braces, tags

        braces, exes = create_three_axis_brace(x_cube, PURPLE, "x", "x", "x")

        self.wait(2)
        self.play(*[Write(b) for b in braces], *[Write(a) for a in exes], run_time=2)

        self.wait(10)
        self.play(
            *[FadeOut(b) for b in braces], *[FadeOut(a) for a in exes], run_time=1.5
        )

        def create_dashed_line(direction, length):
            return DashedLine(
                x_cube.get_corner(direction),
                x_cube.get_corner(direction) + length,
            ).set_stroke(BLACK, width=6)

        w_dlines = [
            create_dashed_line(OUT + UP + RIGHT, OUT * y),
            create_dashed_line(OUT + UP + LEFT, LEFT * y),
            create_dashed_line(IN + DOWN + RIGHT, DOWN * y),
        ]

        self.play(*[Write(a) for a in w_dlines])

        y_t = (
            Tex("y")
            .set_color(BLACK)
            .set_stroke(width=0.7)
            .rotate(PI / 2 - 0.0001, X_AXIS)
            .rotate(-PI / 4, Z_AXIS)
        )

        y_arr = [
            y_t.copy().next_to(w_dlines[0], DOWN),
            y_t.copy().next_to(w_dlines[1], OUT),
            y_t.copy().next_to(w_dlines[2], OUT),
        ]

        self.play(*[Write(a) for a in y_arr], run_time=2)

        self.wait(8)

        # option 1
        z_cube = x_cube.copy()
        self.play(
            Transform(z_cube, z_cube_og),
            *[FadeOut(a) for a in w_dlines],
            *[FadeOut(a) for a in y_arr],
            run_time=3,
        )

        braces_z, zetas = create_three_axis_brace(z_cube, RED_C, "z", "z", "z")
        self.play(*[Write(b) for b in braces_z], *[Write(a) for a in zetas], run_time=2)

        self.wait(10)

        self.play(
            *[FadeOut(b) for b in braces_z], *[FadeOut(a) for a in zetas], run_time=1.5
        )

        # draw lines on z cube

        def create_z_cube_og_lines(corner1, corner2, shift_direction, color):
            corner1 = z_cube_og.get_corner(corner1) + shift_direction * y
            corner2 = z_cube_og.get_corner(corner2) + shift_direction * y
            return Line(corner1, corner2).set_stroke(color, width=3)

        slice_lines = [
            # down face
            create_z_cube_og_lines(OUT + DOWN + LEFT, OUT + DOWN + RIGHT, IN, GREEN),
            create_z_cube_og_lines(OUT + DOWN + LEFT, IN + DOWN + LEFT, RIGHT, GREEN),
            # left face
            create_z_cube_og_lines(OUT + DOWN + LEFT, OUT + UP + LEFT, IN, GREEN),
            create_z_cube_og_lines(OUT + DOWN + LEFT, IN + DOWN + LEFT, UP, GREEN),
            # out face
            create_z_cube_og_lines(OUT + DOWN + LEFT, OUT + UP + LEFT, RIGHT, GREEN),
            create_z_cube_og_lines(OUT + DOWN + LEFT, OUT + DOWN + RIGHT, UP, GREEN),
        ]

        self.play(*[Write(a) for a in slice_lines], run_time=2)
        self.wait(5)

        self.play(
            *[FadeOut(a) for a in slice_lines],
            FadeOut(z_cube),
            FadeIn(x_y_y),
            FadeIn(x_y_y_1),
            FadeIn(x_y_y_2),
            FadeIn(x_x_y),
            FadeIn(x_x_y_1),
            FadeIn(x_x_y_2),
            FadeIn(y_cube),
            run_time=3,
        )

        # explode!

        self.wait(4)
        self.play(
            LaggedStart(
                x_x_y.animate.shift(OUT * 1.2),
                x_x_y_1.animate.shift(LEFT * 1.2),
                x_x_y_2.animate.shift(DOWN * 1.2),
            ),
            run_time=2,
        )

        braces_xxy, tags_xxy = create_three_axis_brace(x_x_y_1, BLUE_D, "y", "x", "x")

        self.play(
            *[Write(b) for b in braces_xxy], *[Write(a) for a in tags_xxy], run_time=2
        )

        self.wait(10)

        self.play(
            LaggedStart(
                x_y_y.animate.shift(DOWN + OUT),
                x_y_y_1.animate.shift(LEFT + OUT),
                x_y_y_2.animate.shift(LEFT + DOWN),
            ),
            run_time=2,
        )
        braces_xyy, tags_xyy = create_three_axis_brace(x_y_y_2, GREEN, "y", "y", "x")

        braces_xyy[0].next_to(IN, coor_mask=[0, 0, 1])

        self.play(
            *[Write(b) for b in braces_xyy], *[Write(a) for a in tags_xyy], run_time=2
        )

        self.wait(10)

        self.play(y_cube.animate.shift(DOWN + LEFT + OUT))

        braces_y, tex_y = create_three_axis_brace(y_cube, YELLOW_D, "y", "y", "y")

        braces_y[1].next_to(y_cube, LEFT, buff=1, coor_mask=[0, 1, 1]).shift(IN * y / 2)
        braces_y[0].next_to(y_cube, DOWN, buff=0.01).shift(IN * y / 2)
        tex_y[0].next_to(braces_y[0], DOWN)
        tex_y[1].next_to(braces_y[1], LEFT)

        self.play(*[Write(b) for b in braces_y], *[Write(a) for a in tex_y], run_time=2)

        self.wait(10)

        # construction of 6x
        self.play(
            *[FadeOut(b) for b in braces_y],
            *[FadeOut(a) for a in tex_y],
            *[FadeOut(b) for b in braces_xyy],
            *[FadeOut(a) for a in tags_xyy],
            *[FadeOut(b) for b in braces_xxy],
            *[FadeOut(a) for a in tags_xxy],
        )

        self.play(
            LaggedStart(
                FadeOut(y_cube),
                frame.animate.shift(LEFT * 5),
            ),
            run_time=5,
        )
        self.wait(3)

        ref_cube = JCube().shift(LEFT * 4)

        self.play(
            LaggedStart(
                # BLUE ONES
                RotatingAndMoveToTarget(
                    x_x_y_1,
                    ref_cube.copy().shift(LEFT * 3),
                    LEFT,
                    radians=0,
                    axis=Y_AXIS,
                ),
                RotatingAndMoveToTarget(
                    x_x_y,
                    x_x_y_1,
                    RIGHT,
                    radians=-PI / 2,
                    axis=Y_AXIS,
                ),
                RotatingAndMoveToTarget(
                    x_x_y_2, x_x_y, RIGHT, radians=PI / 2, axis=Z_AXIS
                ),
                # GREEN ONES
                RotatingAndMoveToTarget(x_y_y_2, x_x_y_1, DOWN, radians=0, axis=Y_AXIS),
                RotatingAndMoveToTarget(
                    x_y_y_1, x_y_y_2, RIGHT, radians=PI / 2, axis=X_AXIS
                ),
                RotatingAndMoveToTarget(
                    x_y_y, x_y_y_1, RIGHT, radians=PI / 2, axis=Y_AXIS
                ),
                lag_ratio=0.2,
                run_time=7,
            )
        )

        # annotation of the measurements
        g_3y = Group(x_y_y, x_y_y_1, x_y_y_2)

        brace_3y = Brace(g_3y).set_color(GREEN).shift(IN * x / 2)
        threey_t = (
            Tex("3y").set_color(GREEN).set_stroke(width=0.7).next_to(brace_3y, DOWN)
        )

        y_t = (
            Tex("y")
            .set_color(GREEN)
            .set_stroke(width=0.7)
            .next_to(x_y_y_2, LEFT)
            .shift(IN * x / 2)
        )

        x_t = (
            Tex("x")
            .set_color(BLUE_C)
            .set_stroke(width=0.7)
            .next_to(x_x_y_1, LEFT)
            .shift(IN * x / 2)
        )

        vg_x_y = VGroup(x_t, y_t)
        brace_z = Brace(vg_x_y, LEFT).set_color(RED_C)
        z_t = Tex("z").set_color(RED_C).set_stroke(width=1).next_to(brace_z, LEFT)

        brace_x_1 = (
            Brace(x_x_y_1, direction=LEFT)
            .set_color(BLUE_D)
            .set_stroke(width=0.7)
            .rotate(PI / 2 - 0.0001, X_AXIS)
            .shift(UP * x / 2)
        )

        x_t_1 = x_t.copy().next_to(brace_x_1, LEFT).rotate(PI / 2 - 0.0001, X_AXIS)

        self.play(Write(brace_3y), Write(threey_t), run_time=2)
        self.wait()
        self.play(Write(y_t), run_time=2)
        self.wait()
        self.play(Write(x_t), run_time=2)
        self.wait()
        self.play(Write(brace_z), Write(z_t), run_time=2)
        self.wait()
        self.play(Write(brace_x_1), Write(x_t_1), run_time=2)

        self.wait(10)

        self.play(
            LaggedStart(
                FadeOut(threey_t),
                FadeOut(brace_3y),
                FadeOut(y_t),
                FadeOut(x_t),
                FadeOut(z_t),
                FadeOut(brace_z),
                FadeOut(x_t_1),
                FadeOut(brace_x_1),
                lag_ratio=0.09,
            )
        )

        # come back
        self.play(
            frame.animate.shift(RIGHT * 8),
            # FadeIn(x_cube),
            LaggedStart(
                # 1º blue
                RotatingAndMoveToTarget(x_x_y_2, x_cube, LEFT, radians=0, axis=Y_AXIS),
                # 1º green
                RotatingAndMoveToTarget(
                    x_y_y, x_cube, LEFT + DOWN, radians=0, axis=Y_AXIS
                ),
                # 2º blue
                RotatingAndMoveToTarget(
                    x_x_y, x_cube, OUT, radians=PI / 2, axis=Y_AXIS
                ),
                # 2º green
                RotatingAndMoveToTarget(
                    x_y_y_1, x_cube, OUT + DOWN, radians=PI / 2, axis=Y_AXIS
                ),
                # 3º blue
                RotatingAndMoveToTarget(
                    x_x_y_1, x_cube, DOWN, radians=PI / 2, axis=Z_AXIS
                ),
                # 3º green
                RotatingAndMoveToTarget(
                    x_y_y_2, x_cube, OUT + LEFT, radians=-PI / 2, axis=X_AXIS
                ),
                lag_ratio=0.2,
            ),
            run_time=8,
        )

        self.wait(10)
        self.play(FadeIn(y_cube))

        y_cube.generate_target()
        y_cube.target.next_to(x_cube, DOWN + LEFT + OUT, buff=0)

        self.wait(2)
        self.play(MoveToTarget(y_cube), run_time=2, rate_func=smooth)

        self.wait(4)

        self.play(
            FadeOut(x_cube),
            FadeOut(x_x_y),
            FadeOut(x_x_y_1),
            FadeOut(x_x_y_2),
            FadeOut(x_y_y),
            FadeOut(x_y_y_1),
            FadeOut(x_y_y_2),
            FadeOut(y_cube),
            run_time=3,
        )

        # final scene

        z_cube_e = z_cube.copy()

        y_cube_e = y_cube.copy()

        self.play(frame.animate.shift(DOWN * 7 + LEFT * 6 + OUT * 3))
        self.play(FadeIn(z_cube_e.shift(LEFT * 3)), run_time=2)

        self.wait(4)
        self.play(FadeIn(y_cube_e.next_to(z_cube_e, DR, buff=6)), run_time=2)

        self.wait(5)


class Ass(ThreeDScene):
    def construct(self):

        frame = self.camera.frame
        frame.set_euler_angles(
            theta=-45 * DEGREES,
            phi=70 * DEGREES,
        )
        a = Cube(side_length=2)
        line = Line(
            a.get_corner(DOWN + LEFT + OUT), a.get_corner(DOWN + RIGHT + OUT)
        ).set_color(BLACK)

        b = Cube(side_length=2).next_to(a, DOWN, buff=0)
        line_b = Line(
            b.get_corner(UP + LEFT + OUT), b.get_corner(UP + RIGHT + OUT)
        ).set_color(BLACK)

        cube_vg_a = Group(a, line)
        cube_vg_b = Group(b, line_b)

        dot1 = (
            Sphere(radius=0.1).move_to(a.get_corner(UP + LEFT + OUT)).set_color(BLACK)
        )
        dot2 = Sphere(radius=0.1).move_to(a.get_edge_center(UP + OUT)).set_color(BLACK)

        # self.play(FadeIn(cube_vg_a))
        # self.play(FadeIn(cube_vg_b))

        xd = JPrism([1, 2, 3])
        self.play(FadeIn(xd))
        self.play(Rotating(xd))

        self.play(frame.animate.shift(IN * 30))
