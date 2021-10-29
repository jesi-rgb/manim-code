from functools import update_wrapper
from typing import final
from manimlib import *
from numpy import cbrt, sqrt

# x^3 = 15x + 4
# x^3 = cx + d


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
                Transform(
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
            anims.append(
                FadeOut(fade_source, self.fade_direction, **kwargs, run_time=0.5)
            )
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


class DepressedCubic(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=-45 * DEGREES,
            phi=70 * DEGREES,
        )

        frame.shift((LEFT + DOWN) * 30 + OUT * 20)

        general_opacity = 1

        # x^3 = 6x^2 + 100
        b = 6
        c = 100

        x = 9
        y = 7
        z = 2

        x_cube = Cube(side_length=x).set_color(PURPLE).shift(UL * 8)  # full cube

        y_cube = (
            Cube(side_length=y)
            .set_color(YELLOW_D)
            .next_to(x_cube, ORIGIN, aligned_edge=UP + RIGHT + IN, buff=0)
            # .shift(LEFT * y / 2)
        ).set_opacity(general_opacity)

        z_cube = (
            Cube(side_length=z)
            .set_color(RED_C)
            .next_to(y_cube, DOWN + LEFT + OUT, buff=0)
        )

        # x, y, y prisms
        ####################################################
        z_y_y = (
            Prism(dimensions=[z, y, y])
            .set_color(BLUE_D)
            .rotate(PI / 2, OUT)
            .next_to(y_cube, DOWN, buff=0)
        ).set_opacity(general_opacity)

        z_y_y_1 = (
            (Prism(dimensions=[z, y, y]).set_color(BLUE_D))
            # .rotate(PI / 2, Z_AXIS)
            .next_to(y_cube, LEFT, buff=0)
        ).set_opacity(general_opacity)

        z_y_y_2 = (
            Prism(dimensions=[y, y, z])
            .set_color(BLUE_D)
            .rotate(0)
            .next_to(y_cube, OUT, buff=0)
        ).set_opacity(general_opacity)

        # x, x, y prisms
        ####################################################
        z_z_y = (
            Prism(dimensions=[z, z, y])
            .set_color(GREEN)
            .rotate(PI / 2, X_AXIS)
            .next_to(y_cube, OUT + LEFT, buff=0)
            .set_opacity(general_opacity)
        )
        z_z_y_1 = (
            Prism(dimensions=[z, z, y])
            .set_color(GREEN)
            .rotate(PI / 2, Y_AXIS)
            .next_to(y_cube, DOWN + OUT, buff=0)
        ).set_opacity(general_opacity)

        z_z_y_2 = (
            Prism(dimensions=[z, z, y])
            .set_color(GREEN)
            .next_to(y_cube, LEFT + DOWN, buff=0)
        ).set_opacity(general_opacity)

        ####################################################
        # DEPRESSED CUBIC

        depressed_prism = (
            Prism(dimensions=[x, x, b]).set_color(BLUE_D).shift(DR * 8)
        )  # full depressed prism

        dep_y = (
            Prism(dimensions=[y, y, b])
            .set_color(YELLOW_D)
            .next_to(depressed_prism, ORIGIN, aligned_edge=RIGHT + IN + UP)
        )  # main one
        dep_z = (
            Prism(dimensions=[z, z, b])
            .set_color(RED_C)
            .next_to(dep_y, DOWN + LEFT, buff=0)
        )
        dep_byz = (
            Prism(dimensions=[y, z, b]).set_color(GREEN).next_to(dep_y, DOWN, buff=0)
        )
        dep_byz_1 = (
            Prism(dimensions=[y, z, b])
            .set_color(GREEN)
            .rotate(PI / 2, Z_AXIS)
            .next_to(dep_y, LEFT, buff=0)
        )

        ####################################################

        def create_three_axis_brace(
            mobject: Mobject,
            color,
            width_tag,
            height_tag,
            depth_tag,
            stroke_w=1.2,
            scale_tags=1,
        ):
            rot_mob = mobject.copy().rotate(PI / 2, X_AXIS)
            braces = [
                Brace(mobject, DOWN)
                .set_color(color)
                .shift(IN * mobject.get_depth() / 2),
                Brace(mobject, LEFT)
                .set_color(color)
                .shift(IN * mobject.get_depth() / 2),
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
                w_tag.copy().scale(scale_tags).next_to(braces[0], DOWN),
                h_tag.copy().scale(scale_tags).next_to(braces[1], LEFT),
                d_tag.copy()
                .scale(scale_tags)
                .next_to(braces[2], LEFT)
                .rotate(PI / 2 - 0.0001, X_AXIS)
                # .shift(UP * mobject.get_depth() / 2 + OUT * mobject.get_height() / 2),
            ]

            [b.set_stroke(width=stroke_w) for b in braces]
            [b.set_stroke(width=stroke_w) for b in tags]

            return braces, tags

        ####################################################
        # beginning of the animation

        # appears main cube

        self.play(FadeIn(x_cube))

        # annotate dimensions
        x_braces, x_tags = create_three_axis_brace(
            x_cube, x_cube.get_color(), "x", "x", "x", scale_tags=5, stroke_w=5
        )

        self.play(
            *[Write(b) for b in x_braces], *[Write(a) for a in x_tags], run_time=2
        )

        # appears depressed cubic

        self.play(FadeIn(depressed_prism))

        # annotate dimensions
        dep_braces, dep_tags = create_three_axis_brace(
            depressed_prism, BLUE_D, "x", "x", "b", stroke_w=5, scale_tags=5
        )

        self.play(
            *[Write(b) for b in dep_braces], *[Write(a) for a in dep_tags], run_time=2
        )

        # draw breaking lines on prisms

        # fade prisms into their constituting parts

        # blow up prisms


class _26_DepressedEquations(Scene):
    def construct(self):
        a, b, c, d = "2", "- 30", "162", "- 350"
        original_eq = (
            Tex(f"{a}x^3 {b}x^2 + {c}x {d} = 0").set_color(BLACK).scale(2).shift(UP * 2)
        )

        sustitute = R"x - \frac{%s}{3\cdot%s}" % (b, a)
        eq_sus = Tex(
            f"2\left({sustitute}\\right)^3",
            f"- 30\left({sustitute}\\right)^2",
            f"+ 162\left({sustitute}\\right) - 350 = 0",
        ).set_color(BLACK)

        depressed_equation = Tex("x^3 + 6x - 20 = 0").set_color(BLACK).scale(2)

        vg_all = VGroup(original_eq, eq_sus, depressed_equation).arrange(DOWN, buff=1.2)

        self.wait(1)
        for eq in vg_all:
            self.play(FadeIn(eq))
            self.wait(3)

        self.wait(2)


class _26_DepressedEquationsBreakdown(Scene):
    def construct(self):

        original_eq = (
            Tex(f"ax^3 +bx^2 + cx + d", "= 0", isolate=["x", "a", "b", "c", "d", "+"])
            .set_color(BLACK)
            .scale(2)
        )

        sustitute = R"x - \frac{b}{3a}"
        eq_sus = Tex(
            f"a",
            f"\left({sustitute}\\right)^3",
            f"+",
            "b",
            f"\left({sustitute}\\right)^2",
            f"+",
            "c",
            f"\left({sustitute}\\right)",
            "+",
            "d",
            "= 0",
            # isolate=["a", "b", "c", "d"],
        ).set_color(BLACK)

        expand_1 = (
            Tex(
                R"ax^3",
                R"-\frac{2bx^2}{3}",  # to indicate 1
                R"+\frac{b^2x}{9}",
                R"-\frac{bx^2}{3}",  # to indicate 3
                R"+\frac{2b^2x}{3}",
                R"-\frac{b^3}{27a}",
                R"+",
                R"bx^2",  # to indicate 7
                R"-\frac{2b^2x}{3a}",
                R"+\frac{b^3}{9a^2}",
                "\dots",
                "=0",
            )
            .set_color(BLACK)
            .scale(0.8)
        )

        compress_1 = Tex(
            R"ax^3",
            R"-bx^2",
            R"+\frac{7b^2x}{9}",
            R"-\frac{b^3}{27a}",
            R"+",
            "bx^2",
            R"-\frac{2b^2x}{3a}",
            R"+\frac{b^3}{9a^2}",
            "\dots",
            "=0",
        ).set_color(BLACK)

        final_eq = Tex(
            R"ax^3",
            R"+\left(c - \frac{b^2}{3a}\right)x",
            "+",
            R"\left(",
            R"d +\frac{2b^3}{27a^2} -\frac{bc}{3a}",
            R"\right)",
            R"=0",
        ).set_color(BLACK)

        self.play(FadeIn(original_eq))

        self.play(
            TransformMatchingTexJ(original_eq, eq_sus, fade_direction=ORIGIN),
            run_time=4,
        )

        self.play(eq_sus.animate.shift(UP * 2))

        self.play(FadeIn(expand_1.next_to(eq_sus, DOWN, buff=1)))

        brace_ax3 = Brace(expand_1[:6], direction=DOWN).set_color(BLACK)
        annotation_ax3 = (
            Tex(f"a\left({sustitute}\\right)^3")
            .set_color(BLACK)
            .scale(0.7)
            .next_to(brace_ax3, DOWN)
        )
        brace_label_ax3 = VGroup(brace_ax3, annotation_ax3)
        self.play(FadeIn(brace_label_ax3), run_time=2)

        brace_bx2 = Brace(expand_1[7:-2], direction=DOWN).set_color(BLACK)
        annotation_bx2 = (
            Tex(f"b\left({sustitute}\\right)^2")
            .set_color(BLACK)
            .scale(0.7)
            .next_to(brace_bx2, DOWN)
        )
        brace_label_bx2 = VGroup(brace_bx2, annotation_bx2)
        self.play(FadeIn(brace_label_bx2), run_time=2)

        self.play(FadeOut(brace_label_ax3), FadeOut(brace_label_bx2))

        rect_1 = SurroundingRectangle(expand_1[1], buff=0.1).set_color(RED_C)
        rect_3 = SurroundingRectangle(expand_1[3], buff=0.1).set_color(RED_C)
        rect_7 = SurroundingRectangle(expand_1[7], buff=0.1).set_color(RED_C)

        self.play(LaggedStartMap(Write, VGroup(*[rect_1, rect_3, rect_7])))

        self.play(FadeIn(compress_1.next_to(expand_1, DOWN, buff=1)))

        brace_ax3 = Brace(compress_1[:4], direction=DOWN).set_color(BLACK)
        annotation_ax3 = (
            Tex(f"a\left({sustitute}\\right)^3")
            .set_color(BLACK)
            .scale(0.7)
            .next_to(brace_ax3, DOWN)
        )
        brace_label_ax3 = VGroup(brace_ax3, annotation_ax3)
        self.play(FadeIn(brace_label_ax3), run_time=2)

        brace_bx2 = Brace(compress_1[5:-2], direction=DOWN).set_color(BLACK)
        annotation_bx2 = (
            Tex(f"b\left({sustitute}\\right)^2")
            .set_color(BLACK)
            .scale(0.7)
            .next_to(brace_bx2, DOWN)
        )
        brace_label_bx2 = VGroup(brace_bx2, annotation_bx2)
        self.play(FadeIn(brace_label_bx2), run_time=2)

        self.play(FadeOut(brace_label_ax3), FadeOut(brace_label_bx2))
