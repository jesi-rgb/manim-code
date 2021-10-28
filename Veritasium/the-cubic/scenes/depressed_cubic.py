from functools import update_wrapper
from manimlib import *
from numpy import cbrt, sqrt

# x^3 = 15x + 4
# x^3 = cx + d
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
