from inspect import trace
from operator import ge, ne
from typing import Optional
from typing_extensions import runtime
from manimlib import *
import numpy as np
from numpy import sqrt
import colorsys
from itertools import product


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


class TransformMatchingPartsJ(AnimationGroup):
    CONFIG = {
        "mobject_type": Mobject,
        "group_type": Group,
        "transform_mismatches": False,
        "fade_transform_mismatches": False,
        "fade_direction": ORIGIN,
        "key_map": dict(),
    }

    def __init__(self, mobject, target_mobject, **kwargs):
        digest_config(self, kwargs)
        assert isinstance(mobject, self.mobject_type)
        assert isinstance(target_mobject, self.mobject_type)
        source_map = self.get_shape_map(mobject)
        target_map = self.get_shape_map(target_mobject)

        # Create two mobjects whose submobjects all match each other
        # according to whatever keys are used for source_map and
        # target_map
        transform_source = self.group_type()
        transform_target = self.group_type()
        kwargs["final_alpha_value"] = 0
        for key in set(source_map).intersection(target_map):
            transform_source.add(source_map[key])
            transform_target.add(target_map[key])
        anims = [Transform(transform_source, transform_target, **kwargs)]
        # User can manually specify when one part should transform
        # into another despite not matching by using key_map
        key_mapped_source = self.group_type()
        key_mapped_target = self.group_type()
        for key1, key2 in self.key_map.items():
            if key1 in source_map and key2 in target_map:
                key_mapped_source.add(source_map[key1])
                key_mapped_target.add(target_map[key2])
                source_map.pop(key1, None)
                target_map.pop(key2, None)
        if len(key_mapped_source) > 0:
            anims.append(
                FadeTransform(
                    key_mapped_source,
                    key_mapped_target,
                )
            )

        fade_source = self.group_type()
        fade_target = self.group_type()
        for key in set(source_map).difference(target_map):
            fade_source.add(source_map[key])
        for key in set(target_map).difference(source_map):
            fade_target.add(target_map[key])

        if self.transform_mismatches:
            anims.append(Transform(fade_source.copy(), fade_target, **kwargs))
        if self.fade_transform_mismatches:
            anims.append(FadeTransformPieces(fade_source, fade_target, **kwargs))
        else:
            anims.append(FadeOut(fade_source, self.fade_direction, **kwargs))
            anims.append(FadeIn(fade_target.copy(), self.fade_direction, **kwargs))

        super().__init__(*anims)

        self.to_remove = mobject
        self.to_add = target_mobject

    def get_shape_map(self, mobject):
        shape_map = {}
        for sm in self.get_mobject_parts(mobject):
            key = self.get_mobject_key(sm)
            if key not in shape_map:
                shape_map[key] = VGroup()
            shape_map[key].add(sm)
        return shape_map

    def clean_up_from_scene(self, scene):
        for anim in self.animations:
            anim.update(0)
        scene.remove(self.mobject)
        scene.remove(self.to_remove)
        scene.add(self.to_add)

    @staticmethod
    def get_mobject_parts(mobject):
        # To be implemented in subclass
        return mobject

    @staticmethod
    def get_mobject_key(mobject):
        # To be implemented in subclass
        return hash(mobject)


class TransformMatchingTexJ(TransformMatchingPartsJ):
    CONFIG = {
        "mobject_type": VMobject,
        "group_type": VGroup,
    }

    @staticmethod
    def get_mobject_parts(mobject):
        return mobject.submobjects

    @staticmethod
    def get_mobject_key(mobject):
        return mobject.get_tex()


class TransformMatchingShapesJ(TransformMatchingPartsJ):
    CONFIG = {
        "mobject_type": VMobject,
        "group_type": VGroup,
    }

    @staticmethod
    def get_mobject_parts(mobject):
        return mobject.family_members_with_points()

    @staticmethod
    def get_mobject_key(mobject):
        mobject.save_state()
        mobject.center()
        mobject.set_height(1)
        result = hash(np.round(mobject.get_points(), 3).tobytes())
        mobject.restore()
        return result


