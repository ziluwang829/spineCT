import numpy as np



class Shape():
    def __init__(self, color):
        self.color = color

    def get_color(self) -> tuple:
        return self.color

    def change_color(self, color):
        self.color = color



class Line(Shape):
    def __init__(self, p0, p1, color = (0, 255, 0)):
        super().__init__(color)
        self.p0 = p0
        self.p1 = p1

    def get_points(self):
        return self.p0, self.p1
    
    def change_points(self, p0, p1):
        self.p0 = p0
        self.p1 = p1



class Circle(Shape):
    def __init__(self, p, radius, color = (0, 255, 0)):
        super().__init__(color)
        self.p = p
        self.radius = radius

    def get_point_radius(self):
        return self.p, self.radius
    
    def change_point_radius(self, p, radius):
        self.p = p
        self.radius = radius



class Rect(Shape):
    def __init__(self, p0, p1, color = (0, 255, 0)):
        super().__init__(color)
        self.p0 = p0
        self.p1 = p1

    def get_points(self):
        return self.p0, self.p1
    
    def change_points(self, p0, p1):
        self.p0 = p0
        self.p1 = p1



class Ellipse(Shape):
    def __init__(self, p0, p1, color = (0, 255, 0)):
        super().__init__(color)
        self.p0 = p0
        self.p1 = p1

    def get_points(self):
        return self.p0, self.p1
    
    def change_points(self, p0, p1):
        self.p0 = p0
        self.p1 = p1



class Polygon(Shape):
    def __init__(self, ps, color = (0, 255, 0)):
        super().__init__(color)
        self.ps = ps

    def get_points(self):
        return self.ps
    
    def change_points(self, ps):
        self.ps = ps