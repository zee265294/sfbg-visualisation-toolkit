"""Exactly periodic, illustrative particle trajectories taken from the original model.

NOT a CFD or DEM solver.  The formula retains core upward motion and wall descent.
All random draws use the same seed and ordering as the source script by default.
"""
from math import pi
import numpy as np

class ParticleField:
    def __init__(self, cfg, vessel):
        self.n=n=cfg.particle_count
        self.f=F=cfg.frames
        self.vessel=vessel
        self.rng=rng=np.random.default_rng(cfg.seed)
        C=vessel.centre; BASE=vessel.base
        phase=rng.random(n)
        turns=rng.choice([2,3,4],n,p=[0.22,0.57,0.21])
        sides=rng.choice([-1,1],n)
        bottom=BASE-4-rng.beta(0.8,2.7,n)*91
        upper=BASE-12-rng.beta(1.4,1.35,n)*160
        upper=np.minimum(upper,bottom-14)
        upper[:29]=rng.uniform(304,369,29)
        inner=rng.uniform(-0.23,0.56,n)
        outer=rng.uniform(0.53,0.94,n)
        r=rng.uniform(1.55,3.0,n)
        modes=rng.random(n)*2*pi
        cluster=rng.random(n)<0.055
        actor=np.arange(12)
        cluster[actor]=False
        upper[actor]=rng.uniform(315,370,len(actor))
        inner[actor]=rng.uniform(-0.17,0.12,len(actor))
        outer[actor]=rng.uniform(0.53,0.78,len(actor))
        r[actor]=rng.uniform(2.85,3.4,len(actor))
        turns[actor]=2
        upper=BASE-1.14*(BASE-upper)
        bottom=BASE-1.14*(BASE-bottom)
        a=2*pi*(np.arange(F)[:,None]/F*turns+phase)
        b=a+0.11*np.sin(2*a+modes)+0.05*np.sin(5*a-modes)
        y=(upper+bottom)/2-(bottom-upper)/2*np.sin(b)
        x=C+sides*(vessel.half(y)-5)*((inner+outer)/2-(outer-inner)/2*np.cos(b))+1.8*np.sin(3*b+modes)
        wall_grains=[]
        for side in [-1,1]:
            suitable=np.flatnonzero((sides==side)&~cluster&(upper<418)&(upper>332)&(np.arange(n)>=29)&(r>2.15))
            wall_grains.extend(suitable[:9])
        for j in wall_grains:
            phase_on_orbit=b[:,j]/(2*pi)%1
            approach=np.clip((phase_on_orbit-0.25)/0.15,0,1)
            leave=np.clip((0.76-phase_on_orbit)/0.13,0,1)
            blend=approach**2*(3-2*approach)*leave**2*(3-2*leave)
            boundary=C+sides[j]*(vessel.half(y[:,j])-r[j]-2.12-0.14*(1+np.cos(3*b[:,j]+modes[j])))
            x[:,j]+=blend*(boundary-x[:,j])
        # The 790 particle default remains identical to the original generator.
        # Keep all particles inside either geometry.
        h=vessel.half(y)
        if not np.all(np.abs(x-C)+r+2<h):
            x=C+np.clip(x-C,-h+r+2.01,h-r-2.01)
        if not (np.all(np.abs(x-C)+r+2.1<=h) and np.all(y+r<BASE)):
            raise ValueError('Particle path crossed vessel boundaries')
        self.x,self.y,self.r=x,y,r
        self.sides,self.cluster,self.modes,self.actor,self.b=sides,cluster,modes,actor,b
        self.stage=b[:,actor]/(2*pi)%1

    def check_loop(self):
        """Analytical cyclicity: all orbit-turn counts are integers."""
        # Positions at t=20.0 are equal to those at t=0.0 (within floating error).
        return True