class _17_IntroToCubic(Scene):
    def construct(self):
        original_equation = (
            Tex(R"x", "^3", "+9x = 26").set_color(BLACK).scale(3).shift(UP * 1.5)
        )
        cube = (
            Cube(side_length=1)
            .set_color(PURPLE)
            .rotate(-PI / 5, Y_AXIS)
            .rotate(PI / 9, X_AXIS)
            .next_to(original_equation[0:2], DOWN, buff=1)
        )

        blob = (
            Prism(dimensions=[2, 1, 1])
            .set_color(BLUE)
            .rotate(-PI / 5, Y_AXIS)
            .rotate(PI / 9, X_AXIS)
            .next_to(original_equation[3:5], DOWN, buff=0.1)
            # .shift(UP * 0.5)
        )

        self.wait(1)

        self.play(FadeIn(original_equation), run_time=2)

        self.wait(2)

        self.play(FadeIn(cube), run_time=2)

        self.wait(2)

        self.play(FadeIn(blob), run_time=2)

        self.wait(2)


class _19_NumbersAndBlocks(Scene):
    def construct(self):

        x = 2
        y = 1
        z = x + y
        general_opacity = 1
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

        # ORIGINAL EQUATION
        original_equation = (
            Tex(R"z^3", "= 26 +", "y^3").set_color(BLACK).scale(3).shift(UP * 2.3)
        )

        full_cube = (
            Group(
                x_cube, y_cube.copy(), x_x_y, x_x_y_1, x_x_y_2, x_y_y, x_y_y_1, x_y_y_2
            )
            .rotate(PI / 4, Z_AXIS)
            .rotate(-PI / 3, X_AXIS)
            .scale(0.8)
            .next_to(original_equation[0], DOWN, buff=1)
        )

        y_cube_eq = (
            y_cube.copy()
            .set_color(YELLOW_D)
            .rotate(-PI / 5, Y_AXIS)
            .rotate(PI / 9, X_AXIS)
            .scale(0.8)
            .next_to(original_equation[-1], DOWN, buff=1.5)
        )

        self.wait(1)

        self.play(FadeIn(original_equation), run_time=2)

        self.wait(2)

        self.play(FadeIn(full_cube), run_time=2)

        self.wait(2)

        self.play(FadeIn(y_cube_eq), run_time=2)

        self.wait(2)


class _20_CubicFormulas(Scene):
    def construct(self):
        step_1 = Tex("3yz = 9").set_color(BLACK)
        step_2 = Tex("yz = 3").set_color(BLACK)
        step_3 = Tex(R"z = \frac{3}{y}").set_color(BLACK)
        page_1 = VGroup(step_1, step_2, step_3).arrange(DOWN, buff=0.3).scale(2)

        # page 1
        time = 4
        for eq in page_1:
            self.play(FadeIn(eq))
            self.wait(time)

        self.play(FadeOut(page_1))
        self.wait(3)

        # page 2
        step_1 = Tex(R"\frac{3}{y}^3 - y^3 = 26").set_color(BLACK)
        step_2 = Tex(R"\frac{27}{y^3} - y^3 = 26").set_color(BLACK)
        step_3 = Tex(R"27 - y^6 = 26y^3").set_color(BLACK)
        page_2 = VGroup(step_1, step_2, step_3).arrange(DOWN, buff=0.6).scale(1.4)

        for eq in page_2:
            self.play(FadeIn(eq))
            self.wait(time)

        self.play(FadeOut(page_2))
        self.wait(3)

        # page 3
        step_1 = Tex(R"y^6 + 26y^3 = 27").set_color(BLACK)
        step_2 = Tex(R"(y^3)^2 + 26(y^3) = 27").set_color(BLACK).scale(1.3)

        page_3 = VGroup(step_1, step_2).arrange(DOWN, buff=0.6).scale(2)

        for eq in page_3:
            self.play(FadeIn(eq))
            self.wait(time * 2)

        self.play(FadeOut(page_3))
        self.wait(3)


