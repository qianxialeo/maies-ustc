from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import base64,json,io
here=Path(__file__).resolve().parent;art=here.parent/'art';out=here.parent
s=json.loads((art/'scene.json').read_text(encoding='utf-8'));world=Image.open(art/'ground.png').convert('RGB')
b64=lambda b:base64.b64encode(b).decode()
sprites={k:Image.open(io.BytesIO(base64.b64decode(v))).convert('RGBA') for k,v in s['sprites'].items()}
for k,x,y,_ in s['objects']:
 im=sprites[k];world.paste(im,(x,y),im)
world.save(out/'中科大全图.png',optimize=True)
# Minimap keeps the true aspect ratio of the world.
mw=450;mh=max(1,round(mw*s['h']/s['w']))
thumb=world.resize((mw,mh),Image.Resampling.LANCZOS);buf=io.BytesIO();thumb.save(buf,'PNG')
s.update(ground=b64((art/'ground.png').read_bytes()),nav=b64((art/'nav.png').read_bytes()),mini=b64(buf.getvalue()),mini_w=mw,mini_h=mh)
html=(here/'game.html').read_text(encoding='utf-8').replace('__ASSETS__',json.dumps(s,ensure_ascii=False,separators=(',',':')))
(out/'中科大像素漫游.html').write_text(html,encoding='utf-8')
x0,y0,x1,y1=s['lakeside'];crop=world.crop((x0,y0,x1,y1))
crop.resize(((x1-x0)*2,(y1-y0)*2),Image.Resampling.NEAREST).save(out/'West-Lakeside.png')
print('bundle',world.size,'mini',mw,mh,'lakeside',(x0,y0,x1,y1))
