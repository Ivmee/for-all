
from manim import *


class Shapes(Scene):
    def construct(self):

        circle = Circle()
        square = Square()
        triangle=Polygon(np.array([0,0,0]),np.array([1,1,0]),np.array([1,-1,0]))
        self.play(Create(circle))
        self.play(FadeOut(circle))
        self.play(GrowFromCenter(square))
        self.play(Transform(square,triangle))