from PIL import Image,ImageDraw,ImageFont,ImageChops
from shapely.geometry import Polygon,Point,LineString,box,MultiPolygon
from shapely.geometry.polygon import orient
from shapely.affinity import affine_transform,translate,scale
from shapely.ops import unary_union
import xml.etree.ElementTree as ET
import json,math,random,os,hashlib,base64,io
from pathlib import Path
R=random.Random(1958);here=Path(__file__).resolve().parent;out=here.parent/'art';out.mkdir(exist_ok=True)
root=ET.parse(here.parent/'data'/'west.osm');ways={w.get('id'):w for w in root.findall('way')}; nodes={n.get('id'):((float(n.get('lon'))-117.255)*94650,(float(n.get('lat'))-31.84)*110900) for n in root.findall('node')}
def tags(e):return {t.get('k'):t.get('v') for t in e.findall('tag')}
def pts(w):return [nodes[t.get('ref')] for t in w.findall('nd')]
def poly(i):return Polygon(pts(ways[i])).buffer(0)
camp=poly('259860583');lake=Polygon(pts(ways['260256366']),[pts(ways['260257562'])]).buffer(0)
A=(3.1,.88,-.48,1.72,2910,640)
def tr(x,y,h=0):return (round(A[0]*x+A[1]*y+A[4]),round(A[2]*x+A[3]*y+A[5]-h*2.8))
def px(p):return affine_transform(p,A)
def parts(p):return [p] if p.geom_type=='Polygon' else [q for i in getattr(p,'geoms',[]) for q in parts(i)]
W,H=3160,1750
bg=Image.new('RGB',(W,H),'#9aaeb0');D=ImageDraw.Draw(bg)
def paint(g,col,d=D,holes=None):
 for p in parts(g):
  if p.is_empty:continue
  d.polygon([(round(x),round(y)) for x,y in p.exterior.coords],fill=col)
  if holes is not None:
   for ring in p.interiors:d.polygon(list(ring.coords),fill=holes)
# A gently banded horizon around the model.
for y in range(H):
 t=y/H;D.line((0,y,W,y),fill=(int(176-44*t),int(199-30*t),int(194-20*t)))
for j in range(4000):
 x=R.randrange(W);y=R.randrange(H);D.line((x,y,x+R.randint(2,18),y),fill='#bacdc1')
cp=px(camp)
for j,c in [(17,'#667c75'),(12,'#738a7c'),(7,'#849b80'),(3,'#8d9d80'),(0,'#b3bc8a')]:paint(translate(cp,yoff=j),c)
mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask);paint(cp,255,md)
for j in range(108000):
 x=R.randrange(W);y=R.randrange(H)
 if not mask.getpixel((x,y)):continue
 l=R.choice([1,2,3,5]);D.line((x,y,x+l,y),fill=R.choice(['#aab786','#bfc593','#c8c99a','#a9b489','#bbc28f']))
 if R.random()<.09:D.line((x+1,y,x+1,y-2),fill='#9ca77b')
structures=[];roads=[];water=[];bridges=[];objs=[];assets={};geometry=[];plants=[];decks=[]
def stash(im,name):
 buf=io.BytesIO();im.save(buf,'PNG',optimize=True);assets[name]=base64.b64encode(buf.getvalue()).decode()
def obj(name,x,y,depth):objs.append([name,x,y,round(depth)])
for i,w in ways.items():
 t=tags(w);v=pts(w)
 if len(v)<2:continue
 if t.get('highway') and t.get('area')!='yes':
  l=LineString(v).intersection(camp)
  if not l.is_empty:
   wid={'path':2,'footway':2.5,'steps':2.4,'service':5,'residential':6,'pedestrian':4.5,'cycleway':3}.get(t['highway'],6)
   if t.get('bridge')=='yes':bridges.append((l,wid,i))
   else:roads.append((l,wid))
  continue
 if len(v)<4 or v[0]!=v[-1]:continue
 p=Polygon(v).buffer(0)
 if p.is_empty or not camp.covers(p.representative_point()):continue
 if t.get('building'):structures.append((i,p,t))
 elif t.get('natural')=='water':water.append(p)
 elif t.get('leisure') in ['pitch','track']:
  q=px(p);paint(q,'#bc866c' if t['leisure']=='track' else '#7fa99a');paint(q.boundary.buffer(1.5),'#e3dcc1');plants.append(p)
