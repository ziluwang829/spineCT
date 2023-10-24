import numpy as np
import cv2
import copy

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

    def __repr__(self):
        l = np.linalg.norm(np.array(self.p0) - np.array(self.p1))
        return "L: " + str(round(float(l), 5))
    
    def get_left(self):
        if self.p0[0] < self.p1[0]:
            return self.p0, np.arctan2(self.p0[0] - self.p1[0], self.p0[1] - self.p1[1])
        else:
            return self.p1, np.arctan2(self.p1[0] - self.p0[0], self.p1[1] - self.p0[1])
        
    def draw(self, array, w, h):
        img = cv2.line(array, (w // 2 + self.p0[0], h // 2 + self.p0[1]), \
                              (w // 2 + self.p1[0], h // 2 + self.p1[1]), \
                               color = self.color, thickness = 1)
        return img
    
    def click(self, array, w, h, p):
        img = cv2.line(array, (w // 2 + self.p0[0], h // 2 + self.p0[1]), \
                              (w // 2 + self.p1[0], h // 2 + self.p1[1]), 
                              color = self.color, thickness = 1)
        return np.sum(img[h // 2 + p[1]-3:h // 2 + p[1]+3, w // 2 + p[0]-3:w // 2 + p[0]+3]) > 0

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

    def draw(self, array, w, h):
        img = cv2.circle(array, (w // 2 + self.p[0], h // 2 + self.p[1]), \
                               self.radius, color = self.color, thickness = 1)
        return img

    def click(self, array, w, h, p):
        p0 = self.p
        img = cv2.circle(array, (w // 2 + p0[0], h // 2 + p0[1]), \
                         self.radius, color = self.color, thickness = 1)
        return np.sum(img[h // 2 + p[1]-3:h // 2 + p[1]+3, w // 2 + p[0]-3:w // 2 + p[0]+3]) > 0

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

    def draw(self, array, w, h):
        img = cv2.rectangle(array, (w // 2 + self.p0[0], h // 2 + self.p0[1]), \
                                   (w // 2 + self.p1[0], h // 2 + self.p1[1]), \
                                    color = self.color, thickness = 1)
        return img

    def click(self, array, w, h, p):
        img = cv2.rectangle(array, (w // 2 + self.p0[0], h // 2 + self.p0[1]), \
                                   (w // 2 + self.p1[0], h // 2 + self.p1[1]), \
                                    color = self.color, thickness = 1)
        return np.sum(img[h // 2 + p[1]-3:h // 2 + p[1]+3, w // 2 + p[0]-3:w // 2 + p[0]+3]) > 0

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

    def draw(self, array, w, h):
        p0 = (w // 2 + self.p0[0], h // 2 + self.p0[1])
        p1 = (w // 2 + self.p1[0], h // 2 + self.p1[1])
        rr = cv2.RotatedRect(p0, (p0[0], p1[1]), p1)
        img = cv2.ellipse(array, rr, color = self.color, thickness = 1)
        return img

    def click(self, array, w, h, p):
        p0 = (w // 2 + self.p0[0], h // 2 + self.p0[1])
        p1 = (w // 2 + self.p1[0], h // 2 + self.p1[1])
        rr = cv2.RotatedRect(p0, (p0[0], p1[1]), p1)
        img = cv2.ellipse(array, rr, color = self.color, thickness = 1)
        return np.sum(img[h // 2 + p[1]-3:h // 2 + p[1]+3, w // 2 + p[0]-3:w // 2 + p[0]+3]) > 0

class Polygon(Shape):
    def __init__(self, ps, color = (0, 255, 0)):
        super().__init__(color)
        self.ps = ps

    def get_points(self):
        return self.ps
    
    def change_points(self, ps):
        self.ps = ps

    def draw(self, array, w, h):
        if len(self.ps) == 0:
            return array
        elif len(self.ps) <= 2:
            img = copy.deepcopy(array)
            ps = [[w // 2 + p[0], h // 2 + p[1]] for p in self.ps]
            for p in ps:
                img[p[1], p[0]] = [0, 255, 0]
            return img
        else:
            ps = [[w // 2 + p[0], h // 2 + p[1]] for p in self.ps]
            ps = np.array(ps)
            ps = ps.reshape(1, -1, 2)
            img = cv2.polylines(array, [ps], True, color = self.color, thickness = 1)
            return img

    def click(self, array, w, h, p):
        if len(self.ps) <= 2:
            return False
        else:
            ps = [[w // 2 + p[0], h // 2 + p[1]] for p in self.ps]
            ps = np.array(ps)
            ps = ps.reshape(1, -1, 2)
            img = cv2.polylines(array, [ps], True, color = self.color, thickness = 1)
            return np.sum(img[h // 2 + p[1]-3:h // 2 + p[1]+3, w // 2 + p[0]-3:w // 2 + p[0]+3]) > 0