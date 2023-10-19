import numpy as np


class Shape():
    # color could be 0: Red, 1: Green, 2: Blue, 3: Yellow
    def __init__(self, ndarray, color):
        self.ndarray = ndarray
        self.color = color
        self.offset = [0, 0]
        self.hide = False
        # need to reduce ndarray to its smallest size  and have the correct offset
        # hide could be used to "detach" an shape from image and move it


    # color could be 0: Red, 1: Green, 2: Blue, 3: Yellow
    def change_color(self, color):
        self.color = color


    def draw_on_array(self, ndarray):
        if self.color == 0:
            c = [255, 0, 0]
        elif self.color == 1:
            c = [0, 255, 0]
        elif self.color == 2:
            c = [0, 0, 255]
        else:
            c = [0, 255, 255]
        ndarray[np.where(self.ndarray > 0)] = np.array(c)
        return ndarray


    def on(self, position):
        return True


    def info(self):
        return str(len(np.where(self.ndarray > 0)[0]))



class Line(Shapes):
    def __init__(self, image_array, start_point, end_point, color):
        super().__init__(image_array)
        self.start_point = start_point
        self.end_point = end_point
        self.color = color

    def draw(self):
        # Implement code to draw a line on the image array
        pass
class Circle(Shapes):
    def __init__(self, image_array, center, radius, color):
        super().__init__(image_array)
        self.center = center
        self.radius = radius
        self.color = color

    def draw(self):
        # Implement code to draw a circle on the image array

class Rectangle(Shapes):
    def __init__(self, image_array, top_left, width, height, color):
        super().__init__(image_array)
        self.top_left = top_left
        self.width = width
        self.height = height
        self.color = color

    def draw(self):
        # Implement code to draw a rectangle on the image array

class Ellipse(Shapes):
    def __init__(self, image_array, center, major_axis, minor_axis, angle, color):
        super().__init__(image_array)
        self.center = center
        self.major_axis = major_axis
        self.minor_axis = minor_axis
        self.angle = angle
        self.color = color

    def draw(self):
        # Implement code to draw an ellipse on the image array

class MultiEdgeShape(Shapes):
    def __init__(self, image_array, points, color):
        super().__init__(image_array)
        self.points = points
        self.color = color

    def draw(self):
        # Implement code to draw a shape with multiple edges on the image array