for l,w in sorted(roads,key=lambda a:-a[1]):
 g=px(l.buffer(w*.5,cap_style=2,join_style=2));paint(g.buffer(1.5),'#a4a58a');paint(g,'#b9b9a3' if w>=4.8 else '#d3c6a4')
 if w>=4.8:paint(g.boundary.buffer(.65),'#ded5b6')
water.append(lake);wg=px(unary_union(water));wm=Image.new('L',(W,H));paint(wg,255,ImageDraw.Draw(wm),0)
paint(wg.buffer(4),'#738f7d',holes='#b3bc8a');paint(wg,'#548e88',holes='#b6be8a')
for dist,c in [(2,'#7daba0'),(5,'#73a99c'),(9,'#69a799'),(15,'#64a192'),(27,'#5e9d94'),(44,'#589895')]:paint(wg.buffer(-dist),c,holes=None) if False else None
for dist,co in [(12,'#69a494'),(7,'#7db09a'),(3,'#9dbb99')]:paint(wg.difference(wg.buffer(-dist)),co,holes=None) if False else None
# Draw narrow shoreline strips with polygon holes preserved using an alpha mask.
def overlay(g,col):
 mm=Image.new('L',(W,H));paint(g,255,ImageDraw.Draw(mm),0);bg.paste(col,(0,0,W,H),mm)
for s,c in [(20,'#66a292'),(10,'#7eae98'),(4,'#a4b99a')]:overlay(wg.difference(wg.buffer(-s)),c)
for i in range(6100):
 bx,by,bX,bY=wg.bounds;x=R.randint(int(bx),int(bX));y=R.randint(int(by),int(bY))
 if not wm.getpixel((x,y)):continue
 length=R.randint(2,13);D.line((x,y,x+length,y),fill=R.choice(['#72a99c','#85b7a6','#599592','#a5c4a6']))
 if R.random()<.2:D.line((x-3,y+1,x+2,y+1),fill='#83b3a0')
# Ground-projected cast shadows soften the edges under each building.
for i,p,t in structures:
 g=px(p);paint(translate(g,xoff=6,yoff=6),'#899b7e')
def tree(type,seed):
 r=random.Random(seed);w,h=76,88;im=Image.new('RGBA',(w,h));d=ImageDraw.Draw(im);cx,cy=38,81
 d.ellipse((15,70,60,80),fill='#85977a');d.polygon([(33,79),(39,64),(40,78),(44,81),(36,80),(31,82)],fill='#574f47')
 d.line((38,76,36,45),fill='#695744',width=4);d.line((38,65,25,47),fill='#665b48',width=2);d.line((38,62,50,42),fill='#665b48',width=2)
 pal=[['#3d6658','#507957','#6b8d5e','#8fa169','#aeb77d'],['#426a63','#558575','#72a088','#94b299','#b8c7a9'],['#4e6b59','#648356','#83a169','#a2b376','#c4c689'],['#5a6d5d','#768358','#a1a05d','#bab26f','#d5c78b']][type%4]
 patches=[]
 for x,y,rx,ry in [(24,44,19,15),(43,43,23,16),(23,29,16,14),(40,23,20,16),(51,34,16,14)]:
  a=[(int(x+(rx+r.uniform(-1.5,1.5))*math.cos(j*math.tau/24)),int(y+(ry+r.uniform(-1.5,1.5))*math.sin(j*math.tau/24))) for j in range(24)]
  d.polygon(a,fill=pal[0]);d.polygon([(xx-1,yy-2) for xx,yy in a],fill=pal[1]);patches.append((x,y,rx,ry))
 for x,y,rx,ry in patches:
  for j in range(65):
   a=r.uniform(0,math.tau);rad=r.random()**.5;xx=int(x+rx*rad*math.cos(a));yy=int(y+ry*rad*math.sin(a))
   lit=(x-xx)/rx+(y-yy)/ry+r.uniform(-.75,.6);co=pal[3 if lit>.55 else 2 if lit>-.5 else 1]
   size=r.randint(2,5);d.polygon([(xx-size,yy),(xx-1,yy-2),(xx+2,yy-2),(xx+size,yy),(xx+1,yy+2),(xx-2,yy+2)],fill=co)
   if lit>1:d.line((xx-2,yy-2,xx+1,yy-2),fill=pal[4])
 return im
for j in range(16):
 k=[.62,.72,.82,.88,.66][j%5];sprite=tree(j%4,223+j);stash(sprite.resize((round(76*k),round(88*k)),Image.Resampling.NEAREST),'tree'+str(j))
