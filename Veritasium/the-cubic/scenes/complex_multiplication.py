from manimlib import *


class ComplexMultiplication(Scene):
    def construct(self):
        nl = NumberLine(x_range=[-10, 10], width=16, include_numbers=True).set_color(
            BLACK
        )
        nl.numbers.set_color(BLACK)

        dot = Dot(nl.n2p(3)).set_color(BLUE_D)
        dot_negative = Dot(nl.n2p(-3)).set_color(BLUE_D)
        tex_dot = Tex("3").set_color(BLUE_D).scale(0.6).next_to(dot, UR, buff=0.1)
        tex_dot_negative = (
            Tex("-3").set_color(BLUE_D).scale(0.6).next_to(dot_negative, UR, buff=0.1)
        )

        self.play(Write(nl), run_time=2)
        self.play(Write(dot), Write(tex_dot), run_time=2)

        self.wait(2)

        arc_arrow = CurvedArrow(
            dot.get_center(),
            end_point=dot_negative.get_center(),
            angle=PI,
            tip_config={"tip_style": 1},
            stroke_width=1,
        ).set_color(BLACK)

        arc_180 = Arc(0, PI, arc_center=nl.n2p(0)).set_color(BLUE_D)
        hundred_eighty_deg = (
            Tex(R"180^{\circ}")
            .set_color(BLUE_D)
            .scale(0.6)
            .next_to(arc_180, UR, buff=0.01)
        )

        self.play(
            ShowCreationThenDestruction(arc_arrow),
            Write(dot_negative),
            Write(tex_dot_negative),
            Write(arc_180),
            Write(hundred_eighty_deg),
            FadeOut(dot),
            FadeOut(tex_dot),
            run_time=2,
        )

        self.wait(2)
        self.play(FadeOut(arc_180), FadeOut(hundred_eighty_deg))

        # repeat backwards

        arc_arrow = CurvedArrow(
            dot_negative.get_center(),
            end_point=dot.get_center(),
            angle=PI,
            tip_config={"tip_style": 1},
            stroke_width=1,
        ).set_color(BLACK)

        arc_180 = Arc(0, -PI, arc_center=nl.n2p(0)).set_color(BLUE_D).flip()
        hundred_eighty_deg = (
            Tex(R"-180^{\circ}")
            .set_color(BLUE_D)
            .scale(0.6)
            .next_to(arc_180, DL, buff=0.01)
        )

        self.play(
            ShowCreationThenDestruction(arc_arrow),
            Write(dot),
            Write(tex_dot),
            Write(arc_180),
            Write(hundred_eighty_deg),
            FadeOut(dot_negative),
            FadeOut(tex_dot_negative),
            run_time=2,
        )

        self.wait(4)

        self.play(
            FadeOut(nl),
            FadeOut(dot),
            FadeOut(tex_dot),
            FadeOut(arc_180),
            FadeOut(hundred_eighty_deg),
            run_time=2,
        )

        self.wait(1)

        c_plane = (
            ComplexPlane(
                faded_line_ratio=1,
                include_numbers=True,
                x_range=[-10, 10],
                y_range=[-10, 10],
                axis_config={
                    "stroke_width": 3,
                    "include_numbers": True,
                },
            )
            .set_opacity(0.5)
            .set_color(GREY_D)
        )

        self.play(Write(c_plane))

        self.wait(2)

        def iterate_complex(start_angle: float, current_dot: Dot):
            curr_number = c_plane.p2n(current_dot.get_center())
            next_number = curr_number * 1j
            new_dot = Dot(c_plane.n2p(next_number)).set_color(BLUE_D)
            new_tex = (
                Tex(str(f"{next_number:.0f}").replace("j", "i"))
                .scale(0.6)
                .set_color(BLUE_D)
                .set_stroke("#FFF4D7", width=10, background=True)
                .next_to(new_dot, UP, buff=0.1)
            )

            arc = Arc(start_angle=start_angle, arc_center=c_plane.n2p(0)).set_color(
                BLUE_D
            )

            arc_arrow = CurvedArrow(
                current_dot.get_center(),
                new_dot.get_center(),
                angle=PI / 2,
                tip_config={"tip_style": 1},
                stroke_width=1,
            ).set_color(BLACK)

            return new_dot, new_tex, arc, arc_arrow

        last_dot = Dot(c_plane.n2p(complex(3))).set_color(BLUE_D)
        last_tex = (
            Tex("3 + 0i")
            .scale(0.6)
            .set_color(BLUE_D)
            .set_stroke("#FFF4D7", width=10, background=True)
            .next_to(last_dot, UP, buff=0.1)
        )
        self.play(Write(last_dot), Write(last_tex))
        self.wait(2)

        for angle in [0, PI / 2, PI, 3 * PI / 2]:
            new_dot, new_tex, arc, arc_arrow = iterate_complex(angle, last_dot)
            self.play(
                Write(new_dot),
                Write(new_tex),
                FadeOut(last_dot),
                FadeOut(last_tex),
                Write(arc),
                ShowCreationThenDestruction(arc_arrow),
            )
            last_dot = new_dot
            last_tex = new_tex
            self.wait(3)

        self.wait(4)

        self.play(FadeOut(c_plane), *[FadeOut(mob) for mob in self.mobjects])
        self.wait(3)