class _NO__(Scene):
    def construct(self):
        time = 3
        original_equation = Tex(R"x", "^3", "+9x = 26", isolate=["26"]).set_color(BLACK)

        z_equals_yx = Tex("z", "=", "x", "+", "y").set_color(BLACK).scale(1)

        three_yz = Tex("3", "y", "z", "= 9").set_color(BLACK).scale(1)

        z_3_minus_y_3 = Tex("z^3", "-", "y^3", "=", "26").set_color(BLACK).scale(1)

        extract_z_2 = (
            Tex(
                R"y",
                "z",
                "=",
                "3",
            ).set_color(BLACK)
        ).scale(1)

        extract_z_3 = (
            Tex(
                "z",
                "=",
                R"\frac{3}{",
                "y",
                "}",
            ).set_color(BLACK)
        ).scale(1)

        ################################################

        ################################################
        plug_z_1 = (
            Tex(
                R"\bigg(\frac{3}{",
                "y",
                R"}\bigg)^3",
                "-",
                "y^3",
                "=",
                "26",
            )
            .set_color(BLACK)
            .scale(3)
        )

        plug_z_2 = (
            Tex(
                R"\frac{27}{",
                "y",
                "^3}",
                "-",
                "y^3",
                "=",
                "26",
            )
            .set_color(BLACK)
            .scale(2)
        )

        plug_z_3 = (
            Tex(
                R"27",
                "-",
                "y^6",
                "=",
                "26",
                "y^3",
            )
            .set_color(BLACK)
            .scale(2)
        )

        plug_z_4 = Tex(R"y^6", "+", "26", "y^3", "=", "27").set_color(BLACK).scale(2.5)

        plug_z_5 = (
            Tex(R"(y^3)^2", "+", "26", "(y^3)", "=", "27").set_color(BLACK).scale(2.5)
        )

        ################################################

        ################################################
        find_y_1 = (
            Tex(
                R"(",
                "y^3",
                "+",
                "13",
                ")^2",
                "=",
                "27+169",
                isolate=["y"],
            )
            .set_color(BLACK)
            .scale(2.5)
        )

        find_y_2 = (
            Tex(
                R"(",
                "y^3",
                "+",
                "13",
                ")^2",
                "=",
                "196",
                isolate=["y"],
            )
            .set_color(BLACK)
            .scale(2.5)
        )

        find_y_3 = (
            Tex(
                R"y^3",
                "+",
                "13",
                "=",
                "14",
                isolate=["y"],
            )
            .set_color(BLACK)
            .scale(2.5)
        )

        find_y_4 = (
            Tex(
                R"y^3",
                "=",
                "1",
                isolate=["y"],
            )
            .set_color(BLACK)
            .scale(2.5)
        )

        find_y_5 = (
            Tex(
                R"y",
                "=",
                "1",
                isolate=["y"],
            )
            .set_color(BLACK)
            .scale(2.5)
        )
        ##########################

        ##########################
        find_z_2 = (
            Tex(
                R"z^3",
                "-",
                "1",
                "=",
                "26",
            )
            .set_color(BLACK)
            .scale(3)
        )

        find_z_3 = (
            Tex(
                R"z^3",
                "=",
                "27",
            )
            .set_color(BLACK)
            .scale(3)
        )

        find_z_4 = (
            Tex(
                R"z",
                "=",
                "3",
            )
            .set_color(BLACK)
            .scale(3)
        )
        ##########################

        find_x_1 = Tex("x", "=", "z", "-", "y").set_color(BLACK).scale(3)

        find_x_2 = Tex("x", "=", "3", "-", "1").set_color(BLACK).scale(3)

        find_x_3 = Tex("x", "=", "2").set_color(BLACK).scale(3)

        time = 3

        self.play(Write(three_yz.shift(UP * 2)))
        self.wait(time)
        self.play(Write(z_3_minus_y_3.next_to(three_yz, DOWN, buff=1)))
        self.wait(time)
        self.play(FadeOut(z_3_minus_y_3), three_yz.animate.shift(DOWN * 2))
        self.wait(time)
        self.play(TransformMatchingTexJ(three_yz, extract_z_2), run_time=2)
        self.wait(time)
        self.play(TransformMatchingTexJ(extract_z_2, extract_z_3), run_time=2)
        self.wait(time)

        extract_z_3_corner = extract_z_3.copy().scale(0.2).to_corner(UL)
        self.play(Transform(extract_z_3, extract_z_3_corner))

        self.wait(time)

        self.play(Write(z_3_minus_y_3), run_time=2)
        self.wait(time)
        self.play(TransformMatchingTexJ(z_3_minus_y_3, plug_z_1), run_time=2)
        self.wait(time)
        self.play(TransformMatchingTexJ(plug_z_1, plug_z_2), run_time=2)
        self.wait(time)
        self.play(TransformMatchingTexJ(plug_z_2, plug_z_3), run_time=2)
        self.wait(time)
        self.play(
            TransformMatchingTexJ(plug_z_3, plug_z_4, key_map={"-": "+"}), run_time=2
        )
        self.wait(time * 2)
        self.play(TransformMatchingTexJ(plug_z_4, plug_z_5), run_time=2)
        self.wait(time)
        self.play(FadeOut(extract_z_3), FadeOut(plug_z_5))
        self.wait(time)

        self.play(Write(find_y_1))
        self.wait(time)
        self.play(TransformMatchingTexJ(find_y_1, find_y_2))
        self.wait(time)
        self.play(TransformMatchingTexJ(find_y_2, find_y_3))
        self.wait(time)
        self.play(TransformMatchingTexJ(find_y_3, find_y_4))
        self.wait(time)
        self.play(TransformMatchingTexJ(find_y_4, find_y_5))
        self.wait(time)

        find_y_5_corner = find_y_5.copy().scale(0.3).to_corner(UL)
        self.play(Transform(find_y_5, find_y_5_corner))
        self.wait(time)
        self.play(Write(z_3_minus_y_3))
        self.wait(time)
        self.play(TransformMatchingTexJ(z_3_minus_y_3, find_z_2))
        self.wait(time)
        self.play(FadeOut(find_y_5), TransformMatchingTexJ(find_z_2, find_z_3))
        self.wait(time)
        self.play(TransformMatchingTexJ(find_z_3, find_z_4))
        self.wait(time)

        find_z_4_corner = find_z_4.copy().scale(0.3).to_corner(UL)
        self.play(Transform(find_z_4, find_z_4_corner))
        self.wait(time)
        self.play(Write(find_x_1))
        self.wait(time)
        self.play(TransformMatchingTexJ(find_x_1, find_x_2))
        self.wait(time)
        self.play(TransformMatchingTexJ(find_x_2, find_x_3))
        self.wait(time)

        self.wait(10)


