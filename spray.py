"""Liquid binder: independently specified pipe entry, nozzle position, and direction.

When left at its defaults, this follows the source script's *same droplet deposition
algorithm*, generating the same trajectories and wetting masks.
"""
from math import cos, sin, pi
import numpy as np
from particle_style import line, polygon
from geometry import STEEL


class SprayField:
    def __init__(self, cfg, vessel, field):
        self.cfg=cfg.spray
        self.vessel=vessel
        self.field=field
        self.drops=[[] for _ in range(cfg.frames)]
        self.wet=np.zeros((cfg.frames,field.n))
        self.enabled=self.cfg.enabled
        self.nx,self.ny=vessel.nozzle_point(self.cfg)
        if self.enabled:
            self._build()

    def _default(self):
        s=self.cfg
        return (s.entry=='right' and s.direction=='down' and
                abs(self.nx-167)<1e-7 and abs(self.ny-172)<1e-7)

    def _build(self):
        f=self.field
        rng=f.rng; F=f.f
        x,y,r=f.x,f.y,f.r
        C=self.vessel.centre
        default=self._default()
        if self.cfg.direction=='down':
            vx,vy=0,1
        elif self.cfg.direction=='up':
            vx,vy=0,-1
        elif self.cfg.direction=='left':
            vx,vy=-1,0
        else:
            vx,vy=1,0
        start_x,start_y=self.nx+vx*2,self.ny+vy*2

        def deposit(end,j,dur,featured=False):
            xx,yy=x[end,j],y[end,j]-r[j] if default else y[end,j]
            hit=None
            for k in range(dur+1):
                t=k/dur
                fi=(end-dur+k)%F
                if default:
                    u=C+(xx-C)*t
                    v=174+(yy-174)*(0.78*t+0.22*t*t)
                    test_hit=v>261
                    droplet_slope=(xx-C)/(yy-174)
                else:
                    u=start_x+(xx-start_x)*t
                    v=start_y+(yy-start_y)*(0.78*t+0.22*t*t)
                    test_hit=t>.4
                    droplet_slope=(xx-start_x)/(yy-start_y) if abs(yy-start_y)>.0001 else 0
                if test_hit:
                    d=(x[fi]-u)**2+(y[fi]-v)**2
                    hits=np.flatnonzero(d<(r+0.65)**2)
                    if len(hits):
                        hit=hits[np.argmin(d[hits])]
                        break
                self.drops[fi].append((u,v,droplet_slope,0.66 if not featured else 0.9))
            if hit is None:
                hit=j
            for age in range(80):
                self.wet[(fi+age)%F,hit]=max(self.wet[(fi+age)%F,hit],(1-age/80)**1.4)

        if default:
            # Original draw order and RNG sequence are kept unchanged.
            for _ in range(self.cfg.droplet_events):
                e=int(rng.integers(F))
                target=C+rng.triangular(-57,0,57)
                candidates=np.flatnonzero((abs(x[e]-target)<4.5)&(y[e]<464))
                if len(candidates):
                    choices=candidates[np.argsort(y[e,candidates])[:6]]
                    j=rng.choice(choices)
                    deposit(e,j,int((y[e,j]-174)/rng.uniform(4.7,6.7)))
            for j in f.actor:
                starts=np.flatnonzero((f.stage[:,j]>=0.182)&(np.roll(f.stage[:,j],1)<0.182))
                for e in starts:
                    deposit(e,j,33,True)
        else:
            # Restrict possible impacts to the forward spray hemisphere near its axis.
            for _ in range(self.cfg.droplet_events):
                e=int(rng.integers(F))
                dx=x[e]-start_x; dy=y[e]-start_y
                along=dx*vx+dy*vy
                cross=np.abs(dx*vy-dy*vx)
                candidates=np.flatnonzero((along>15)&(cross<12+along*.25)&(along<410))
                if len(candidates):
                    j=int(rng.choice(candidates))
                    deposit(e,j,max(8,int(along[j]/rng.uniform(4.7,6.7))))
            for j in f.actor:
                starts=np.flatnonzero((f.stage[:,j]>=0.182)&(np.roll(f.stage[:,j],1)<0.182))
                for e in starts:
                    delta=(x[e,j]-start_x)*vx+(y[e,j]-start_y)*vy
                    if delta>10:
                        deposit(e,j,max(8,int(delta/5.5)),True)

    def draw_drops(self,c,fi):
        if not self.enabled:
            return
        for u,v,k,size in self.drops[fi]:
            line(c,[(u-k*1.45,v-1.45),(u,v)],(0.18,0.56,0.77),size*1.8)

    def draw_equipment(self,c):
        if not self.enabled:
            return
        C=167; nx,ny=self.nx,self.ny
        # Preserve the exact fixed, right-fed, down-pointing original equipment.
        if self._default():
            for width,color in [(8,STEEL),(5.7,(0.88,0.91,0.92)),(1.8,(0.63,0.79,0.84))]:
                c.move_to(334,136)
                c.line_to(C+8,136)
                c.curve_to(C+3,136,C,139,C,145)
                c.line_to(C,156)
                c.set_line_width(width)
                c.set_source_rgb(*color)
                c.stroke()
            for dx in [0,4]:
                line(c,[(329+dx,132.1),(329+dx,139.9)],STEEL,1.2)
            polygon(c,[(C-6,153),(C+6,153),(C+6,161),(C+2.5,172),
                       (C-2.5,172),(C-6,161)],STEEL)
            polygon(c,[(C-4.5,154),(C+4.5,154),(C+4.5,160),(C+1.4,169),
                       (C-1.4,169),(C-4.5,160)],(0.74,0.79,0.81))
            line(c,[(C-6,157),(C+6,157)],STEEL,1.3)
            return
        # Generic supply line: anchor at vessel boundary on chosen entry side,
        # route to nozzle. This line and the nozzle remain stationary.
        entry=self.cfg.entry
        direction=self.cfg.direction
        if direction=='down':
            vx,vy=0,1
        elif direction=='up':
            vx,vy=0,-1
        elif direction=='left':
            vx,vy=-1,0
        else:
            vx,vy=1,0
        outlet=np.array([nx,ny],float)
        upstream=outlet-np.array([vx,vy])*23
        if entry in ('right','left'):
            sign=1 if entry=='right' else -1
            ey=float(upstream[1])
            ex=self.vessel.centre+sign*(float(self.vessel.half(ey))+14)
            path=[(ex,ey),(upstream[0],ey),(upstream[0],upstream[1])]
        elif entry=='top':
            path=[(nx,self.vessel.top-16),(nx,upstream[1])]
        else:
            path=[(nx,self.vessel.base+16),(nx,upstream[1])]
        for width,color in [(7,STEEL),(4.8,(0.88,0.91,0.92)),(1.2,(0.63,0.79,0.84))]:
            line(c,path,color,width)
        c.save()
        c.translate(nx,ny)
        c.rotate({'down':0,'up':pi,'left':pi/2,'right':-pi/2}[direction])
        polygon(c,[(-6,-18),(6,-18),(6,-10),(2.5,0),(-2.5,0),(-6,-10)],STEEL)
        polygon(c,[(-4.5,-17),(4.5,-17),(4.5,-11),(1.4,-3),(-1.4,-3),(-4.5,-11)],(0.74,0.79,0.81))
        line(c,[(-6,-14),(6,-14)],STEEL,1.3)
        c.restore()
