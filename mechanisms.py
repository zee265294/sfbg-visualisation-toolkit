"""Vessel-free close-up examples using the same grey particle sprite renderer.

Mechanism scenes are *illustrative*. They show mass-equivalent fragment radii
for binary/ternary breakage, but do not solve contact mechanics or PBEs.
"""
from math import sin,cos,pi
import numpy as np
import cairo
from particle_style import ParticleStyler,upward_arrow,smooth


class MechanismScene:
    world_width=960
    world_height=320

    def __init__(self,cfg,styler=None):
        self.cfg=cfg
        self.styler=styler or ParticleStyler()
        rng=np.random.default_rng(cfg.seed)
        self.x=rng.uniform(12,948,52)
        self.y=rng.uniform(52,284,52)
        self.r=rng.uniform(3.0,7.0,52)
        self.phase=rng.uniform(0,2*pi,52)

    def _sphere(self,c,x,y,r,a=1,depth=0,wet=0):
        if a<=0:
            return
        c.save()
        c.push_group()
        self.styler.grain(c,x,y,r,depth,wet)
        c.pop_group_to_source()
        c.paint_with_alpha(min(1,max(0,a)))
        c.restore()

    def draw(self,c,f):
        cycle=(f/self.cfg.frames*4)%1
        phase=cycle
        # Air up, binder down: visual cues only, not a simulated flow field.
        for i in range(8):
            xx=70+i*118
            p=(f/self.cfg.frames*8+i*.18)%1
            upward_arrow(c,xx,276-190*p,15,1.8,.27*sin(pi*p),(0.81,0.23,0.2))
        for i in range(52):
            x=self.x[i]+8*sin(self.phase[i]+2*pi*f/self.cfg.frames)
            y=self.y[i]+13*sin(self.phase[i]+8*pi*f/self.cfg.frames)
            self._sphere(c,x,y,self.r[i],a=.37,depth=i%2)
        if self.cfg.scene=='binary_aggregation':
            # Two wet particles coalesce, with equivalent-volume output radius.
            s=smooth((phase-.10)/.30)
            r0=35
            distance=88*(1-s)
            if phase<.48:
                alpha=min(1,phase/.10)
                self._sphere(c,480-distance,155,r0,alpha,wet=.75)
                self._sphere(c,480+distance,155,r0,alpha,wet=.75)
            else:
                r1=r0*2**(1/3)
                y=155+125*smooth((phase-.48)/.46)
                self._sphere(c,480,y,r1,min(1,(1-phase)/.09) if phase>.91 else 1,wet=.60)
        elif self.cfg.scene=='binary_breakage':
            r0=42
            if phase<.41:
                self._sphere(c,480,204,r0,min(1,phase/.09))
                if .27<phase<.41:
                    c.set_source_rgba(.70,.24,.21,.65)
                    c.set_line_width(2.2)
                    c.move_to(480,180);c.line_to(473,195);c.line_to(487,207);c.line_to(477,225);c.stroke()
            else:
                u=smooth((phase-.41)/.50)
                r1=r0/2**(1/3)
                a=min(1,(1-phase)/.08) if phase>.92 else 1
                self._sphere(c,480-75*u,204-110*u,r1,a)
                self._sphere(c,480+75*u,204-110*u,r1,a)
        else:
            # Collider z is *not* itself fragmented. It impacts parent y;
            # parent y fragments into three products x1,x2,x3.
            rparent=42
            zrad=23
            if phase<.4:
                xz=330+110*smooth((phase-.02)/.37)
                self._sphere(c,480,190,rparent,min(1,phase/.09))
                self._sphere(c,xz,190,zrad,min(1,phase/.09),wet=.2)
            else:
                u=smooth((phase-.4)/.5)
                daughter=rparent/3**(1/3)
                a=min(1,(1-phase)/.08) if phase>.92 else 1
                for dx,dy in [(-84,-65),(3,-112),(84,-59)]:
                    self._sphere(c,480+dx*u,190+dy*u,daughter,a)
                # Incoming z remains intact, deflects left/down after impact.
                self._sphere(c,440-80*u,190+30*u,zrad,a,wet=.2)

    def frame(self,index):
        s=cairo.ImageSurface(cairo.FORMAT_RGB24,self.cfg.width,self.cfg.height)
        c=cairo.Context(s)
        c.set_source_rgb(1,1,1);c.paint()
        # preserve aspect ratio in horizontal mechanism strips
        scale=min(self.cfg.width/self.world_width,self.cfg.height/self.world_height)
        c.translate((self.cfg.width-self.world_width*scale)/2,
                    (self.cfg.height-self.world_height*scale)/2)
        c.scale(scale,scale)
        self.draw(c,index)
        return s