def furnishing(kind):
 im=Image.new('RGBA',(30,33));d=ImageDraw.Draw(im)
 if kind=='lamp':
  d.ellipse((8,28,23,31),fill='#87977d');d.line((15,29,15,9),fill='#445a50',width=2);d.rectangle((12,4,18,10),fill='#506454');d.rectangle((13,5,17,8),fill='#f5da97');d.polygon([(11,4),(15,1),(19,4)],fill='#4e6254')
 else:
  d.line((4,26,4,31),fill='#4f6458',width=2);d.line((24,23,24,28),fill='#4f6458',width=2);d.polygon([(1,24),(22,19),(28,22),(6,28)],fill='#9f7455');d.line((2,23,22,18),fill='#d4b386',width=2);d.line((1,18,23,13),fill='#a78460',width=3)
 return im
for k in ['lamp','bench']:stash(furnishing(k),k)
def art_build(i,p,t):
 q=px(p);minx,miny,maxx,maxy=q.bounds;origin=(int(minx)-45,int(miny)-235)
 ww,hh=int(maxx)-origin[0]+55,int(maxy)-origin[1]+40;im=Image.new('RGBA',(ww,hh));d=ImageDraw.Draw(im);rng=random.Random(int(i))
 ox,oy=origin;pol=lambda a,c:d.polygon([(round(x-ox),round(y-oy)) for x,y in a],fill=c)
 def line(a,c,w=1):d.line([(round(x-ox),round(y-oy)) for x,y in a],fill=c,width=w)
 def roof(r,z,col):
  for g in parts(r):
   if g.is_empty or g.area<.05:continue
   polyline=[(x,y-z) for x,y in g.exterior.coords];pol(polyline,col);line(polyline,'#777c6e');line(polyline[:2],'#d1c6a4')
 def shell(r,z,h,wall,shade,top,floors,style='normal'):
  for g in parts(r):
   if g.is_empty or g.area<.05:continue
   ring=list(orient(g,1).exterior.coords);edges=sorted(zip(ring,ring[1:]),key=lambda e:(e[0][1]+e[1][1])/2)
   for (x,y),(u,v) in edges:
    dx,dy=u-x,v-y;L=math.hypot(dx,dy)
    if dx>0 or L<.3:continue
    def pt(t,zz):return (x+dx*t,y+dy*t-zz)
    pol([pt(0,z),pt(1,z),pt(1,h),pt(0,h)],wall if dy<0 else shade)
    if L<5:continue
    n=max(1,int(L/(10 if style!='glass' else 8)))
    for j in range(floors):
     hh=(h-z)/floors;b=z+(j+.22)*hh;e=z+(j+.80)*hh
     if hh<3:continue
     for k in range(n):
      if L/n<4:continue
      a=(k+.16)/n;f=(k+.80)/n
      if style=='glass':a=k/n+.008;f=(k+1)/n-.005
      pol([pt(a,b),pt(f,b),pt(f,e),pt(a,e)],rng.choice(['#426064','#58767a','#496970','#657f7c']))
      line([pt(a,e),pt(f,e)],'#798c86');line([pt(a,b-.5),pt(f,b-.5)],'#d9c9a3')
      if L/n>9:line([pt((a+f)/2,b),pt((a+f)/2,e)],'#a3a795')
     if style in ['gallery','glass']:line([pt(0,z+j*hh+.6),pt(1,z+j*hh+.6)],'#d3cbb4',2)
    line([pt(0,h),pt(1,h)],'#ede0ba',2)
   roof(g,h,top)
 def terrace(r,z,col):
  roof(r,z,col)
  x0,y0,x1,y1=r.bounds
  for yy in range(int(y0)-100,int(y1)+60,4):
   cut=LineString([(x0-3,yy),(x1+3,yy-(x1-x0)*.16)]).intersection(r)
   for g in ([cut] if cut.geom_type=='LineString' else getattr(cut,'geoms',[])):
    if g.geom_type=='LineString' and not g.is_empty:line([(x,y-z) for x,y in g.coords],'#ad8a6c')
 name=t.get('name','');lv=t.get('building:levels','');floors=int(lv) if lv.isdigit() else (2 if p.area<800 else 4)
 special=i in ['259873139','1135360042','260224955','260224953','260057933']
 if i=='1135360042':
  terrace(q.buffer(10),2,'#c69e77')
  shell(q,2,14,'#706f5c','#586858','#899583',1,'glass')
  roof(q.buffer(2),15,'#5e756c')
  up=q.intersection(box(minx-1,miny-1,(minx+maxx)*.5+12,maxy+1));shell(up,15,23,'#e0dbc5','#c4c9af','#c8c9b5',1)
  for dx,dy in [(-18,1),(8,0),(28,-2)]:
   xx,yy=(minx+maxx)/2+dx,maxy+dy+4;line([(xx,yy),(xx,yy-11)],'#695744',2)
   pol([(xx-8,yy-10),(xx-5,yy-14),(xx+2,yy-17),(xx+9,yy-12),(xx+4,yy-9),(xx-4,yy-8)],'#ebd4a3')
   line([(xx-8,yy-10),(xx+2,yy-17),(xx+4,yy-9)],'#bca983')
  # Timber slats, menu board and cafe furniture read at walking scale.
  for dx,dy in [(-25,-2),(-3,4),(22,0)]:
   xx,yy=(minx+maxx)/2+dx,maxy+dy
   line([(xx,yy),(xx,yy-4)],'#6e5946',2)
   pol([(xx-3,yy-4),(xx,yy-6),(xx+4,yy-5),(xx+2,yy-3)],'#e0c097')
   line([(xx+5,yy-2),(xx+7,yy-3),(xx+7,yy-5)],'#826747',2)
  xx,yy=maxx-3,maxy-5
  pol([(xx-5,yy),(xx-3,yy-9),(xx+3,yy-9),(xx+4,yy)],'#a2835d');pol([(xx-3,yy-2),(xx-2,yy-8),(xx+2,yy-8),(xx+2,yy-2)],'#47665c')
 elif i=='259873139':
  shell(q,0,31,'#ad9071','#937961','#a29d86',3,'gallery');cx,cy=p.centroid.coords[0];tower=px(box(cx-10,cy-13,cx+15,cy+20))
  shell(tower,31,148,'#b98d60','#99734f','#b49774',12)
  shell(tower.buffer(.8),136,143,'#e7dbbd','#d2c6a6','#dad0b5',0)
  shell(px(box(cx-8,cy-11,cx-3,cy+16)),148,157,'#b88d61','#9e7855','#cab18b',0)
  shell(px(box(cx+7,cy-11,cx+12,cy+16)),148,157,'#b88d61','#9e7855','#cab18b',0)
  xx,yy=tr(cx+3,cy+4);line([(xx-13,yy-156),(xx,yy-169),(xx+14,yy-156),(xx-13,yy-156)],'#f5e8ca',3)
 elif i=='260057933':
  shell(q,0,21,'#c79879','#a57f69','#b3b6a4',1)
  cx,cy=p.centroid.coords[0];oval=px(scale(Point(cx,cy).buffer(1,quad_segs=30),42,29,origin=(cx,cy))).intersection(q)
  roof(oval,22,'#84999a')
  for rr in [.88,.76,.64,.52]:
   o=scale(oval,rr,rr);line([(x,y-22) for x,y in o.exterior.coords],'#bcc8b7',2)
 else:
  third=i in ('260224955','260224953')
  pal=('#a89078','#86796c','#a4a398') if third else rng.choice([('#cfb398','#b59b83','#acaaa0'),('#d7c4a6','#b7a88f','#9ea79b'),('#bb9785','#a98576','#ab9b8b'),('#c1b49c','#a69d89','#a5a59a')])
  h=floors*(9.5 if third else 8.6);shell(q,0,h,*pal,floors,'gallery' if third or '#' in name else 'normal')
  inset=q.buffer(-3);roof(inset,h+.3,'#b9b6a0')
  if p.area>650:
   cx,cy=q.representative_point().coords[0];shed=box(cx-6,cy-3,cx+7,cy+3).intersection(inset);shell(shed,h,h+3,'#a59c85','#928c7b','#c3beaa',0)
 bbox=im.getbbox()
 if bbox:
  key='b'+i;stash(im.crop(bbox),key);obj(key,origin[0]+bbox[0],origin[1]+bbox[1],q.bounds[3]-2)
 return name,special