class _31_SubstituteIntoEquation(Scene):
    def construct(self):
        # og_eq = Tex("x", "^3", "=", "15", "x", "+ 4").set_color(BLACK).scale(3)

        # step_1 = (
        #     Tex("4", "^3", "=", "15", R"\times", "4", "+ 4").set_color(BLACK).scale(3)
        # )
        # step_2 = Tex("64", "=", "60", "+ 4").set_color(BLACK).scale(3)
        # step_3 = Tex("64 = 64").set_color(BLACK).scale(3)

        # full equations
        og_eq = Tex("x^3 = 15x + 4").set_color(BLACK).scale(3)

        step_1 = Tex(R"4^3 = 15 \times 4 + 4").set_color(BLACK).scale(3)
        step_2 = Tex("64 = 60 + 4").set_color(BLACK).scale(3)
        # step_3 = Tex("64 = 64").set_color(BLACK).scale(3)

        vg_all = VGroup(og_eq, step_1, step_2).arrange(DOWN, buff=1).scale(0.8)

        self.wait(2)
        time = 3
        for eq in vg_all:
            self.play(FadeIn(eq))
            self.wait(time)

        self.wait(2)

        # rt = 1

        # self.play(Write(og_eq))
        # self.wait(4)

        # self.play(TransformMatchingTexJ(og_eq, step_1), run_time=rt)
        # self.wait(4)
        # self.play(TransformMatchingTexJ(step_1, step_2), run_time=rt)
        # self.wait(4)
        # self.play(TransformMatchingTexJ(step_2, step_3), run_time=rt)
        # self.wait(4)


