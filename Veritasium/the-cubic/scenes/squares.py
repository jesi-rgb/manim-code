from manimlib import *
from numpy import absolute, sign, sqrt, square, ndarray

# X^2 + 10X = 39 => x = 3
# x^2 + 4x = 32 => x = 4


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


class Rectangle(Rectangle):
    def get_center_of_edges(self, buff=SMALL_BUFF * 3):
        vertices = self.get_vertices()
        coords_vertices = []
        for i in range(len(vertices)):
            if i < len(vertices) - 1:
                p1, p2 = [vertices[i], vertices[i + 1]]
            else:
                p1, p2 = [vertices[-1], vertices[0]]
            guide_line = Line(p1, p2)
            side = guide_line.get_center()
            normal_direction = guide_line.copy()
            normal_direction.rotate(PI / 2)
            vector_normal_direction = normal_direction.get_unit_vector()
            direction = Dot(side).shift(vector_normal_direction * buff).get_center()
            coords_vertices.append(direction)

        return coords_vertices


class Square(Square):
    def get_center_of_edges(self, buff=SMALL_BUFF * 3):
        vertices = self.get_vertices()
        coords_vertices = []
        for i in range(len(vertices)):
            if i < len(vertices) - 1:
                p1, p2 = [vertices[i], vertices[i + 1]]
            else:
                p1, p2 = [vertices[-1], vertices[0]]
            guide_line = Line(p1, p2)
            side = guide_line.get_center()
            normal_direction = guide_line.copy()
            normal_direction.rotate(PI / 2)
            vector_normal_direction = normal_direction.get_unit_vector()
            direction = Dot(side).shift(vector_normal_direction * buff).get_center()
            coords_vertices.append(direction)

        return coords_vertices