for i,p,t in structures:
 art_build(i,p,t)
geometry=[p for _,p,_ in structures]
# Bridge decking and handrail. Deck goes on the ground and front rail is independently sorted.
for l,w,i in bridges:
 line=px(l);gg=px(l.buffer(w*.53,cap_style=2,join_style=2));paint(gg.buffer(1.0),'#747c70');paint(gg,'#e2d3b0')
 if line.geom_type!='LineString':continue
 for off in [-1,1]:
  rail=px(l.offset_curve(off*w*.48))
  if rail.geom_type!='LineString':continue
  a=list(rail.coords);D.line([(round(x),round(y)-3) for x,y in a],fill='#dbd3b9',width=1)
  for v in range(0,int(rail.length),9):
   pt=rail.interpolate(v);x,y=pt.coords[0];D.line((x,y,x,y-5),fill='#ebe3c4',width=2)
avoid=unary_union([*geometry,*water,*plants,*[l.buffer(w/2+1.5) for l,w in roads],*[l.buffer(w) for l,w,i in bridges]])
clear=camp.difference(avoid);park=poly('260257562')
taken=set()
def plant(x,y,forced=False):
 pt=Point(x,y);cell=(round(x/6),round(y/6))
 if cell in taken or not clear.covers(pt):return
 sx,sy=tr(x,y)
 for cx,cy,rx,ry in [(1774,1018,74,50),(2050,1022,51,72),(1553,1128,39,30)]:
  if ((sx-cx)/rx)**2+((sy-cy)/ry)**2<1:return
 if any(p.distance(pt)<6 for i,p,t in structures if i in ['1135360042','259873139']):return
 taken.add(cell);sx,sy=tr(x,y);j=R.randrange(16);k=[.62,.72,.82,.88,.66][j%5];obj('tree'+str(j),sx-round(38*k),sy-round(80*k),sy)
