from math import sqrt
from manimlib import *
from perlin_noise import PerlinNoise


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


class CubicFunctionCircles(Scene):
    def construct(self):
        noise = PerlinNoise()
        # wait for further instruction to add the texture
        # paper_bg = ImageMobject("paper.jpg").scale(4).set_opacity(0.95)
        # self.add(paper_bg)

        axes = Axes(
            x_range=[0, 2, 0.5],
            y_range=[0, 2, 0.5],
            width=7,
            height=7,
            axis_config={
                "include_tip": False,
                "include_ticks": True,
                "numbers_with_elongated_ticks": [1, 2],
                "line_to_number_buff": 0.35,
                "stroke_color": BLACK,
            },
            x_axis_config={
                "stroke_color": BLACK,
            },
            y_axis_config={"stroke_color": BLACK},
            num_sampled_graph_points_per_tick=100,
        )

        self.play(self.camera.frame.animate.shift(OUT * 3 + LEFT))

        axes.add_coordinate_labels(
            y_values=np.arange(0, 3),
            x_values=np.arange(0, 3),
        ).set_color(BLACK)
        # self.play(Write(axes))

        # x^3 + bx = c
        # semicircle: r = c / 2b, center: (r, 0)
        # parabola: y = x^2 / sqrt(b)

        b = 4
        c = 5
        r = c / (2 * b)

        def cubic_func(x):
            return x ** 2 / sqrt(b)

        points = axes.c2p(r, 0)

        origin_axis = axes.c2p(0, 0)
        # self.play(Write(Dot(points, radius=0.01).set_color(RED)))

        semicircle = Arc(
            radius=abs(points[0] - origin_axis[0]),
            arc_center=points,
            angle=PI,
        ).set_color(RED)

        # semicircle.apply_function(lambda x: x + UP * np.random.rand() * 0.05)

        self.play(Write(semicircle))

        cubic_graph = (
            axes.get_graph(cubic_func, [0, 3]).set_color("#16264c").set_stroke(width=5)
        )

        points = []
        factor = 0.08
        for i, p in enumerate(cubic_graph.get_points()):
            points.append(p + noise(i / 100) * factor)

        # self.add(
        #     Tex(f"factor = {factor}").scale(1).set_color(BLACK).to_corner(UL, buff=0.01)
        # )

        cubic_graph.set_points(points)

        cubic_graph_tex = (
            Tex(R"\frac{x^2} {\sqrt{" + str(b) + "}}")
            .set_color("#16264c")
            .scale(1)
            .next_to(cubic_graph, DOWN * 1.6 + LEFT * 1.3, buff=-4.6)
        )

        self.wait(2)
        self.play(Write(cubic_graph), Write(cubic_graph_tex))

        self.wait(2)

        intersection_dot = Dot(axes.input_to_graph_point(1, cubic_graph)).set_color(RED)

        line_to_graph = DashedLine(
            axes.c2p(1, 0), axes.input_to_graph_point(1, cubic_graph)
        ).set_color("#16264c")

        self.play(Write(line_to_graph), Write(intersection_dot))

        intersection_coords = axes.p2c(intersection_dot.get_center())
        intersection_tex = (
            Tex(f"({intersection_coords[0]:.1f}, {intersection_coords[1]:.1f})")
            .set_color(RED)
            .set_stroke("#FFF4D7", width=10, background=True)
            .scale(0.7)
            .next_to(intersection_dot, UP, buff=0.4)
        )

        self.play(Write(intersection_tex))

        self.wait(4)

        # self.embed()


class CubicSubstituteMoveToOrigin(Scene):
    def construct(self):

        a = 1
        b = 6
        c = 100

        cubic_func = lambda x: a * (x ** 3) + b * (x ** 2) - c

        cubic_func_sus = (
            lambda x: a * ((x - (b / (3 * a))) ** 3)
            + b * ((x - (b / (3 * a))) ** 2)
            - c
        )

        axes = Axes(
            x_range=[-50, 50, 10],
            y_range=[-500, 500, 100],
            width=17,
            height=14,
            faded_line_ratio=0.1,
            include_numbers=True,
            axis_config={
                "stroke_width": 3,
                "include_numbers": True,
                "include_tip": False,
            },
            y_axis_config={
                "line_to_number_direction": UP,
            },
        ).set_color(GREY_C)

        # axes.add_coordinate_labels(
        #     x_values=np.arange(-50, 60, 10),
        #     y_values=np.arange(-500, 600, 100),
        # ).set_color(GREY_C)

        # for g in axes.coordinate_labels:
        #     for num in g:
        #         num.scale(0.7)

        cubic_graph = (
            axes.get_graph(cubic_func, [-20, 10])
            .set_color("#16264c")
            .set_stroke(width=3)
        )
        cubic_graph_sus = (
            axes.get_graph(cubic_func_sus, [-20, 10])
            .set_color(RED_C)
            .set_stroke(width=3)
        )

        self.play(Write(axes), run_time=0.5)
        self.wait(2)

        iso = [f"{b}", f"{c}"]
        cubic_tex = (
            Tex(
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
            )
            .set_color("#16264c")
            .scale(1)
            .to_corner(UL)
        )

        sustitution = R"\left(x - \frac{b}{3a}\right)"

        sus_fraction = (
            Tex(
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
            )
            .set_color(RED_C)
            # .set_stroke("#FFF4D7", width=2, background=True)
            .scale(0.6)
            .to_corner(UL)
        )

        sustitution_tex = (
            Tex(R"x = x - \frac{b}{3a}")
            .set_color(BLACK)
            .scale(0.6)
            .next_to(sus_fraction, DOWN, aligned_edge=LEFT)
        )

        self.play(Write(cubic_graph), Write(cubic_tex), run_time=5)

        self.wait(2)

        self.play(Write(sustitution_tex))

        self.wait(2)

        self.play(
            Transform(cubic_graph, cubic_graph_sus),
            TransformMatchingTexJ(cubic_tex, sus_fraction),
            run_time=2,
        )
        # self.play(cubic_graph.animate.move_to(ORIGIN, coor_mask=[1, 0, 0]), run_time=2)
