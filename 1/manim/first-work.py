
from manim import *


class Shapes(Scene):
    def construct(self):

        circle = Circle()
        square = Square()
        self.play(GrowFromCenter(circle))
        self.play(Transform(circle,square))
        self.play(FadeOut(square))