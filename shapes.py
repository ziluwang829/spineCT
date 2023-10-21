import numpy as np



class Shape():
    def __init__(self, ndarray, offset, color = np.array([0, 255, 0]).astype(np.uint8)):
        self.matrix = ndarray
        self.color = color
        self.offset = offset
        self.hide = False
        # need to reduce ndarray to its smallest size  and have the correct offset
        # hide could be used to "detach" an shape from image and move it

    def get_matrix(self):
        return self.matrix

    def get_color(self):
        return self.color
    
    def get_offset(self):
        return self.offset
    
    def get_hide(self):
        return self.hide

    def get_matrix(self, matrix):
        self.matrix = matrix

    def change_color(self, color):
        self.color = color

    def change_offset(self, offset):
        self.offset = offset

    def change_hide(self, hide):
        self.hide = hide








# class Line(Shapes):
#     def __init__(self, image_array, start_point, end_point, color):
#         super().__init__(image_array)
#         self.start_point = start_point
#         self.end_point = end_point
#         self.color = color

#     def draw(self):
#         # Implement code to draw a line on the image array
#         pass
# class Circle(Shapes):
#     def __init__(self, image_array, center, radius, color):
#         super().__init__(image_array)
#         self.center = center
#         self.radius = radius
#         self.color = color

#     def draw(self):
#         # Implement code to draw a circle on the image array

# class Rectangle(Shapes):
#     def __init__(self, image_array, top_left, width, height, color):
#         super().__init__(image_array)
#         self.top_left = top_left
#         self.width = width
#         self.height = height
#         self.color = color

#     def draw(self):
#         # Implement code to draw a rectangle on the image array

# class Ellipse(Shapes):
#     def __init__(self, image_array, center, major_axis, minor_axis, angle, color):
#         super().__init__(image_array)
#         self.center = center
#         self.major_axis = major_axis
#         self.minor_axis = minor_axis
#         self.angle = angle
#         self.color = color

#     def draw(self):
#         # Implement code to draw an ellipse on the image array

# class MultiEdgeShape(Shapes):
#     def __init__(self, image_array, points, color):
#         super().__init__(image_array)
#         self.points = points
#         self.color = color

#     def draw(self):
#         # Implement code to draw a shape with multiple edges on the image array