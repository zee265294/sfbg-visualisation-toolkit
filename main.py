#!/usr/bin/env python3
"""Main controller. Run `python main.py` or override options from the command line.

All illustration components are generated from Python, without image assets.
"""
import argparse
from dataclasses import replace
from pathlib import Path
from config import Config
from render import create_scene
from export import export_all


def parse_args(argv=None):
    p=argparse.ArgumentParser(description='Generate unlabelled SFBG schematic animations')
    p.add_argument('--config',default='config.yaml',help='YAML settings file')
    p.add_argument('--scene',choices=['full','binary_aggregation','binary_breakage','ternary_breakage'])
    p.add_argument('--geometry',choices=['tapered','rectangular'])
    p.add_argument('--format',choices=['png','mp4','gif','all'],help='Export format')
    p.add_argument('--width',type=int)
    p.add_argument('--height',type=int)
    p.add_argument('--fps',type=int)
    p.add_argument('--duration',type=float)
    p.add_argument('--particles',type=int)
    p.add_argument('--seed',type=int)
    p.add_argument('--image-time',type=float)
    p.add_argument('--spray-entry',choices=['right','left','top','bottom'])
    p.add_argument('--nozzle-x',type=float)
    p.add_argument('--nozzle-y',type=float)
    p.add_argument('--spray-direction',choices=['up','down','left','right'])
    p.add_argument('--no-spray',action='store_true')
    p.add_argument('--output',help='Destination directory')
    p.add_argument('--stem',help='Output file basename')
    return p.parse_args(argv)


def run(argv=None):
    a=parse_args(argv)
    cpath=Path(a.config)
    if not cpath.is_file() and a.config=='config.yaml':
        cpath=Path(__file__).resolve().with_name('config.yaml')
    cfg=Config.from_yaml(cpath)
    updates={}
    for arg,field in [('scene','scene'),('geometry','geometry'),('width','width'),('height','height'),
                      ('fps','fps'),('duration','duration'),('particles','particle_count'),
                      ('seed','seed'),('image_time','image_time'),('output','output')]:
        val=getattr(a,arg)
        if val is not None:
            updates[field]=val
    if a.format:
        updates['formats']=['png','mp4','gif'] if a.format=='all' else [a.format]
    spray_updates={}
    for arg,field in [('spray_entry','entry'),('nozzle_x','nozzle_x'),('nozzle_y','nozzle_y'),
                      ('spray_direction','direction')]:
        val=getattr(a,arg)
        if val is not None:
            spray_updates[field]=val
    if a.no_spray:
        spray_updates['enabled']=False
    cfg=replace(cfg,**updates,spray=replace(cfg.spray,**spray_updates))
    cfg.validate()
    print(f'Scene={cfg.scene} | geometry={cfg.geometry} | {cfg.width}x{cfg.height} | '
          f'fps={cfg.fps} | duration={cfg.duration}s | frames={cfg.frames}',flush=True)
    scene=create_scene(cfg)
    return export_all(scene,cfg,stem=a.stem)


if __name__=='__main__':
    run()