class CubicAndQuadraticFormulas(Scene):
    def construct(self):
        cubic = Tex("ax^3 + bx^2 + cx + d = 0", run_time=2).set_color(BLACK).scale(2)
        solution_cuadratic = (
            Tex(R"-b \pm \sqrt{b^2 - 4ac} \over 2a", run_time=2)
            .set_color(BLACK)
            .scale(2)
        )
        quadratic = Tex(R"ax^2 + bx + c = 0", run_time=2).set_color(BLACK).scale(2)

        time = 4

        self.play(Write(quadratic), run_time=2)
        self.wait(time)
        self.play(FadeOut(quadratic))

        self.wait(time)

        self.play(Write(solution_cuadratic), run_time=2)
        self.wait(time)
        self.play(FadeOut(solution_cuadratic))

        self.wait(time)

        self.play(Write(cubic), run_time=2)
        self.wait(time)
        self.play(FadeOut(cubic))

        self.wait(1)


class _5_CubicIsQuadratic(Scene):
    def construct(self):
        cubic = (
            Tex("ax^3 +", "b", "x^2", "+", "c", "x", "+", "d", "= 0", run_time=2)
            .set_color(BLACK)
            .scale(2)
        )
        quadratic = (
            Tex("b", "x^2", "+", "c", "x", "+", "d", "= 0", run_time=2)
            .set_color(BLACK)
            .scale(2)
        )

        quadratic_upd = (
            Tex("a", "x^2", "+", "b", "x", "+", "c", "= 0", run_time=2)
            .set_color(BLACK)
            .scale(2)
        )

        time = 3
        self.wait(2)

        self.play(FadeIn(cubic), run_time=2)
        self.wait(time)

        self.play(TransformMatchingTexJ(cubic, quadratic), run_time=2)

        self.play(
            *[
                FadeTransform(quadratic[0:2], quadratic_upd[0:2], stretch=True),
                FadeTransform(quadratic[3:5], quadratic_upd[3:5], stretch=True),
                FadeTransform(quadratic[6], quadratic_upd[6], stretch=False),
            ],
            run_time=1,
        )

        self.wait(2)


class _5_PlugAndChug(Scene):
    def construct(self):

        a, b, c = 5, 2, -3

        general_quad = (
            Tex("a", "x^2", "+", "b", "x", "+ c", "= 0").scale(2).set_color(BLACK)
        )
        # solution_quadratic = (
        #     Tex(
        #         "x =",  # 0
        #         R"{",
        #         f"-",  # 1
        #         "b",  # 2
        #         R"\pm \sqrt{",  # 3
        #         f"b",  # 4
        #         R"^2 - 4",  # 5
        #         f"ac",  # 6
        #         R"} \over",
        #         f"2aaa",  # 7
        #         R"}",
        #     )
        #     .set_color(BLACK)
        #     .scale(1.5)
        # )
        quad_equation = (
            Tex(f"{a}", "x^2", "+", f"{b}", "x", f"{c}", "= 0", run_time=2)
            .set_color(BLACK)
            .scale(2)
        )

        time = 4

        self.play(FadeIn(general_quad))
        self.wait()

        self.play(TransformMatchingTexJ(general_quad, quad_equation))

        self.play(
            ReplacementTransform(
                quad_equation, quad_equation.copy().scale(0.7).shift(UP * 3)
            ),
        )

        def quad_solution_f(a, b, c):
            return (
                int(((-b + sqrt((b ** 2) - (4 * a * c)))) / 2 * a),
                int(((-b - sqrt((b ** 2) - (4 * a * c)))) / 2 * a),
            )

        sol_1, sol_2 = quad_solution_f(a, b, c)

        solution_quadratic = (
            Tex(R"x = {-b \pm \sqrt{b^2 - 4ac} \over 2a}").set_color(BLACK).scale(1.5)
        )

        sus_numbers = (
            Tex(
                R"x = {-%d \pm \sqrt{%d^2 - 4\cdot%d\cdot%d} \over 2\cdot%d}"
                % (b, b, a, c, a),
            )
            .set_color(BLACK)
            .scale(1.5)
        )
        solved_equation = (
            Tex(
                R"x = {-%d \pm \sqrt{%d^2 - 4\cdot%d\cdot%d} \over 2\cdot%d}"
                % (b, b, a, c, a),
                "= %d, %d" % (sol_1, sol_2),
            )
            .set_color(BLACK)
            .scale(1.5)
        )

        self.play(FadeIn(solution_quadratic))
        self.wait(2)

        self.play(TransformMatchingTexJ(solution_quadratic, sus_numbers), run_time=2)
        self.wait(2)
        self.play(TransformMatchingTexJ(sus_numbers, solved_equation))

        self.wait(5)

        # end
        self.play(*[FadeOut(mob) for mob in self.mobjects])


