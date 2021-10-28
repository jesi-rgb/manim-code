from manimlib import *
from numpy import int32, sqrt


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


class SquareUSolution(Scene):
    def construct(self):

        # wait for further instruction to add the texture
        # paper_bg = ImageMobject("paper.jpg").scale(4).set_opacity(0.95)
        # self.add(paper_bg)

        # latex and variables
        # x = -10 + 6 * sqrt(3) ≈ 0.4

        # u^2 + 26u = 27 -> u = 1, v = 27

        x = 1
        x_term = 26
        equals = 27
        x_2 = x_term * x
        main_sq = Square(x).set_color(BLACK)
        rect = Rectangle(x_term, x).shift(DOWN * 3).set_color(BLUE_E)

        latex_eq = (
            Tex(f"(y^3)^2 + {x_term}y^3 = {equals}", isolate=[f"{x_term}"])
            .scale(2)
            .shift(UP * 10)
            .set_color(BLACK)
        )
        latex_eq.set_color_by_tex(f"{x_term}", BLUE_E)

        x_t = Tex(r"y^3").set_color(GREY_C).scale(0.8)
        term_t = Tex(f"{x_term}").set_color(BLUE_E)

        ex_sq = Tex(r"(y^3)^2").set_color(BLACK).scale(2)
        ex_term = Tex(f"{x_term}y^3").set_color(BLUE_E).scale(2)
        ex_term_half = Tex(f"{x_term // 2}y^3").set_color(BLUE_E).scale(2)
        ex_term_half_sq = Tex(f"{(x_term // 2) ** 2}").set_color(RED_C).scale(2)

        ex_plus_half = Tex(
            f"(y^3 + {x_term // 2})", isolate=f"{x_term // 2}"
        ).set_color(BLACK)
        ex_plus_half.set_color_by_tex(f"{x_term // 2}", RED_C)

        def ex_sq_updt(mobject):
            mobject.move_to(main_sq.get_center())

        def ex_term_updt(mobject):
            mobject.move_to(rect.get_center())

        def ex_term_half_1_updt(mobject):
            mobject.move_to(rect_half_1.get_center())

        def ex_term_half_2_updt(mobject):
            mobject.move_to(rect_half_2.get_center())

        def x_side_updt(mobject):
            mobject.move_to(main_sq.get_center_of_edges()[1])

        def x_1_side_updt(mobject):
            mobject.move_to(main_sq.get_center_of_edges()[2])

        def term_side_updt(mobject):
            mobject.move_to(rect.get_center_of_edges()[0])

        def term_1_side_updt(mobject):
            mobject.move_to(rect.get_center_of_edges()[1])

        ex_sq.add_updater(ex_sq_updt)
        ex_term.add_updater(ex_term_updt)

        # x_t.add_updater(x_side_updt)
        x_t_1 = x_t.copy()  # .add_updater(x_1_side_updt)

        term_t.add_updater(term_side_updt)
        x_rect_t = x_t.copy().set_color(BLUE_E).add_updater(term_1_side_updt)

        self.play(self.camera.frame.animate.shift(OUT * 30))

        self.wait(2)

        # start of the animation

        self.play(Write(latex_eq))
        self.wait(2)
        self.play(
            Write(main_sq),
            run_time=2,
        )

        self.play(
            ShowCreationThenDestruction(x_t.shift(RIGHT * 1), time_width=20),
            ShowCreationThenDestruction(x_t_1.shift(DOWN * 1), time_width=20),
            run_time=3,
        )

        self.wait(2)
        self.play(main_sq.animate.shift(UP * 3), run_time=2)
        self.wait(2)
        self.play(Write(rect), run_time=2)
        self.play(
            ShowCreationThenDestruction(
                term_t,
                time_width=10,
            ),
            ShowCreationThenDestruction(
                x_rect_t.move_to(rect.get_center_of_edges()[1]),
                time_width=10,
            ),
            run_time=5,
        )

        # divide rect in half
        rect_half_1 = (
            Rectangle(x_term / 2, x)
            .set_color(BLUE_E)
            .shift(DOWN * 3 + LEFT * x_term / 4)
        )
        rect_half_2 = (
            Rectangle(x_term / 2, x)
            .set_color(BLUE_E)
            .shift(DOWN * 3 - LEFT * x_term / 4)
        )

        def x_half_1_side_updt(mobject):
            mobject.move_to(rect_half_1.get_center_of_edges()[3])

        def x_half_2_side_updt(mobject):
            mobject.move_to(rect_half_2.get_center_of_edges()[3])

        def term_half_1_side_updt(mobject):
            mobject.move_to(rect_half_1.get_center_of_edges()[2])

        def term_half_2_side_updt(mobject):
            mobject.move_to(rect_half_2.get_center_of_edges()[0])

        x_half_1_side = x_t.copy().set_color(BLUE_E).add_updater(x_half_1_side_updt)
        x_half_2_side = x_t.copy().set_color(BLUE_E).add_updater(x_half_2_side_updt)

        term_half_1_side = (
            Tex(f"{x_term // 2}").set_color(BLUE_E).add_updater(term_half_1_side_updt)
        )
        term_half_2_side = (
            Tex(f"{x_term // 2}").set_color(BLUE_E).add_updater(term_half_2_side_updt)
        )

        self.wait(2)
        # self.play(FadeOut(ex_term), FadeOut(term_t), FadeOut(x_rect_t))

        ex_term_half.add_updater(ex_term_half_1_updt)
        ex_term_half_2 = ex_term_half.copy().add_updater(ex_term_half_2_updt)

        self.wait(2)
        self.play(Write(rect_half_1), run_time=2)
        self.play(Write(rect_half_2), FadeOut(rect), run_time=2)
        self.play(
            Write(x_half_1_side),
            Write(x_half_2_side),
            Write(term_half_1_side),
            Write(term_half_2_side),
        )

        # put all the pieces together

        # self.play(main_sq.animate.shift(UP * 4 + RIGHT * 3))

        rect_half_1.generate_target()
        rect_half_1.target.next_to(main_sq, LEFT, buff=0)
        self.play(MoveToTarget(rect_half_1), run_time=1.5)

        self.play(Rotate(rect_half_2, angle=PI / 2))
        rect_half_2.generate_target()
        rect_half_2.target.next_to(main_sq, DOWN, buff=0)
        self.play(MoveToTarget(rect_half_2), run_time=1.5)

        # rearrange to the center
        vg_og_area = VGroup(main_sq, rect_half_1, rect_half_2)
        self.play(vg_og_area.animate.move_to(ORIGIN + DOWN * 0.5))

        self.wait(4)

        # add the missing gap 5^2
        print(f"{x_2=}")
        square_gap = (
            Square(x_term / 2).set_color(RED_C).next_to(rect_half_1, DOWN, buff=0)
        )

        def gap_sq_updt(mobject):
            mobject.move_to(square_gap.get_center())

        def gap_sq_side_updt(mobject):
            mobject.move_to(square_gap.get_center_of_edges()[0])

        def gap_sq_side_1_updt(mobject):
            mobject.move_to(square_gap.get_center_of_edges()[3])

        ex_term_half_sq.add_updater(gap_sq_updt)
        gap_sq_side = Tex(f"{x_term//2}").set_color(RED_E).add_updater(gap_sq_side_updt)
        gap_sq_side_1 = (
            Tex(f"{x_term//2}").set_color(RED_E).add_updater(gap_sq_side_1_updt)
        )

        self.play(
            Write(square_gap),
            Write(ex_term_half_sq),
            Write(gap_sq_side),
            Write(gap_sq_side_1),
            run_time=2,
        )
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
            FadeOut(brace_d),
            FadeOut(brace_l),
            FadeOut(ex_plus_half_d),
            FadeOut(ex_plus_half_l),
            vg_all.animate.shift(LEFT * 5),
        )
        self.wait(2)

        # lets solve the equation
        eq_step_1 = (
            Tex(
                f"(y^3 + ",
                f"{x_term//2}",
                f") ^ 2 =",
                f"{equals}",
                f" + {(x_term//2) ** 2}",
                isolate=[f"u + {x_term//2}", f"{(x_term//2) ** 2}", f"{equals}", "^2"],
            )
            .shift(RIGHT * 10 + UP * 3)
            .set_color(BLACK)
            .scale(2)
        )
        eq_step_1.set_color_by_tex(f"{(x_term//2) ** 2}", RED_C)
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
                f"(y^3 + ",
                f"{x_term//2}",
                f") ^ 2",
                f" = ",
                f"{equals + (x_term // 2) ** 2}",
            )
            .next_to(eq_step_1, DOWN, buff=1)
            .set_color(BLACK)
            .scale(2)
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
                f"y^3 + {x_term // 2} = \pm \sqrt{ {equals + (x_term // 2) ** 2} }",
                # isolate=[f"{x_term // 2}"],
            )
            .next_to(eq_step_2, DOWN, buff=1)
            .set_color(BLACK)
            .scale(2)
        )
        # eq_step_3.set_color_by_tex(f"{x_term//2}", BLUE_E)

        self.play(Write(eq_step_3))
        self.wait(4)

        eq_step_4 = (
            Tex(
                f"y^3 = \pm { {int(sqrt(equals + (x_term // 2) ** 2))} } - {x_term // 2}",
                # isolate=[f"{x_term // 2}"],
            )
            .next_to(eq_step_3, DOWN, buff=1)
            .set_color(BLACK)
            .scale(2)
        )

        eq_u_1 = (
            Tex(
                f"y^3_1 = {int(math.sqrt(equals + (x_term // 2) ** 2) - (x_term // 2))}",
                R"\rightarrow y_1 = 1",
            )
            .next_to(eq_step_4, DOWN, buff=1)
            .set_color(BLACK)
            .scale(2)
        )
        eq_u_2 = (
            Tex(
                f"y^3_2 = {int(-(math.sqrt(equals + (x_term // 2) ** 2)) - (x_term // 2))}",
                R"\rightarrow y_2 = \sqrt[3]{%d}"
                % int(-(math.sqrt(equals + (x_term // 2) ** 2)) - (x_term // 2)),
            )
            .next_to(eq_u_1, DOWN, buff=1)
            .set_color(BLACK)
            .scale(2)
        )

        # eq_final_u = (
        #     Tex(R"u=\sqrt{108}-10 \\ u=-10+6\sqrt{3}")
        #     .next_to(eq_step_3, DOWN, buff=1)
        #     .set_color(BLACK)
        #     .scale(2)
        # )

        self.play(Write(eq_step_4))
        self.wait(1)
        self.play(Write(eq_u_1))
        self.play(Write(eq_u_2))

        self.wait(4)
