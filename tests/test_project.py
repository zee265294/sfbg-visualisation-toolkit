"""Fast smoke tests, plus a short MP4/GIF export roundtrip."""
import json
import math
import subprocess
from dataclasses import replace
from pathlib import Path
import numpy as np
import pytest

from config import Config,SprayConfig
from geometry import Vessel
from particles import ParticleField
from render import create_scene
from export import save_mp4,save_gif,save_png


def test_config_defaults():
    cfg=Config.from_yaml(Path(__file__).parent.parent/'config.yaml')
    assert (cfg.width,cfg.height,cfg.frames,cfg.particle_count)==(720,1280,600,790)
    assert cfg.spray.entry=='right'
    assert cfg.spray.direction=='down'


def test_geometry():
    tapered=Vessel('tapered')
    rect=Vessel('rectangular')
    assert abs(float(tapered.half(86))-126.4)<1e-10
    assert abs(float(tapered.half(550))-79)<1e-10
    assert float(rect.half(86))==float(rect.half(550))==79


@pytest.mark.parametrize('shape',['tapered','rectangular'])
def test_all_particles_inside(shape):
    cfg=Config(duration=1,fps=30)
    g=Vessel(shape)
    p=ParticleField(cfg,g)
    assert np.all(np.abs(p.x-g.centre)+p.r <g.half(p.y))
    assert np.all(p.y+p.r<g.base)


def test_deterministic_and_looped():
    cfg=Config(duration=1)
    a=create_scene(cfg);b=create_scene(cfg)
    assert np.array_equal(a.particles.x,b.particles.x)
    assert bytes(a.frame(0).get_data())==bytes(a.frame(cfg.frames).get_data())


@pytest.mark.parametrize('entry,position,direction',[
    ('right',.1853448275862069,'down'),('left',.3,'down'),
    ('top',.25,'down'),('bottom',.94,'up')])
def test_spray_options(entry,position,direction):
    cfg=Config(duration=.5,fps=10)
    cfg.spray=SprayConfig(entry=entry,nozzle_y=position,direction=direction,droplet_events=100)
    scene=create_scene(cfg)
    assert len(scene.spray.drops)==cfg.frames
    assert scene.frame(2).get_width()==cfg.width


@pytest.mark.parametrize('which',['binary_aggregation','binary_breakage','ternary_breakage'])
def test_mechanism_scene(which):
    cfg=Config(scene=which,width=960,height=320,duration=1)
    scene=create_scene(cfg)
    a=scene.frame(0)
    assert a.get_width()==960 and a.get_height()==320


def test_no_spray():
    cfg=Config(duration=.5)
    cfg.spray.enabled=False
    scene=create_scene(cfg)
    assert not any(scene.spray.drops)


def test_validation():
    with pytest.raises(ValueError): Config(geometry='cylindrical').validate()
    with pytest.raises(ValueError): Config(width=721).validate()
    with pytest.raises(ValueError): Config(spray=SprayConfig(entry='rear')).validate()


def test_media_export(tmp_path):
    cfg=Config(width=360,height=640,fps=10,duration=.8)
    scene=create_scene(cfg)
    still=save_png(scene,tmp_path/'preview.png',0.1)
    movie=save_mp4(scene,tmp_path/'preview.mp4')
    gif=save_gif(movie,tmp_path/'preview.gif',fps=10)
    assert all(path.stat().st_size>2000 for path in (still,movie,gif))
    result=subprocess.run(['ffprobe','-v','error','-select_streams','v:0',
                           '-show_entries','stream=width,height,nb_frames:format=duration',
                           '-of','json',str(movie)],capture_output=True,text=True,check=True)
    data=json.loads(result.stdout)
    assert data['streams'][0]['width']==360
    assert data['streams'][0]['height']==640
    assert abs(float(data['format']['duration'])-.8)<.06
    from PIL import Image
    with Image.open(gif) as im:
        assert im.n_frames>2
        assert im.info.get('loop')==0
