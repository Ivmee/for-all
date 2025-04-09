from manim import *
class makeText(Scene):
    def construct(self):
        first_line = Text("Hello manim!")
        self.wait(1)
        self.play(Write(first_line))
        self.wait(1)
        self.play(first_line.animate.to_corner(UP + RIGHT))
        self.play(FadeOut(first_line))
        self.wait(2)