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


class NumberlineSquaring(Scene):
    def construct(self):
        frame = self.camera.frame

        nl = NumberLine(x_range=[-20, 20, 1], include_numbers=True, width=14).set_color(
            BLACK
        )
        nl.numbers.set_color(BLACK)
        [n.scale(0.5) for n in nl.numbers]

        self.play(frame.animate.scale(0.36))
        self.play(frame.animate.move_to(nl.n2p(5)))

        dot = Dot(nl.n2p(3)).set_color(BLUE_D)
        self.play(Write(nl))

        self.play(Write(dot))
        self.wait(2)

        arrow = Arrow(
            dot.get_center(),
            nl.n2p(9),
            fill_color=BLUE_D,
            buff=0,
            thickness=0.01,
        )
        self.play(GrowArrow(arrow), run_time=1 / 2)
        final_dot = dot.copy().move_to(nl.n2p(9))
        three_sq = (
            Tex("3^2").set_color(BLUE_D).next_to(final_dot, UP, buff=0.2).scale(0.4)
        )

        tex_mul = (
            Tex(R"3", R"\times", "3", "= 9")
            .set_color(BLACK)
            .scale(0.6)
            .next_to(final_dot, UP, buff=1)
        )

        self.play(
            Write(three_sq),
            Write(tex_mul),
            arrow.scale,
            0,
            {"about_point": arrow.get_end()},
            run_time=1,
        )

        self.play(ReplacementTransform(dot, final_dot), run_time=2)
        self.wait(2)

        self.play(frame.animate.scale(1.5), FadeOut(final_dot))
        self.wait(2)

        dot = Dot(nl.n2p(-3)).set_color(BLUE_D)

        self.play(Write(dot))

        arrow = Arrow(
            dot.get_center(),
            nl.n2p(9),
            fill_color=BLUE_D,
            buff=0,
            thickness=0.01,
        )
        self.play(GrowArrow(arrow), run_time=1)

        tex_mul_neg = (
            Tex(R"-", "3", R"\times", "-", "3", "= 9")
            .set_color(BLACK)
            .scale(0.6)
            .next_to(final_dot, UP, buff=1)
        )

        minus_three_sq = (
            Tex(R"(-3)^2").set_color(BLUE_D).next_to(final_dot, UP, buff=0.2).scale(0.4)
        )

        self.play(
            Transform(three_sq, minus_three_sq),
            Transform(dot, final_dot, run_time=3),
            TransformMatchingTexJ(tex_mul, tex_mul_neg),
            arrow.scale,
            0,
            {"about_point": arrow.get_end()},
        )

        self.wait(5)

        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(2)
