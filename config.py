"""User-editable, validated configuration for SFBG scientific animations.

All positions are *illustrative drawing coordinates* (not CFD geometry).
The exact original default remains portrait (720x1280), 30 fps, 20 seconds.
"""
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class SprayConfig:
    enabled: bool = True
    entry: str = 'right'                 # right/left/top/bottom
    nozzle_x: float = 0.5                 # fraction across vessel at nozzle_y
    nozzle_y: float = 0.1853448275862069 # fraction down from the top: (172-86)/464
    direction: str = 'down'              # down/up/left/right
    droplet_events: int = 1600           # matched to original source default

    def validate(self):
        if self.entry not in ('right','left','top','bottom'):
            raise ValueError('spray.entry must be right, left, top, or bottom')
        if self.direction not in ('down','up','left','right'):
            raise ValueError('spray.direction must be down, up, left, or right')
        if not (0.05 <= self.nozzle_x <= 0.95 and 0.02 <= self.nozzle_y <= 0.98):
            raise ValueError('nozzle_x, nozzle_y must be fractions within the vessel')
        if self.droplet_events < 0:
            raise ValueError('droplet_events must be >= 0')


@dataclass
class Config:
    scene: str = 'full'  # full, binary_aggregation, binary_breakage, ternary_breakage
    geometry: str = 'tapered' # tapered, rectangular (for full scene)
    width: int = 720
    height: int = 1280
    fps: int = 30
    duration: float = 20.0
    particle_count: int = 790
    seed: int = 417
    output: str = 'outputs'
    formats: list = field(default_factory=lambda: ['png','mp4','gif'])
    image_time: float = 0.0
    spray: SprayConfig = field(default_factory=SprayConfig)

    def validate(self):
        if self.scene not in ('full','binary_aggregation','binary_breakage','ternary_breakage'):
            raise ValueError(f'Unsupported scene: {self.scene}')
        if self.geometry not in ('tapered','rectangular'):
            raise ValueError('geometry must be tapered or rectangular')
        if min(self.width,self.height) < 64 or self.width % 2 or self.height % 2:
            raise ValueError('width and height must be even integers >= 64')
        if not (1 <= self.fps <= 60 and 0 < self.duration <= 120):
            raise ValueError('fps must be 1..60 and duration must be 0..120 seconds')
        if self.particle_count < 80:
            raise ValueError('particle_count must be at least 80')
        if not self.formats or any(v not in ('png','mp4','gif') for v in self.formats):
            raise ValueError('formats must be a non-empty subset of png/mp4/gif')
        self.spray.validate()

    @property
    def frames(self):
        return round(self.fps * self.duration)

    @classmethod
    def from_yaml(cls, path):
        p=Path(path)
        data=yaml.safe_load(p.read_text(encoding='utf8')) or {}
        spray=SprayConfig(**(data.pop('spray',{}) or {}))
        result=cls(**data, spray=spray)
        # relative output paths use the directory containing config.yaml
        if not Path(result.output).is_absolute():
            result.output=str((p.resolve().parent / result.output).resolve())
        result.validate()
        return result