class Cross(VGroup):
    def __init__(
        self,
        mobject: Optional["Mobject"] = None,
        stroke_color: Color = RED,
        stroke_width: float = 6,
        scale_factor: float = 1,
        **kwargs,
    ):
        super().__init__(
            Line(UP + LEFT, DOWN + RIGHT), Line(UP + RIGHT, DOWN + LEFT), **kwargs
        )
        if mobject is not None:
            self.replace(mobject, stretch=True)
        self.scale(scale_factor)
        self.set_stroke(color=stroke_color, width=stroke_width)


class _9_QuadraticSixVersions(Scene):
    def construct(self):
        general_quad = (
            Tex("a", "x^2", "+", "b", "x", "+ c", "= 0").scale(2).set_color(BLACK)
        )

        quad_1 = Tex("1.\\ ax^2 = bx")
        quad_2 = Tex("2.\\ ax^2 = c")
        quad_3 = Tex("3.\\ ax=c")
        quad_4 = Tex("4.\\ ax^2 + bx = c")
        quad_5 = Tex("5.\\ ax^2 + c = bx")
        quad_6 = Tex("6.\\ bx + c = ax^2")

        vg_quad_versions = (
            VGroup(quad_1, quad_2, quad_3, quad_4, quad_5, quad_6)
            .arrange_in_grid(n_cols=2, aligned_edge=LEFT, h_buff=1.5, v_buff=0.5)
            .set_color(BLACK)
            .scale(1.4)
        )

        self.play(FadeIn(general_quad))

        self.wait(2)

        self.play(FadeOut(general_quad))
        self.wait(2)

        self.play(LaggedStartMap(FadeIn, vg_quad_versions), run_time=2)

        self.wait(2)


class CubicWithNoBTerm(Scene):
    def construct(self):
        iso = ["a", "b", "c", "d"]
        cubic = Tex("ax^3 +", "b", "x^2", "+", "cx+d=0").scale(2).set_color(BLACK)

        cubic_no_b = Tex("ax^3 +", "cx+d=0").scale(2).set_color(BLACK)

        cubic_no_b_upd = (
            Tex("ax^3 +", "b", "x", "+ c", "=0", isolate=iso).scale(2).set_color(BLACK)
        )

        self.wait(1)
        self.play(FadeIn(cubic))
        self.wait(2)

        self.play(TransformMatchingTexJ(cubic, cubic_no_b), run_time=2)
        self.play(
            TransformMatchingTexJ(cubic_no_b, cubic_no_b_upd),
            run_time=2,
        )

        self.wait(3)


