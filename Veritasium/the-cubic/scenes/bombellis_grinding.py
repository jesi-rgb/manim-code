from inspect import getinnerframes, iscode
from typing import final
from manimlib import *


class TransformMatchingPartsJ(AnimationGroup):
    CONFIG = {
        "mobject_type": Mobject,
        "group_type": Group,
        "transform_mismatches": False,
        "fade_transform_mismatches": False,
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
        anims = [FadeTransformPieces(transform_source, transform_target, **kwargs)]
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
                FadeTransformPieces(
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
            anims.append(FadeTransformPieces(fade_source.copy(), fade_target, **kwargs))
        if self.fade_transform_mismatches:
            anims.append(FadeTransformPieces(fade_source, fade_target, **kwargs))
        else:
            anims.append(FadeOut(fade_source, DOWN, **kwargs))
            anims.append(FadeIn(fade_target.copy(), DOWN, **kwargs))

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


class BombellisFormulaSolutionGrind(Scene):
    def construct(self):

        quadratic = (
            Tex(R"x^2=15x+4 \rightarrow ax^2 = bx + c")
            .set_color(BLACK)
            .scale(1)
            .to_corner(UL)
        )
        eq_1 = Tex(
            R"\sqrt[3]{\frac d2+\sqrt{\frac{d^2}4-\frac{c^3}{27}}}",
            R"+\sqrt[3]{\frac d2-\sqrt{\frac{d^2}4-\frac{c^3}{27}}}",
        ).set_color(BLACK)

        sustitution = Tex(
            R"\sqrt[3]{\frac 42+\sqrt{\frac{4^2}4-\frac{15^3}{27}}}",
            R"+\sqrt[3]{\frac 42-\sqrt{\frac{4^2}4-\frac{15^3}{27}}}",
        ).set_color(BLACK)

        simplify_1 = Tex(
            R"\sqrt[3]{2+\sqrt{4-125}} +\sqrt[3]{2-\sqrt{4-125}}"
        ).set_color(BLACK)

        separation = Tex(
            R"\sqrt[3]{ ",
            R"2 + \sqrt{-121}",
            "}",
            R" \rightarrow ",
            R"a + b \sqrt{-11} ",
        ).set_color(BLACK)

        cube_sides = Tex(
            R"2 + \sqrt{-121}", "=", R"(a+b\sqrt{-1})(a+b\sqrt{-1})(a+b\sqrt{-1})"
        ).set_color(BLACK)

        equals = Tex(R"(a^2+2ab\sqrt{-1}+b^2(\sqrt{-1})^2)(a+b\sqrt{-1})").set_color(
            BLACK
        )

        simplify_2 = Tex(
            R"2+\sqrt{-121} = a^3-3ab^2+3a^2b\sqrt{-1}-b^3\sqrt{-1}"
        ).set_color(BLACK)

        separate_equations = Tex(
            R"2=a^3-3ab^2 \\ \sqrt{-121}=3a^2b\sqrt{-1}-b^3\sqrt{-1}"
        ).set_color(BLACK)

        separate_equations_2 = Tex(
            R"11 \sqrt{-1} =b \sqrt{-1}(3a^2-b^2) \\ 11=b(3a^2-b^2)"
        ).set_color(BLACK)

        separate_equations_3 = Tex(R"2=a^3-3ab^2 \\ 11=b(3a^2-b^2)").set_color(BLACK)

        meaning = Tex(
            R"\sqrt[3]{2+\sqrt{-121}}=2+\sqrt{-1} \\ \sqrt[3]{2-\sqrt{-121}}=2-\sqrt{-1}"
        ).set_color(BLACK)
        final_step = Tex(R"(2+\sqrt{-1}) + (2-\sqrt{-1})=4").set_color(BLACK)

        self.add(quadratic)

        self.wait(1)

        time = 4

        self.play(Write(eq_1))
        self.wait(time)
        self.play(TransformMatchingTexJ(eq_1, sustitution))
        self.wait(time)
        self.play(TransformMatchingTexJ(sustitution, simplify_1))
        self.wait(time)
        self.play(TransformMatchingTexJ(simplify_1, separation))
        self.wait(time)

        self.play(TransformMatchingShapes(separation, cube_sides))
        self.wait(time)

        self.play(
            TransformMatchingTexJ(
                cube_sides,
                equals,
                key_map={
                    "(a+b\sqrt{-1})(a+b\sqrt{-1})(a+b\sqrt{-1})": "(a^2+2ab\sqrt{-1}+b^2(\sqrt{-1})^2)(a+b\sqrt{-1})"
                },
            )
        )
        self.wait(time)

        self.play(TransformMatchingTexJ(equals, simplify_2))
        self.wait(time)
        self.play(TransformMatchingTexJ(simplify_2, separate_equations))
        self.wait(time)
        self.play(TransformMatchingTexJ(separate_equations, separate_equations_2))
        self.wait(time)
        self.play(TransformMatchingTexJ(separate_equations_2, separate_equations_3))
        self.wait(time)
        self.play(TransformMatchingTexJ(separate_equations_3, meaning))
        self.wait(time)
        self.play(TransformMatchingTexJ(meaning, final_step))


class BombellisFormulaSolutionSlideShow(Scene):
    def construct(self):

        quadratic = (
            Tex(R"x^2=15x+4 \rightarrow ax^2 = bx + c")
            .set_color(BLACK)
            .scale(1)
            .to_corner(UL)
        )
        eq_1 = Tex(
            R"\sqrt[3]{\frac d2+\sqrt{\frac{d^2}4-\frac{c^3}{27}}}",
            R"+\sqrt[3]{\frac d2-\sqrt{\frac{d^2}4-\frac{c^3}{27}}}",
        ).set_color(BLACK)

        sustitution = Tex(
            R"\sqrt[3]{\frac 42+\sqrt{\frac{4^2}4-\frac{15^3}{27}}}",
            R"+\sqrt[3]{\frac 42-\sqrt{\frac{4^2}4-\frac{15^3}{27}}}",
        ).set_color(BLACK)

        simplify_1 = Tex(
            R"\sqrt[3]{2+\sqrt{4-125}} +\sqrt[3]{2-\sqrt{4-125}}"
        ).set_color(BLACK)

        separation = Tex(
            R"\sqrt[3]{ ",
            R"2 + \sqrt{-121}",
            "}",
            R" \rightarrow ",
            R"a + b \sqrt{-11} ",
        ).set_color(BLACK)

        cube_sides = Tex(
            R"2 + \sqrt{-121}", "=", R"(a+b\sqrt{-1})(a+b\sqrt{-1})(a+b\sqrt{-1})"
        ).set_color(BLACK)

        equals = Tex(R"(a^2+2ab\sqrt{-1}+b^2(\sqrt{-1})^2)(a+b\sqrt{-1})").set_color(
            BLACK
        )

        simplify_2 = Tex(
            R"2+\sqrt{-121} = a^3-3ab^2+3a^2b\sqrt{-1}-b^3\sqrt{-1}"
        ).set_color(BLACK)

        separate_equations = Tex(
            R"2=a^3-3ab^2 \\ \sqrt{-121}=3a^2b\sqrt{-1}-b^3\sqrt{-1}"
        ).set_color(BLACK)

        separate_equations_2 = Tex(
            R"11 \sqrt{-1} =b \sqrt{-1}(3a^2-b^2) \\ 11=b(3a^2-b^2)"
        ).set_color(BLACK)

        separate_equations_3 = Tex(R"2=a^3-3ab^2 \\ 11=b(3a^2-b^2)").set_color(BLACK)

        meaning = Tex(
            R"\sqrt[3]{2+\sqrt{-121}}=2+\sqrt{-1} \\ \sqrt[3]{2-\sqrt{-121}}=2-\sqrt{-1}"
        ).set_color(BLACK)

        final_step_1 = Tex(
            R"(2 + \sqrt{-1}) + (2 - \sqrt{-1})=4", isolate=["2", "+", "=", "4"]
        ).set_color(BLACK)

        all_eqs = (
            VGroup(
                eq_1,
                sustitution,
                simplify_1,
                simplify_2,
                separation,
                cube_sides,
                equals,
                simplify_2,
                separate_equations,
                separate_equations_2,
                separate_equations_3,
                meaning,
                Tex(""),
                Tex(""),
                Tex(""),
                final_step_1,
            )
            .arrange(DOWN, buff=2)
            .move_to(ORIGIN, aligned_edge=UP)
            .scale(1)
        )

        final_step_2 = (
            Tex(R"2 + 2 = 4", isolate=["2", "+", "=", "4"])
            .set_color(BLACK)
            .move_to(final_step_1)
            .scale(1.5)
        )

        final_step_3 = (
            Tex(R"4 = 4", isolate=["="])
            .set_color(BLACK)
            .move_to(final_step_1)
            .scale(1.5)
        )

        self.add(all_eqs)

        frame = self.camera.frame
        self.play(
            frame.animate.shift(final_step_1.get_center()),
            run_time=30,
            rate_func=linear,
        )

        self.play(
            final_step_1.animate.scale(1.5),
        )

        self.play(TransformMatchingTexJ(final_step_1, final_step_2), run_time=3)
        self.wait(2)


class _29_BombellisSolutionBreakdown(Scene):
    def construct(self):

        quadratic = (
            Tex(R"x^2=15x+4 \rightarrow ax^2 = bx + c")
            .set_color(BLACK)
            .scale(1)
            .to_corner(UL)
        )
        eq_1 = Tex(
            R"\sqrt[3]{\frac d2+\sqrt{\frac{d^2}4-\frac{c^3}{27}}}+\sqrt[3]{\frac d2-\sqrt{\frac{d^2}4-\frac{c^3}{27}}}",
        ).set_color(BLACK)

        sustitution = Tex(
            R"\sqrt[3]{\frac 42+\sqrt{\frac{4^2}4-\frac{15^3}{27}}}+\sqrt[3]{\frac 42-\sqrt{\frac{4^2}4-\frac{15^3}{27}}}",
        ).set_color(BLACK)

        simplify_1 = Tex(R"\sqrt[3]{2+\sqrt{-121}} +\sqrt[3]{2-\sqrt{-121}}").set_color(
            BLACK
        )

        separation = Tex(
            R"\sqrt[3]{2 + \sqrt{-121}} = a + b \sqrt{-1} \\ \sqrt[3]{2 - \sqrt{-121}} = a - b \sqrt{-1}",
        ).set_color(BLACK)

        simplify_2 = Tex(
            R"{\left(\sqrt[3]{2 + \sqrt{-121}}\right)}^3 = {\left(a + b\sqrt{-1}\right)}^3 = \\ a^3-3ab^2+3a^2b\sqrt{-1}-b^3\sqrt{-1}"
        ).set_color(BLACK)

        separation_2 = Tex(
            R"2+\sqrt{-121} = a^3-3ab^2+3a^2b\sqrt{-1}-b^3\sqrt{-1}"
        ).set_color(BLACK)

        separate_equations = Tex(
            R"2=a^3-3ab^2 \\ \sqrt{-121}=3a^2b\sqrt{-1}-b^3\sqrt{-1}"
        ).set_color(BLACK)

        separate_equations_2 = Tex(
            R"11 \sqrt{-1} =b \sqrt{-1}(3a^2-b^2) \\ 11=b(3a^2-b^2)"
        ).set_color(BLACK)

        separate_equations_3 = Tex(R"2=a^3-3ab^2 \\ 11=b(3a^2-b^2)").set_color(BLACK)

        equals_four = Tex(R"4=a+b\sqrt{-1} + a-b\sqrt{-1}").set_color(BLACK)

        meaning = Tex(
            R"\sqrt[3]{2+\sqrt{-121}}=2+\sqrt{-1} \\ \sqrt[3]{2-\sqrt{-121}}=2-\sqrt{-1}"
        ).set_color(BLACK)

        final_step_1 = (
            Tex(R"(2 + \sqrt{-1}) + (2 - \sqrt{-1})=4", isolate=["2", "+", "=", "4"])
            .set_color(BLACK)
            .scale(1.3)
        )

        page_1 = (
            VGroup(
                eq_1,
                sustitution,
                simplify_1,
                separation,
            )
            .arrange(DOWN, buff=1)
            .scale(0.8)
        )

        page_2 = (
            VGroup(
                simplify_2,
                separation_2,
                separate_equations,
                separate_equations_2,
            )
            .arrange(DOWN, buff=1)
            .scale(0.8)
        )

        page_3 = (
            VGroup(
                separate_equations_3,
                equals_four,
                meaning,
                final_step_1,
            )
            .arrange(DOWN, buff=1)
            .scale(0.9)
        )

        time = 7

        for eq in page_1:
            self.play(FadeIn(eq))
            self.wait(time)

        self.play(page_1.animate.shift(UP * 10), run_time=2)
        self.remove(page_1)

        for eq in page_2:
            self.play(FadeIn(eq))
            self.wait(time)

        self.play(page_2.animate.shift(UP * 10), run_time=2)
        self.remove(page_2)

        for eq in page_3:
            self.play(FadeIn(eq))
            self.wait(time)

        self.play(page_3.animate.shift(UP * 10), run_time=2)
        self.remove(page_3)