class SquareExplanation(Scene):
    def construct(self):

        self.play(self.camera.frame.animate.shift(OUT * 13))

        # wait for further instruction to add the texture
        # paper_bg = ImageMobject("paper.jpg").scale(4).set_opacity(0.95)
        # self.add(paper_bg)

        # latex and variables

        x = 3
        x_term = 10
        # equals = 39

        real_x = 1
        real_x_term = 26
        real_equals = 27

        main_sq = Square(x).set_color(BLACK)
        rect = Rectangle(x_term, x).set_color(BLUE_E)

        latex_eq = (
            Tex(
                "x",
                "^2",
                "+",
                f"{real_x_term}x",
                "=",
                f"{real_equals}",
                # isolate=[f"{real_x_term}"],
            )
            .scale(1.3)
            .set_color(BLACK)
            .move_to(self.camera.frame.get_edge_center(UP), coor_mask=[1, 0.9, 0.9])
        )

        latex_eq[3][:-1].set_color(BLUE_E)
        latex_eq.set_color_by_tex(f"{(real_x_term//2)**2}", RED_C)

        x_t = Tex(r"x").set_color(GREY_C)
        term_t = Tex(f"{real_x_term}").set_color(BLUE_E)

        ex_sq = Tex(r"x^2").set_color(BLACK).scale(1.5)
        ex_term = Tex(f"{real_x_term}x").set_color(BLUE_E).scale(1.5)
        # ex_term_half = Tex(f"{real_x_term // 2}x").set_color(BLUE_E).scale(1)
        ex_term_half_sq = Tex(f"{(real_x_term // 2) ** 2}").set_color(RED_C).scale(1.5)

        ex_plus_half = Tex(
            f"(x + {real_x_term//2})", isolate=[f"{real_x_term//2}"]
        ).set_color(BLACK)
        ex_plus_half.set_color_by_tex(f"{real_x_term//2}", RED_C)

        def ex_sq_updt(mobject):
            mobject.move_to(main_sq.get_center())

        def ex_term_updt(mobject):
            mobject.move_to(rect.get_center())

        # def ex_term_half_1_updt(mobject):
        #     mobject.move_to(rect_half_1.get_center())

        # def ex_term_half_2_updt(mobject):
        #     mobject.move_to(rect_half_2.get_center())

        def x_side_updt(mobject):
            mobject.move_to(main_sq.get_center_of_edges()[3])

        def x_1_side_updt(mobject):
            mobject.move_to(main_sq.get_center_of_edges()[2])

        def term_side_updt(mobject):
            mobject.move_to(rect.get_center_of_edges()[0])

        def term_1_side_updt(mobject):
            mobject.move_to(rect.get_center_of_edges()[1])

        ex_sq.add_updater(ex_sq_updt)
        ex_term.add_updater(ex_term_updt)

        x_t.add_updater(x_side_updt)
        x_t_1 = Tex(r"x").set_color(GREY_C).add_updater(x_1_side_updt)

        term_t.add_updater(term_side_updt)
        x_rect_t = x_t.copy().set_color(BLUE_E).add_updater(term_1_side_updt)

        self.wait(2)

        # start of the animation
        self.play(Write(latex_eq))
        self.wait(2)
        self.play(Write(main_sq), run_time=2)

        self.play(Write(x_t), Write(x_t_1))

        # self.play(main_sq.animate.shift(LEFT * 3), run_time=2)

        aux_sq = main_sq.copy()
        under_eq_sq = main_sq.copy().scale(0.1).next_to(latex_eq[0], DOWN, buff=0.2)
        under_eq_rect = rect.copy().scale(0.1).next_to(latex_eq[2], DOWN, buff=0.2)

        # updaters for the little squares
        def under_sq_updt(mobject: Mobject):
            mobject.next_to(latex_eq[0], DOWN, buff=0.2)
            # mobject.next_to(latex_eq.get_part_by_tex("x^2")[0], DOWN, buff=0.2)

        def under_rect_updt(mobject: Mobject):
            mobject.next_to(latex_eq[3], DOWN, buff=0.2)
            # mobject.next_to(latex_eq.get_parts_by_tex(f"{real_x_term}"), DOWN, buff=0.2)

        vg_sq_rect = VGroup(aux_sq, rect).arrange(RIGHT, buff=2)

        under_eq_rect.add_updater(under_rect_updt)
        under_eq_sq.add_updater(under_sq_updt)
        self.wait(2)
        self.play(
            Transform(main_sq, aux_sq),
            TransformFromCopy(main_sq, under_eq_sq),
            run_time=2,
        )

        self.wait()
        self.play(
            Write(rect),
            Write(ex_term),
            run_time=2,
        )
        self.play(
            Write(term_t),
            Write(x_rect_t),
            TransformFromCopy(rect, under_eq_rect),
        )

        # divide rect in half
        rect_half_1 = (
            Rectangle(x_term / 2, x)
            .set_color(BLUE_E)
            .move_to(rect)
            .shift(LEFT * x_term / 4)
        )
        rect_half_2 = (
            Rectangle(x_term / 2, x)
            .set_color(BLUE_E)
            .move_to(rect)
            .shift(RIGHT * x_term / 4)
        )

        def x_half_1_side_updt(mobject):
            mobject.move_to(rect_half_1.get_center_of_edges()[1])

        def x_half_2_side_updt(mobject):
            mobject.move_to(rect_half_2.get_center_of_edges()[1])

        def term_half_1_side_updt(mobject):
            mobject.move_to(rect_half_1.get_center_of_edges()[2])

        def term_half_2_side_updt(mobject):
            mobject.move_to(rect_half_2.get_center_of_edges()[0])

        x_half_1_side = x_t.copy().set_color(BLUE_E).add_updater(x_half_1_side_updt)
        x_half_2_side = x_t.copy().set_color(BLUE_E).add_updater(x_half_2_side_updt)

        term_half_1_side = (
            Tex(f"{real_x_term // 2}")
            .set_color(BLUE_E)
            .add_updater(term_half_1_side_updt)
        )
        term_half_2_side = (
            Tex(f"{real_x_term // 2}")
            .set_color(BLUE_E)
            .add_updater(term_half_2_side_updt)
        )

        self.wait(2)
        self.play(FadeOut(ex_term), FadeOut(term_t), FadeOut(x_rect_t))

        self.wait(2)
        self.play(Write(rect_half_1), run_time=2)
        self.play(Write(rect_half_2), FadeOut(rect), run_time=2)
        self.wait(2)
        self.play(
            Write(x_half_1_side),
            Write(x_half_2_side),
            Write(term_half_1_side),
            Write(term_half_2_side),
        )

        self.wait(4)

        # put all the pieces together

        rect_half_1.generate_target()
        rect_half_1.target.next_to(main_sq, RIGHT, buff=0)

        rect_half_2.generate_target()
        rect_half_2.target.next_to(main_sq, DOWN, buff=0)

        # rearrange to the center
        vg_og_area = VGroup(main_sq, rect_half_1, rect_half_2)
        self.play(
            MoveToTarget(rect_half_1),
            RotatingAndMoveToTarget(
                rect_half_2,
                main_sq,
                DOWN,
                radians=-PI / 2,
            ),
        )

        def x_half_2_side_updt(mobject):
            mobject.move_to(rect_half_2.get_center_of_edges()[3])

        def term_half_2_side_updt(mobject):
            mobject.move_to(rect_half_2.get_center_of_edges()[2])

        x_half_2_side.add_updater(x_half_2_side_updt)
        term_half_2_side.add_updater(term_half_2_side_updt)

        rect_half_2.rotate(PI)

        self.play(
            vg_og_area.animate.move_to(ORIGIN + DOWN * 0.5),
        )

        self.wait(4)

        # add the missing gap 5^2
        square_gap = (
            Square(x_term / 2).set_color(RED_C).next_to(rect_half_1, DOWN, buff=0)
        )

        def gap_sq_updt(mobject):
            mobject.move_to(square_gap.get_center())

        def gap_sq_side_updt(mobject):
            mobject.move_to(square_gap.get_center_of_edges()[0])

        def gap_sq_side_1_updt(mobject):
            mobject.move_to(square_gap.get_center_of_edges()[1])

        ex_term_half_sq.add_updater(gap_sq_updt)
        gap_sq_side = (
            Tex(f"{real_x_term//2}").set_color(RED_E).add_updater(gap_sq_side_updt)
        )
        gap_sq_side_1 = (
            Tex(f"{real_x_term//2}").set_color(RED_E).add_updater(gap_sq_side_1_updt)
        )

        new_latex_eq = (
            Tex(
                f"x",
                "^2",
                "+",
                f"{real_x_term}x",
                "=",
                f"{real_equals}",
                f"+ {(real_x_term//2)**2}",
            )
            .scale(1.3)
            .set_color(BLACK)
            .move_to(self.camera.frame.get_edge_center(UP), coor_mask=[1, 0.9, 0.9])
        )

        new_latex_eq[3][:-1].set_color(BLUE_E)
        new_latex_eq[-1][1:].set_color(RED_C)

        def under_sq_updt(mobject: Mobject):
            mobject.next_to(new_latex_eq[0], DOWN, buff=0.2)

        def under_rect_updt(mobject: Mobject):
            mobject.next_to(new_latex_eq[3], DOWN, buff=0.2)

        self.play(
            Write(square_gap),
            Write(ex_term_half_sq),
            Write(gap_sq_side),
            Write(gap_sq_side_1),
            TransformMatchingTexJ(latex_eq, new_latex_eq),
            run_time=2,
        )

        under_eq_sq.clear_updaters()
        under_eq_sq.add_updater(under_sq_updt)

        under_eq_rect.clear_updaters()
        under_eq_rect.add_updater(under_rect_updt)
        self.wait(2)

        # now, (x+5)^2
        brace_l = Brace(vg_og_area, LEFT).set_color(BLACK)
        brace_d = Brace(vg_og_area, DOWN).set_color(BLACK)

        self.play(Write(brace_d), Write(brace_l), run_time=2)

        ex_plus_half_l = ex_plus_half.copy().next_to(brace_l, LEFT)
        ex_plus_half_d = ex_plus_half.copy().next_to(brace_d, DOWN)

        self.play(
            Write(ex_plus_half_l),
            Write(ex_plus_half_d),
        )
        self.wait(2)

        vg_all = VGroup(vg_og_area, square_gap)
        self.play(
            LaggedStart(
                AnimationGroup(
                    FadeOut(brace_d),
                    FadeOut(ex_plus_half_d),
                    FadeOut(brace_l),
                    FadeOut(ex_plus_half_l),
                ),
                vg_all.animate.shift(LEFT * 5),
                lag_ratio=1,
            ),
            run_time=2,
        )
        self.wait(2)

        # lets solve the equation
        eq_step_1 = (
            Tex(
                f"(x + ",
                f"{real_x_term//2}",
                f") ^ 2 =",
                f"{real_equals}",
                f" + {(real_x_term//2) ** 2}",
                isolate=[
                    f"x + {real_x_term//2}",
                    f"{(real_x_term//2) ** 2}",
                    f"{real_equals}",
                    "^2",
                ],
            )
            .shift(RIGHT * 6 + UP * 3)
            .set_color(BLACK)
            .scale(1.5)
        )
        eq_step_1.set_color_by_tex(f"{(real_x_term//2) ** 2}", RED_C)
        eq_step_1[1].set_color(BLUE_E)
        self.play(Write(eq_step_1))

        frame_x_plus_term = SurroundingRectangle(eq_step_1[3], buff=0.1).set_color(
            BLUE_E
        )

        self.wait(2)

        og_area_indicator = vg_og_area.copy().set_fill(BLUE_E).set_opacity(0.4)
        self.play(
            ShowCreationThenDestruction(frame_x_plus_term, run_time=2),
            FadeIn(og_area_indicator),
        )
        self.play(FadeOut(og_area_indicator), run_time=1 / 4)

        eq_step_2 = (
            Tex(
                f"(x + ",
                f"{real_x_term//2}",
                f") ^ 2",
                f" = ",
                f"{real_equals + (real_x_term // 2) ** 2}",
                isolate=[f"{real_x_term // 2}"],
            )
            .next_to(eq_step_1, DOWN, buff=1)
            .set_color(BLACK)
            .scale(1.5)
        )
        eq_step_2[1].set_color(BLUE_E)

        frame_total_area = SurroundingRectangle(eq_step_2[4], buff=0.1).set_color(RED_C)

        full_area_indicator = vg_all.copy().set_color(RED_C).set_opacity(0.4)

        self.play(Write(eq_step_2))
        self.play(
            FadeIn(full_area_indicator),
            ShowCreationThenDestruction(frame_total_area, run_time=2),
        )
        self.play(FadeOut(full_area_indicator), run_time=1 / 4)
        self.wait(2)

        eq_step_3 = (
            Tex(
                f"x + {real_x_term // 2} = {int(math.sqrt(real_equals + (real_x_term // 2) ** 2))}",
                isolate=[f"{real_x_term // 2}"],
            )
            .next_to(eq_step_2, DOWN, buff=1)
            .set_color(BLACK)
            .scale(1.5)
        )
        eq_step_3.set_color_by_tex(f"{real_x_term//2}", BLUE_E)

        self.play(Write(eq_step_3))
        self.wait(4)

        eq_step_4 = (
            Tex(
                f"x = {int(math.sqrt(real_equals + (real_x_term // 2) ** 2)) - (real_x_term // 2)}"
            )
            .next_to(eq_step_3, DOWN, buff=1)
            .set_color(BLACK)
            .scale(1.5)
        )

        self.play(Write(eq_step_4))
        self.wait(4)

        real_main_sq = Square(real_x).set_color(BLACK).move_to(main_sq)
        real_rect_half_2 = (
            Rectangle(real_x_term / 2, real_x)
            .set_color(BLUE_E)
            .shift(DOWN * 3 + LEFT * real_x_term / 4)
            .move_to(rect_half_2)
        )

        real_rect_half_1 = (
            Rectangle(real_x_term / 2, real_x)
            .set_color(BLUE_E)
            .shift(DOWN * 3 - LEFT * real_x_term / 4)
            .move_to(rect_half_1)
        )

        real_square_gap = Square(real_x_term / 2).set_color(RED_C).move_to(square_gap)

        real_rect_half_1.next_to(real_main_sq, RIGHT, buff=0)
        real_rect_half_2.rotate(PI / 2)
        real_rect_half_2.next_to(real_main_sq, DOWN, buff=0)
        real_square_gap.next_to(real_main_sq, DR, buff=0)

        real_vg_all = (
            VGroup(real_main_sq, real_rect_half_1, real_rect_half_2, real_square_gap)
            .shift(LEFT * 5 + UP * 3)
            # .scale(real_x / x)
            .set_width(vg_all.get_width())
            .set_height(vg_all.get_height())
            .move_to(vg_all)
        )

        self.play(
            FadeOut(x_t),
            AnimationGroup(
                ReplacementTransform(main_sq, real_main_sq),
                ReplacementTransform(rect_half_1, real_rect_half_1),
                ReplacementTransform(rect_half_2, real_rect_half_2),
                ReplacementTransform(square_gap, real_square_gap),
            ),
            run_time=10,
        )

        # end
        self.wait(4)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