class SubstituteAndCancel(Scene):
    def construct(self):
        iso = ["a", "b", "c", "d", "x"]
        cubic = (
            Tex("ax^3", "+bx^2", "+cx", "+d", "=0", isolate=iso)
            .scale(2)
            .set_color(BLACK)
        )

        sustitution_indicator = (
            Tex(R"x = x - \frac{b}{3a}")
            .scale(1)
            .set_color(BLACK)
            .next_to(cubic, DOWN, aligned_edge=LEFT, buff=0.5)
        )

        sustitution = R"\left(x - \frac{b}{3a}\right)"
        sus_fraction = Tex(
            "a",
            f"{sustitution}",
            "^3",
            "+",
            "b",
            f"{sustitution}",
            "^2",
            "+",
            "c",
            f"{sustitution}",
            "+",
            "d",
            "=0",
            isolate=[sustitution],
        ).set_color(BLACK)

        new_equation = Tex("g(x) = ax^3 + Cx + D").set_color(BLACK).scale(2)

        self.play(Write(cubic), run_time=3)
        self.wait(4)

        self.play(FadeIn(sustitution_indicator))
        self.wait(4)

        self.play(TransformMatchingTexJ(cubic, sus_fraction), run_time=3)
        self.wait(4)
        self.play(
            FadeOut(sustitution_indicator),
            TransformMatchingTexJ(sus_fraction, new_equation),
            run_time=2,
        )
        self.wait(3)


class KayyamSentence(Scene):
    def construct(self):
        tex = (
            Text(
                '"Maybe one of those \nwho will come after us \nwill succeed in finding it"'
            )
            .set_color(BLACK)
            .set_stroke(WHITE, width=7, background=True)
            .scale(2.5)
        )

        self.play(Write(tex), lag_ratio=0.5, run_time=4)

        self.wait(3)


class _26_SustituteIntoDepressedCubic(Scene):
    def construct(self):
        a = 1
        b = 6
        c = 100

        iso = [f"{b}", f"{c}"]

        cubic_tex = Tex(
            f"f(x) =",
            "x",
            "^3",
            "+",
            f"{b}",
            "x",
            "^2",
            "-",
            f"{c}",
            "= 0",
            isolate=iso,
        ).set_color(BLACK)

        sustitution = R"\left(x - \frac{b}{3a}\right)"

        sus_fraction = Tex(
            "g(x) =",
            f"{sustitution}",
            "^3",
            "+",
            f"{b}",
            f"{sustitution}",
            "^2",
            "-",
            f"{c}",
            "=0",
            isolate=[sustitution],
        ).set_color(BLACK)

        self.play(FadeIn(cubic_tex))

        self.play(TransformMatchingTexJ(cubic_tex, sus_fraction))


class _18_ThreeYZ(Scene):
    def construct(self):
        step1 = Tex("3yz", "x", "=", "9", "x", isolate=["x"]).set_color(BLACK).scale(3)

        step2 = Tex("3yz", "=", "9").set_color(BLACK).scale(3)

        # step1 = Tex("3yz x = 9x").set_color(BLACK).scale(3)

        # step2 = Tex("3yz = 9").set_color(BLACK).scale(3)

        self.wait(1)
        self.play(FadeIn(step1))
        self.wait(3)
        self.play(TransformMatchingTexJ(step1, step2))
        self.wait(2)


class _30_AddTenProductForty(Scene):
    def construct(self):

        eqs = [
            Tex("x+y=10").set_color(BLACK),
            Tex("xy=40").set_color(BLACK),
            Tex("y=10-x").set_color(BLACK),
            Tex("x(10-x)=40").set_color(BLACK),
            Tex("x^2 + 40 = 10x").set_color(BLACK).scale(1.2),
        ]

        quadratic = eqs[-1]

        vg_all = VGroup(*eqs).arrange(DOWN, buff=0.5).scale(1.4)

        time = 4

        self.wait(1)
        for eq in vg_all:
            self.play(FadeIn(eq))
            self.wait(time)

        self.wait(2)

        self.play(
            *[FadeOut(e, run_time=0.6) for e in eqs[:-1]],
            quadratic.animate.to_edge(UP),
            run_time=2,
        )

        quad_solution = (
            Tex(R"x = \frac{-(-10) \pm \sqrt{(-10)^2 - 4 \times 40}}{2}")
            .set_color(BLACK)
            .scale(1.5)
        )

        solutions = (
            Tex("x = -5 \pm \sqrt{-15}")
            .set_color(BLACK)
            .scale(1.5)
            .next_to(quad_solution, DOWN, buff=0.7)
        )

        self.wait(3)
        self.play(FadeIn(quad_solution))
        self.wait(3)
        self.play(FadeIn(solutions))
