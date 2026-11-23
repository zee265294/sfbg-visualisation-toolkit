"""Source-faithful Cairo frame renderer without any text or labelling feature."""
from math import cos,sin,pi
import cairo
from particle_style import ParticleStyler,line,upward_arrow,smooth
from geometry import Vessel
from particles import ParticleField
from spray import SprayField
from mechanisms import MechanismScene


class FullSFBG:
    logical_width=360.0
    logical_height=640.0

    def __init__(self,cfg):
        self.cfg=cfg
        self.vessel=Vessel(cfg.geometry)
        self.particles=ParticleField(cfg,self.vessel)
        self.spray=SprayField(cfg,self.vessel,self.particles)
        self.styler=ParticleStyler()

    def draw(self,c,fi):
        p=self.particles
        x,y,r=p.x,p.y,p.r
        b,sides,cluster,modes,stage=p.b,p.sides,p.cluster,p.modes,p.stage
        C=self.vessel.centre
        F=self.cfg.frames
        n=p.n
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        # Faint, slowly rising evaporation traces from the original SFBG code.
        for j in range(19):
            q=(fi/F*3+j*.618034)%1
            v=390-369*q
            u=C+53*sin(j*5.16)+12*sin(q*4+j)+q*19*sin(j)
            c.set_source_rgba(.35,.49,.53,.33*sin(pi*q)**.7)
            c.set_line_width(.9)
            c.move_to(u,v)
            c.curve_to(u+4,v-6,u-4,v-10,u-1,v-17)
            c.stroke()
        for j in range(19):
            q=(fi/F*4+j*.618)%1
            v=546-450*q
            u=C+sin(j*32.6)*(.75*float(self.vessel.half(v)))+3*sin(q*5+j)
            upward_arrow(c,u,v,13,1,.22*sin(pi*q))
        for i in range(-2,3):
            q=(fi/F*8+.12*(i%2))%1
            for m in [0,1]:
                t=(q+m)/2
                upward_arrow(c,C+i*29,623-64*t,16,2.05,
                             .85*sin(pi*t)**.75,(.81,.23,.2))
        for i in [-1,0,1]:
            q=(fi/F*6+.17*(i%2))%1
            for m in [0,1]:
                t=(q+m)/2
                upward_arrow(c,C+i*68,108-85*t,17,2,
                             .78*sin(pi*t)**.8,(.46,.5,.52))
        self.spray.draw_drops(c,fi)

        def draw_grain(j):
            u,v=x[fi,j],y[fi,j]
            rr=r[j]
            w=self.spray.wet[fi,j]
            if j<12:
                phase=stage[fi,j]
                apart=smooth((phase-.73)/.19) if phase>.7 else 1-smooth((phase-.18)/.068)
                angle=-.5+1.8*sin(b[fi,j]-.8)
                sep=rr*(1.5+3.05*apart)
                self.styler.grain(c,u+sides[j]*sep*cos(angle),v+sep*sin(angle),rr*.81,0,w*.74)
            if cluster[j]:
                angle=b[fi,j]+modes[j]
                self.styler.grain(c,u+rr*cos(angle),v+rr*sin(angle),rr*.82,int(j%3==1),w)
            self.styler.grain(c,u,v,rr,int(j%3==1),w)

        # Event actors are layered between the two halves of the population.
        for j in range(12,n//2):
            draw_grain(j)
        for j in p.actor:
            draw_grain(j)
        for j in range(n//2,n):
            draw_grain(j)
        self.vessel.draw(c,line)
        self.spray.draw_equipment(c)

    def frame(self,index):
        s=cairo.ImageSurface(cairo.FORMAT_RGB24,self.cfg.width,self.cfg.height)
        c=cairo.Context(s)
        c.set_source_rgb(1,1,1)
        c.paint()
        scale=min(self.cfg.width/self.logical_width,self.cfg.height/self.logical_height)
        c.translate((self.cfg.width-self.logical_width*scale)/2,
                    (self.cfg.height-self.logical_height*scale)/2)
        c.scale(scale,scale)
        self.draw(c,index%self.cfg.frames)
        return s


def create_scene(cfg):
    cfg.validate()
    if cfg.scene=='full':
        return FullSFBG(cfg)
    return MechanismScene(cfg)
