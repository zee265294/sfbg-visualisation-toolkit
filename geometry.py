"""Two adjustable vessel contours.  Original tapered geometry is preserved."""
import numpy as np

STEEL=(0.25,0.3,0.33)

class Vessel:
    centre=167.0
    top=86.0
    base=550.0
    base_half=79.0
    top_half=126.4

    def __init__(self, kind='tapered'):
        if kind not in ('tapered','rectangular'):
            raise ValueError(kind)
        self.kind=kind

    def half(self, y):
        if self.kind=='rectangular':
            return np.zeros_like(y, dtype=float)+self.base_half
        return self.base_half+47.4*(self.base-y)/(self.base-self.top)

    def draw(self, c, line):
        for sign in [-1,1]:
            line(c, [(self.centre+sign*float(self.half(self.top)),self.top),
                     (self.centre+sign*self.base_half,self.base)], STEEL, 2.6)
        c.rectangle(self.centre-self.base_half,self.base,2*self.base_half,6)
        c.set_source_rgb(0.78,0.81,0.82)
        c.fill_preserve()
        c.set_source_rgb(*STEEL)
        c.set_line_width(1.45)
        c.stroke()
        for dx in range(-72,73,9):
            c.rectangle(self.centre+dx-1.05,self.base+0.3,2.1,5.4)
            c.set_source_rgb(0.93,0.98,1)
            c.fill()

    def nozzle_point(self, spray):
        y=self.top+spray.nozzle_y*(self.base-self.top)
        h=float(self.half(y))
        x=self.centre+(2*spray.nozzle_x-1)*h
        return x,y

    def is_inside(self,x,y,radius=0):
        return (np.abs(x-self.centre)+radius < self.half(y)) & (y+radius < self.base) & (y-radius > self.top)
