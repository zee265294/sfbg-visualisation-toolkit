"""The same matte grey sphere sprite algorithm as the supplied sfbg_animation.py."""
from math import pi
import cairo

class ParticleStyler:
    def __init__(self):
        self.sprites={}

    def grain(self,c,u,v,rad,depth=0,w=0):
        sz=round(rad*3)
        shade=round(w*5)
        key=(sz,depth,shade)
        if key not in self.sprites:
            rr=sz/3
            side=max(24,int(4*rr+5))  # large close-up granules, no sprite clipping
            s=cairo.ImageSurface(cairo.FORMAT_ARGB32,side,side)
            z=cairo.Context(s)
            z.translate(side/2,side/2)
            z.scale(2,2)
            grad=cairo.RadialGradient(-0.32*rr,-0.41*rr,0.02*rr,-0.06*rr,-0.08*rr,rr*1.14)
            for pos,val in [(0,0.9),(0.48,0.79),(1,0.57)]:
                val += 0.06*depth-0.035*shade-0.14
                grad.add_color_stop_rgb(pos,val-0.017,val,val+0.012+0.003*shade)
            z.arc(0,0,rr,0,2*pi)
            z.set_source(grad)
            z.fill_preserve()
            z.set_line_width(0.38)
            z.set_source_rgba(0.26,0.3,0.32,0.63)
            z.stroke()
            self.sprites[key]=s
        c.save()
        side=self.sprites[key].get_width()
        c.translate(u-side/4,v-side/4)
        c.scale(0.5,0.5)
        c.set_source_surface(self.sprites[key])
        c.paint()
        c.restore()


def line(c,points,color,width):
    c.set_source_rgb(*color)
    c.set_line_width(width)
    c.move_to(*points[0])
    for p in points[1:]:
        c.line_to(*p)
    c.stroke()


def upward_arrow(c,x,y,length,width,alpha,col=(0.32,0.68,0.83)):
    c.set_source_rgba(*col,alpha)
    c.set_line_width(width)
    c.move_to(x,y+length)
    c.line_to(x,y+2)
    c.stroke()
    w=width*2.5
    c.move_to(x,y)
    c.line_to(x-w,y+w*1.4)
    c.line_to(x+w,y+w*1.4)
    c.close_path()
    c.fill()


def polygon(c,pts,col):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()
    c.set_source_rgb(*col)
    c.fill()


def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)