for l,w in roads:
 if l.geom_type!='LineString' or l.length<12:continue
 for dist in range(5,int(l.length)-3,R.randint(11,17)):
  pt=l.interpolate(dist);p2=l.interpolate(dist+1);dx=p2.x-pt.x;dy=p2.y-pt.y
  for s in [-1,1]:
   x=pt.x+dy*(w/2+2.8)*s;y=pt.y-dx*(w/2+2.8)*s
   if R.random()<.51:plant(x,y)
   elif R.random()<.26:
    sx,sy=tr(x,y);obj('lamp',sx-15,sy-30,sy)
for j in range(2200):
 x=R.uniform(-840,-52);y=R.uniform(-340,369)
 if R.random()<.4:plant(x,y)
# Dense reeds and small, varied lily pads sit on quiet margins.
for j in range(650):
 x=R.uniform(-510,-365);y=R.uniform(121,207);pt=Point(x,y)
 if not lake.covers(pt) or lake.boundary.distance(pt)>2.9:continue
 sx,sy=tr(x,y);D.ellipse((sx-3,sy-1,sx+3,sy+1),fill=R.choice(['#769763','#92aa72','#acb981']));D.point((sx+1,sy),fill='#afc89c')
 if R.random()<.19:D.rectangle((sx,sy-2,sx+1,sy-1),fill='#e9c4ae')
for j in range(530):
 x=R.uniform(-515,-360);y=R.uniform(118,210);pt=Point(x,y)
 if lake.contains(pt) or lake.boundary.distance(pt)>1.6:continue
 sx,sy=tr(x,y)
 for no in [0,2,4]:D.line((sx+no,sy,sx+no-1,sy-R.randint(2,6)),fill=R.choice(['#6c8968','#8f9d6d','#aab782']))
# Collision mask and safe arrival points are derived from the same shoreline and outlines.
bridge=unary_union([l.buffer(w*.6) for l,w,i in bridges]);walk=camp.buffer(-1).difference(unary_union([*geometry,*water])).union(bridge).buffer(-.24)
nav=Image.new('1',(W,H));paint(px(walk),1,ImageDraw.Draw(nav),0);nav.save(out/'nav.png')
marks=[]
for label,x,y,about in [('九曲桥',-480,150,'曲折的桥面连接湖心岛与西岸，岸线与岛按地图轮廓绘制。'),('西区 1958',-393,124,'沿水岸可以看到外挑的平台、深色窗框和低矮的白墙。'),('西区图书馆',-300,145,'低裙房托起赭色塔楼，浅色顶带和屋顶标志勾出天际线。'),('第三教学楼',-525,53,'A、B 楼的楼翼折转相接，邻近 C 楼较低。'),('同步辐射实验室',-728,-221,'实验大厅位于西区西南部。屋顶细节为游戏化示意。'),('西区学生食堂',-620,302,'食堂及学生宿舍位于北侧生活区。')]:
 from shapely.ops import nearest_points
 pt=nearest_points(walk.buffer(-1),Point(x,y))[0];sx,sy=tr(pt.x,pt.y);marks.append(dict(name=label,x=sx,y=sy,about=about))
bg.save(out/'ground.png',optimize=True);objs.sort(key=lambda o:o[3]);print('scene',len(structures),'buildings,',len(taken),'trees',marks,flush=True)
(out/'scene.json').write_text(json.dumps(dict(w=W,h=H,sprites=assets,objects=objs,marks=marks,buildings=len(structures)),ensure_ascii=False,separators=(',',':')))
