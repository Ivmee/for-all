from manim import *

class GroupRotation(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        square = Square(color=GREEN)

        group = VGroup(circle, square)
        group.arrange(RIGHT)

        self.play(FadeIn(group))
        self.wait(0.5)

        # Вращаем всю группу
        self.play(Rotate(group, angle=PI))
        self.wait()