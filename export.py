"""Single-frame PNG, high-quality MP4, and infinite-loop GIF exporting."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def need_ffmpeg():
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg must be installed and on PATH to export MP4 or GIF.')


def _run(args):
    subprocess.run(args,check=True)


def save_png(scene,path,time_seconds=0):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    index=round(time_seconds*scene.cfg.fps)%scene.cfg.frames
    scene.frame(index).write_to_png(str(path))
    return path


def save_mp4(scene,path,crf=18):
    need_ffmpeg()
    cfg=scene.cfg
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo',
             '-pix_fmt','bgr0' if sys.byteorder=='little' else '0rgb',
             '-s',f'{cfg.width}x{cfg.height}','-r',str(cfg.fps),'-i','-',
             '-an','-c:v','libx264','-preset','medium','-crf',str(crf),
             '-pix_fmt','yuv420p','-movflags','+faststart',str(path)]
    proc=subprocess.Popen(command,stdin=subprocess.PIPE)
    try:
        for f in range(cfg.frames):
            surface=scene.frame(f)
            proc.stdin.write(surface.get_data())
        proc.stdin.close()
        if proc.wait()!=0:
            raise RuntimeError('FFmpeg MP4 encoder failed')
    except Exception:
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        raise
    return path


def save_gif(mp4,path,fps=25,width=None):
    """High quality global palette + infinite looping GIF from MP4 frames."""
    need_ffmpeg()
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    mp4=str(mp4)
    # FFmpeg palettegen/paletteuse avoids massive RAM usage on long animations.
    with tempfile.TemporaryDirectory(prefix='sfbg-palette-') as td:
        palette=str(Path(td)/'palette.png')
        filter1=f'fps={fps}'
        if width:
            filter1+=f',scale={width}:-2:flags=lanczos'
        _run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',mp4,
              '-vf',filter1+',palettegen=max_colors=256:stats_mode=full',
              '-frames:v','1',palette])
        _run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',mp4,'-i',palette,
              '-filter_complex',filter1+'[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
              '-loop','0',str(path)])
    return path


def export_all(scene,cfg,stem=None):
    cfg.validate()
    base=Path(cfg.output)
    base.mkdir(parents=True,exist_ok=True)
    stem=stem or (cfg.scene+'_'+cfg.geometry if cfg.scene=='full' else cfg.scene)
    generated=[]
    if 'png' in cfg.formats:
        p=save_png(scene,base/(stem+'.png'),cfg.image_time)
        generated.append(p)
        print('PNG:',p,flush=True)
    if 'mp4' in cfg.formats or 'gif' in cfg.formats:
        if 'mp4' in cfg.formats:
            p=base/(stem+'.mp4')
        else:
            # gif needs a temporary mp4 source
            p=base/(stem+'__gif_source.mp4')
        save_mp4(scene,p)
        if 'mp4' in cfg.formats:
            generated.append(p)
            print('MP4:',p,flush=True)
        if 'gif' in cfg.formats:
            g=save_gif(p,base/(stem+'.gif'))
            generated.append(g)
            print('GIF:',g,flush=True)
        if 'mp4' not in cfg.formats:
            p.unlink()
    return generated
