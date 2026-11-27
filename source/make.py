from PIL import Image,ImageDraw,ImageFont,ImageChops
from shapely.geometry import Polygon,Point,LineString,box,MultiPolygon
from shapely.geometry.polygon import orient
from shapely.affinity import affine_transform,translate,scale,rotate
from shapely.ops import unary_union
import xml.etree.ElementTree as ET
import json,math,random,os,hashlib,base64,io
from pathlib import Path
R=random.Random(1958);here=Path(__file__).resolve().parent;out=here.parent/'art';out.mkdir(exist_ok=True)
root=ET.parse(here.parent/'data'/'campus3.osm');ways={w.get('id'):w for w in root.findall('way')}; nodes={n.get('id'):((float(n.get('lon'))-117.255)*94650,(float(n.get('lat'))-31.84)*110900) for n in root.findall('node')}
def tags(e):return {t.get('k'):t.get('v') for t in e.findall('tag')}
def pts(w):return [nodes[t.get('ref')] for t in w.findall('nd')]
def poly(i):return Polygon(pts(ways[i])).buffer(0)
CAMP=['259860583','298734692','262614785']
_cp=[poly(c) for c in CAMP]
# 西区—中区 由肥西路相连，中区—东区 由金寨路地下通道相连；两段街道并入陆地，避免出现“海峡”。
from shapely.ops import nearest_points as _np
_a,_b=_np(_cp[0],_cp[1]);LINK_A=LineString([_a.coords[0],_b.coords[0]]);LINK_B_AT=(_a.coords[0],_b.coords[0])
_c,_d=_np(_cp[1],_cp[2]);LINK_B=LineString([_c.coords[0],_d.coords[0]]);TUNNEL_AT=(_c.coords[0],_d.coords[0])
def _named_lines(nm):
 _out=[]
 for _w in ways.values():
  _t=tags(_w)
  if _t.get('name')==nm and _t.get('highway') and _t.get('area')!='yes':
   _pp=pts(_w)
   if len(_pp)>1:_out.append(LineString(_pp))
 return _out
# 肥西路与金寨路作为“街道地块”并入陆地，校区之间不再是海峡。
FROAD=unary_union([l.buffer(21) for l in _named_lines('肥西路')]).intersection(box(-90,-345,-18,378))
JROAD=unary_union([l.buffer(25) for l in _named_lines('金寨路')]).intersection(box(470,-625,730,405))
camp=unary_union([*_cp,LINK_A.buffer(20),LINK_B.buffer(30),FROAD,JROAD]).buffer(0)
lake=Polygon(pts(ways['260256366']),[pts(ways['260257562'])]).buffer(0)
# ---------------------------------------------------------------------------
# 投影：正射平面，正北向上（自南向北俯视）。校园主网格与南北轴只差 1.5°，
# 先把它转正，长直线才不会一路锯齿；高度沿屏幕竖直方向拉伸，南立面可见，
# 于是平面比例不变，却得到“从南面看过去”的 2.5D 立体感。
S=3.1;VS=0.80;K=S*VS;HZ=1.0;TH=math.radians(1.5);CS,SN=math.cos(TH),math.sin(TH)
def rw(x,y):return (x*CS-y*SN,x*SN+y*CS)
_xs=[];_ys=[]
for x,y in camp.exterior.coords:
 X,Y=rw(x,y);_xs.append(X);_ys.append(Y)
minX,maxX=min(_xs),max(_xs);minY,maxY=min(_ys),max(_ys)
MARGIN=190
W=int(round((maxX-minX)*S))+MARGIN*2;H=int(round((maxY-minY)*K))+MARGIN*2
TX=MARGIN-minX*S;TY=MARGIN+maxY*K
def tr(x,y,h=0):
 X,Y=rw(x,y);return (round(X*S+TX),round(TY-Y*K-h*HZ))
def fm(u,v):return (round(u*S+TX),round(TY-v*K))
A=(S*CS,-S*SN,-K*SN,-K*CS,TX,TY)
def px(p):return affine_transform(p,A)
def parts(p):return [p] if p.geom_type=='Polygon' else [q for i in getattr(p,'geoms',[]) for q in parts(i)]
AREA=W*H/5.53e6
bg=Image.new('RGB',(W,H),'#9aaeb0');D=ImageDraw.Draw(bg)
def paint(g,col,d=D,holes=None):
 for p in parts(g):
  if p.is_empty:continue
  d.polygon([(round(x),round(y)) for x,y in p.exterior.coords],fill=col)
  if holes is not None:
   for ring in p.interiors:d.polygon(list(ring.coords),fill=holes)
def fillm(g,col):
 mm=Image.new('L',(W,H));paint(g,255,ImageDraw.Draw(mm),0);bg.paste(Image.new('RGB',(W,H),col),(0,0),mm)
def overlay(g,col):
 mm=Image.new('L',(W,H));paint(g,255,ImageDraw.Draw(mm),0);bg.paste(Image.new('RGB',(W,H),col),(0,0),mm)
# A gently banded horizon around the model.
for y in range(H):
 t=y/H;D.line((0,y,W,y),fill=(int(176-44*t),int(199-30*t),int(194-20*t)))
for j in range(int(4000*AREA)):
 x=R.randrange(W);y=R.randrange(H);D.line((x,y,x+R.randint(2,18),y),fill='#bacdc1')
cp=px(camp)
for j,c in [(17,'#667c75'),(12,'#738a7c'),(7,'#849b80'),(3,'#8d9d80'),(0,'#b3bc8a')]:paint(translate(cp,yoff=j),c)
mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask);paint(cp,255,md)
for j in range(int(108000*AREA)):
 x=R.randrange(W);y=R.randrange(H)
 if not mask.getpixel((x,y)):continue
 l=R.choice([1,2,3,5]);D.line((x,y,x+l,y),fill=R.choice(['#aab786','#bfc593','#c8c99a','#a9b489','#bbc28f']))
 if R.random()<.09:D.line((x+1,y,x+1,y-2),fill='#9ca77b')
structures=[];roads=[];water=[];bridges=[];plazas=[];objs=[];assets={};geometry=[];plants=[]
def stash(im,name):
 buf=io.BytesIO();im.save(buf,'PNG',optimize=True);assets[name]=base64.b64encode(buf.getvalue()).decode()
def obj(name,x,y,depth):objs.append([name,x,y,round(depth)])
FIELD_IDS={'259869887','367584042','259869888','298467057','298467058'}
COURT_IDS=set()
for i,w in ways.items():
 t=tags(w);v=pts(w)
 if len(v)<2:continue
 if t.get('highway') and t.get('area')!='yes':
  l=LineString(v).intersection(camp)
  if not l.is_empty:
   wid={'trunk':13,'trunk_link':8,'primary':11,'primary_link':8,'secondary':10,'secondary_link':7,'tertiary':8,'residential':6,'service':5,'pedestrian':4.5,'cycleway':3,'footway':2.5,'path':2,'steps':2.4}.get(t['highway'],6)
   if t.get('bridge')=='yes':bridges.append((l,wid,i))
   else:roads.append((l,wid))
  continue
 if len(v)<4 or v[0]!=v[-1]:continue
 p=Polygon(v).buffer(0)
 if p.is_empty or not camp.covers(p.representative_point()):continue
 if t.get('building'):structures.append((i,p,t))
 elif t.get('natural')=='water':water.append(p)
 elif t.get('highway')=='pedestrian' and t.get('area')=='yes':plazas.append(p)
 elif i in FIELD_IDS:continue
 elif t.get('leisure') in ['pitch','track']:COURT_IDS.add(i)
# Plazas are paved before the roads so kerbs read on top of them.
for p in plazas:
 q=px(p);fillm(q,'#c6c2ab');paint(q.boundary.buffer(.7),'#b3ae97')
for l,w in sorted(roads,key=lambda a:-a[1]):
 g=px(l.buffer(w*.5,cap_style=2,join_style=2))
 paint(g.buffer(1.6),'#8b8c80' if w>=9 else '#a4a58a')
 paint(g,'#98998c' if w>=10 else ('#a8a89b' if w>=7 else ('#b9b9a3' if w>=4.8 else '#d3c6a4')))
 if w>=4.8:paint(g.boundary.buffer(.65),'#ded5b6')
 if w>=9 and l.geom_type=='LineString':
  for dd in range(0,int(l.length)-1,15):
   q0=l.interpolate(dd);q1=l.interpolate(min(dd+8,l.length))
   D.line([tr(q0.x,q0.y),tr(q1.x,q1.y)],fill='#e6dfc6',width=1)
water.append(lake);wg=px(unary_union(water));wm=Image.new('L',(W,H));paint(wg,255,ImageDraw.Draw(wm),0)
fillm(wg.buffer(4),'#738f7d');fillm(wg,'#548e88')
for s,c in [(20,'#66a292'),(10,'#7eae98'),(4,'#a4b99a')]:overlay(wg.difference(wg.buffer(-s)),c)
for i in range(int(6100*AREA)):
 bx,by,bX,bY=wg.bounds;x=R.randint(int(bx),int(bX));y=R.randint(int(by),int(bY))
 if not wm.getpixel((x,y)):continue
 length=R.randint(2,13);D.line((x,y,x+length,y),fill=R.choice(['#72a99c','#85b7a6','#599592','#a5c4a6']))
 if R.random()<.2:D.line((x-3,y+1,x+2,y+1),fill='#83b3a0')
# 建筑落地影子：太阳在西北，影子压向东南；塔楼影子更长。
def floors_of(i,p,t):
 lv=t.get('building:levels','');return int(lv) if lv.isdigit() else (2 if p.area<800 else 4)
def height_of(i,p,t):
 if i=='259873139':return 146
 if i=='260057933':return 30
 if i=='1135360042':return 34
 return floors_of(i,p,t)*HZ*(13.8 if i in ('260224955','260224953') else 10.6)
sh=Image.new('RGBA',(W,H),(0,0,0,0));sd=ImageDraw.Draw(sh)
for i,p,t in structures:
 q=px(p);h=height_of(i,p,t);dx=min(64,.34*h+4);dy=min(74,.46*h+4)
 paint(translate(q,xoff=dx,yoff=dy),(62,76,62,88),sd)
bg=Image.alpha_composite(bg.convert('RGBA'),sh).convert('RGB');D=ImageDraw.Draw(bg)
# 西区—中区：肥西路斑马线（沿校际连接线画白色斑条）
_la,_lb=LINK_B_AT
_mx,_my=((_la[0]+_lb[0])/2,(_la[1]+_lb[1])/2)
_dx,_dy=_lb[0]-_la[0],_lb[1]-_la[1];_L=math.hypot(_dx,_dy) or 1;_dx,_dy=_dx/_L,_dy/_L
_nx,_ny=-_dy,_dx
for _t in range(-16,17,3):
 _p0=tr(_mx+_dx*_t-_nx*2.6,_my+_dy*_t-_ny*2.6);_p1=tr(_mx+_dx*_t+_nx*2.6,_my+_dy*_t+_ny*2.6)
 D.line([_p0,_p1],fill='#f1e9d2',width=3)
D.line([tr(_la[0],_la[1]),tr(_lb[0],_lb[1])],fill='#c9c3ac',width=1)
# 中区—东区：金寨路地下通道（隧道口 + 虚线走廊）
_ta,_tb=TUNNEL_AT
_tl=LineString([_ta,_tb])
_tg=px(_tl.buffer(6.0))
paint(_tg,'#6f7a86')
paint(_tg.boundary.buffer(.6),'#dfe4e4')
_s0=tr(_ta[0],_ta[1]);_s1=tr(_tb[0],_tb[1])
_steps=26
for _i in range(0,_steps,2):
 _f0=_i/_steps;_f1=min(1,(_i+1)/_steps)
 _q0=(_s0[0]+(_s1[0]-_s0[0])*_f0,_s0[1]+(_s1[1]-_s0[1])*_f0)
 _q1=(_s0[0]+(_s1[0]-_s0[0])*_f1,_s0[1]+(_s1[1]-_s0[1])*_f1)
 D.line([_q0,_q1],fill='#efd79b',width=2)
for _pp,_sg in [(_ta,-1),(_tb,1)]:
 _ex,_ey=tr(_pp[0],_pp[1])
 D.ellipse((_ex-9,_ey-5,_ex+9,_ey+3),fill='#6f7a86')
 D.rectangle((_ex-8,_ey-4,_ex+8,_ey+2),fill='#59626d')
 for _k in range(-6,7,3):
  D.line([(_ex+_k,_ey-1),(_ex+_k+2,_ey+1)],fill='#aab3bb')
 D.rectangle((_ex-9,_ey-6,_ex+9,_ey-4),fill='#7d8792')
 D.line([(_ex-10,_ey-6),(_ex+10,_ey-6)],fill='#c8d0d4')

# ---------------------------------------------------------------------------
# 西区田径场：400 m 标准跑道（8 道 × 1.22 m，tartan 面层）+ 105×68 m 人造草皮球场。
# 场地外框取 OSM 259869887（约 96 × 180 m），跑道对齐南北轴。
fground=poly('259869887')
_fp=[rw(x,y) for x,y in fground.exterior.coords]
FCX=(min(p[0] for p in _fp)+max(p[0] for p in _fp))/2;FCY=(min(p[1] for p in _fp)+max(p[1] for p in _fp))/2
FHU=(max(p[0] for p in _fp)-min(p[0] for p in _fp))/2;FHV=(max(p[1] for p in _fp)-min(p[1] for p in _fp))/2
def F(u,v):return (round((FCX+u)*S+TX),round(TY-(FCY+v)*K))
STRAIGHT=84.39;RIN=36.5;LANEW=1.22;NLANE=8;ROUT=RIN+LANEW*NLANE;HLEN=STRAIGHT/2
TRACK='#a2593f';TRACK_D='#8f4c36';TRACK_L='#b26a4c';LANE='#d8cbac';KERB='#efe6cd'
TURF='#6d9560';TURF_L='#739c65';TURF_D='#678f5a';CLINE='#eee7cf'
SAND='#dccb9f';SAND_D='#cbb98c';APRON='#c7c2ab';APRON_D='#b7b19a'
def st_pts(cu,cv,hl,r,n=40):
 p=[(cu-r,cv-hl)]
 for i in range(n+1):
  a=math.pi*(1-i/n);p.append((cu+r*math.cos(a),cv+hl+r*math.sin(a)))
 p.append((cu+r,cv-hl))
 for i in range(1,n+1):
  a=-math.pi*i/n;p.append((cu+r*math.cos(a),cv-hl+r*math.sin(a)))
 return p
def in_st(u,v,hl,r):
 a=abs(v)
 return abs(u)<=r if a<=hl else (u*u+(a-hl)**2)<=r*r
def scr(pl):return [(round((FCX+u)*S+TX),round(TY-(FCY+v)*K)) for u,v in pl]
def fpoly(pl,col):D.polygon(scr(pl),fill=col)
def seg1(d,a,b,col):
 x0,y0=a;x1,y1=b
 n=int(max(abs(x1-x0),abs(y1-y0)))
 if n<=0:d.point((int(x0),int(y0)),fill=col);return
 for i in range(n+1):d.point((round(x0+(x1-x0)*i/n),round(y0+(y1-y0)*i/n)),fill=col)
def poly1(d,pl,col,closed=False):
 pl=list(pl)
 if closed:pl=pl+[pl[0]]
 for a,b in zip(pl,pl[1:]):seg1(d,a,b,col)
def fline(pl,col,w=1,closed=False):
 s=scr(pl)
 if w<=1:poly1(D,s,col,closed)
 else:
  if closed:s=s+[s[0]]
  D.line(s,fill=col,width=w)
def frect(u0,v0,u1,v1,col):
 x0,y0=F(u0,v1);x1,y1=F(u1,v0)
 xa,xb=sorted((x0,x1-1));ya,yb=sorted((y0,y1-1))
 D.rectangle((xa,ya,max(xa,xb),max(ya,yb)),fill=col)
def fell(cu,cv,r,col,w=0):
 x,y=F(cu,cv);bb=(round(x-r*S),round(y-r*K),round(x+r*S),round(y+r*K))
 if w:D.ellipse(bb,outline=col,width=w)
 else:D.ellipse(bb,fill=col)
def farc(cu,cv,r,a0,a1,col,w=1):
 x,y=F(cu,cv);D.arc((round(x-r*S),round(y-r*K),round(x+r*S),round(y+r*K)),a0,a1,fill=col,width=w)
def patch(pl,colfn):
 s=scr(pl);xs=[p[0] for p in s];ys=[p[1] for p in s];ox,oy=min(xs),min(ys);ww=max(xs)-ox+2;hh=max(ys)-oy+2
 im=Image.new('RGB',(ww,hh),colfn(0));dd=ImageDraw.Draw(im);colfn(1,dd,ww,hh)
 mk=Image.new('L',(ww,hh),0);ImageDraw.Draw(mk).polygon([(x-ox,y-oy) for x,y in s],fill=255)
 bg.paste(im,(ox,oy),mk)
# 场地铺装、伸缩缝与颗粒
frect(-FHU,-FHV,FHU,FHV,APRON)
for u in range(-46,47,6):fline([(u,-FHV+1),(u,FHV-1)],APRON_D)
for v in range(-88,89,6):fline([(-FHU+1,v),(FHU-1,v)],APRON_D)
for j in range(2600):
 u=R.uniform(-FHU,FHU);v=R.uniform(-FHV,FHV);x,y=F(u,v)
 D.point((x,y),fill=R.choice([APRON_D,'#d0cbb4','#bfb9a1']))
# 跑道面层、颗粒、分道线、内沿
fpoly(st_pts(0,0,HLEN,ROUT),TRACK)
for j in range(13000):
 u=R.uniform(-ROUT,ROUT);v=R.uniform(-HLEN-ROUT,HLEN+ROUT)
 if not in_st(u,v,HLEN,ROUT) or in_st(u,v,HLEN,RIN+1.1):continue
 x,y=F(u,v);D.point((x,y),fill=R.choice([TRACK_D,TRACK_L,'#a75f45','#b06a4b']))
for k in range(1,NLANE):fline(st_pts(0,0,HLEN,RIN+LANEW*k),LANE,closed=True)
fline(st_pts(0,0,HLEN,RIN),KERB,closed=True)
fline(st_pts(0,0,HLEN,ROUT),'#8a4a35',closed=True)
# 内场草皮：南北向割草条纹
def turf_paint(mode,dd=None,ww=None,hh=None):
 if mode==0:return TURF
 x0=F(-RIN,-(HLEN+RIN))[0]
 for i in range(-9,9):
  xa=round(x0+i*5*S)-x0
  dd.rectangle((xa,0,xa+round(5*S)-1,hh),fill=TURF_L if i%2==0 else TURF_D)
patch(st_pts(0,0,HLEN,RIN),turf_paint)
# 足球场画线 105 × 68 m
PW,PL=34,52.5
fline([(-PW,-PL),(PW,-PL),(PW,PL),(-PW,PL)],CLINE,closed=True)
fline([(-PW,0),(PW,0)],CLINE);fell(0,0,9.15,CLINE,1);fell(0,0,.18,CLINE)
for s in (-1,1):
 vg=s*PL
 fline([(-20.16,vg),(-20.16,s*(PL-16.5)),(20.16,s*(PL-16.5)),(20.16,vg)],CLINE)
 fline([(-9.16,vg),(-9.16,s*(PL-5.5)),(9.16,s*(PL-5.5)),(9.16,vg)],CLINE)
 fell(0,s*41.5,.18,CLINE)
 if s>0:farc(0,s*41.5,9.15,0,180,CLINE)
 else:farc(0,s*41.5,9.15,180,360,CLINE)
farc(PW,PL,1,90,180,CLINE);farc(-PW,PL,1,0,90,CLINE)
farc(PW,-PL,1,180,270,CLINE);farc(-PW,-PL,1,270,360,CLINE)
# 球门（俯视：门柱与球网）
for s in (1,-1):
 vg=s*PL;vb=s*(PL+2.1)
 frect(-3.66,min(vg,vb),3.66,max(vg,vb),'#b6bda3')
 for hh in (-2.4,-1.2,0,1.2,2.4):fline([(hh,vg),(hh,vb)],'#d9dfc7')
 fline([(-3.66,vg),(-3.66,vb),(3.66,vb),(3.66,vg)],'#eef1de')
 fline([(-3.66,vg),(3.66,vg)],'#8f9684',1)
 fell(-3.66,vg,.3,'#7d8571');fell(3.66,vg,.3,'#7d8571')
# 终点线与分道标记（东直道）
fline([(RIN+0.2,15),(ROUT-0.2,15)],'#f7f0da',2)
# 北端铅球区（位置取自 OSM 铅球沙坑）
for cu,cv in [(-17.0,55.0),(19.0,55.0)]:
 a0,a1=math.radians(75),math.radians(105)
 fan=[(cu,cv)]+[(cu+8*math.cos(a0+(a1-a0)*i/12),cv+8*math.sin(a0+(a1-a0)*i/12)) for i in range(13)]
 fpoly(fan,'#d3c097')
 fline([(cu,cv),(cu+8*math.cos(a0),cv+8*math.sin(a0))],'#bcae88')
 fline([(cu,cv),(cu+8*math.cos(a1),cv+8*math.sin(a1))],'#bcae88')
 fell(cu,cv,1.07,'#b0aa96');fell(cu,cv,1.07,'#e3ddc6',1);fell(cu,cv,.12,'#8b7a58')
 fline([(cu-.6,cv-.9),(cu-.6,cv+.9)],'#8b7a58',2)
# 南端跳远：助跑道 + 起跳板 + 沙坑
JU=15.0
frect(JU-.61,-64,JU+.61,-53.2,'#ab8a74')
fline([(JU-.61,-53.2),(JU-.61,-64),(JU+.61,-64),(JU+.61,-53.2)],'#e3d8bd')
frect(JU-1.375,-73,JU+1.375,-64.2,SAND)
for j in range(240):
 u=R.uniform(JU-1.3,JU+1.3);v=R.uniform(-72.8,-64.4);x,y=F(u,v);D.point((x,y),fill=R.choice([SAND_D,'#e5d6ad','#bfa87e']))
frect(JU-.61,-64.35,JU+.61,-64.05,'#f2ead2')
# 四角灯塔、场边长凳、场内几棵树
for su in (-1,1):
 for sv in (-1,1):
  sx,sy=F(su*42,sv*82);obj('flood',sx-17,sy-80,sy)
for su in (-1,1):
 sx,sy=F(su*44.2,66);obj('bench',sx-15,sy-30,sy);sx,sy=F(su*44.2,-66);obj('bench',sx-15,sy-30,sy)
# 围栏（东侧留门）
def fence_line(u0,v0,u1,v1,gaps=()):
 horiz=v0==v1
 a,b=sorted((u0,u1) if horiz else (v0,v1));segs=[(a,b)]
 for g0,g1 in gaps:
  ns=[]
  for s0,s1 in segs:
   if g1<=s0 or g0>=s1:ns.append((s0,s1));continue
   if s0<g0:ns.append((s0,g0))
   if g1<s1:ns.append((g1,s1))
  segs=ns
 for s0,s1 in segs:
  if horiz:fline([(s0,v0),(s1,v0)],'#7d8571')
  else:fline([(u0,s0),(u0,s1)],'#7d8571')
  for t in range(int(s0),int(s1)+1,4):
   if horiz:fell(t,v0,.18,'#68715f')
   else:fell(u0,t,.18,'#68715f')
fence_line(-FHU,-FHV,FHU,-FHV);fence_line(-FHU,FHV,FHU,FHV)
fence_line(-FHU,-FHV,-FHU,FHV);fence_line(FHU,-FHV,FHU,FHV,gaps=[(-5,5)])
# ---------------------------------------------------------------------------
# 篮球场与排球场：补地面与画线（原来只有一块空白色块）
def court_paint(i,p,t):
 pp=[rw(x,y) for x,y in p.exterior.coords]
 u0=min(a[0] for a in pp);u1=max(a[0] for a in pp);v0=min(a[1] for a in pp);v1=max(a[1] for a in pp)
 w=u1-u0;h=v1-v0;basket=t.get('sport')=='basketball'
 base='#a49c86' if basket else '#9fa393'
 x0,y0=fm(u0,v1);x1,y1=fm(u1,v0)
 D.rectangle((x0,y0,x1,y1),fill=base)
 for j in range(int(w*h*.9)):
  D.point((R.randint(x0,x1),R.randint(y0,y1)),fill=R.choice(['#9d9580','#aca48d','#96907b']))
 cx,cy=(u0+u1)/2,(v0+v1)/2
 def L(a,b,col='#efe8d0'):D.line([fm(*a),fm(*b)],fill=col)
 def C(cu,cv,r,col='#efe8d0'):
  x,y=fm(cu,cv);D.ellipse((round(x-r*S),round(y-r*S),round(x+r*S),round(y+r*S)),outline=col,width=1)
 def one(cu,cv,bl,bw,vert):
  if vert:rect=[(cu-bw/2,cv-bl/2),(cu+bw/2,cv+bl/2)]
  else:rect=[(cu-bl/2,cv-bw/2),(cu+bl/2,cv+bw/2)]
  (a,b),(c,e)=rect
  L((a,b),(c,b));L((c,b),(c,e));L((c,e),(a,e));L((a,e),(a,b))
  if basket:
   if vert:
    L((a,cv),(c,cv));C(cu,cv,1.8)
    for s in (-1,1):
     vb=cv+s*bl/2;vl=cv+s*(bl/2-5.8)
     L((cu-2.45,vb),(cu-2.45,vl));L((cu+2.45,vb),(cu+2.45,vl));L((cu-2.45,vl),(cu+2.45,vl));C(cu,vl,1.8)
     hx,hy=fm(cu,vb-s*1.575);D.rectangle((hx-2,hy-1,hx+2,hy+1),fill='#c07a5e')
   else:
    L((cu,b),(cu,e));C(cu,cv,1.8)
    for s in (-1,1):
     ub=cu+s*bl/2;ul=cu+s*(bl/2-5.8)
     L((ub,cv-2.45),(ul,cv-2.45));L((ub,cv+2.45),(ul,cv+2.45));L((ul,cv-2.45),(ul,cv+2.45));C(ul,cv,1.8)
     hx,hy=fm(ub-s*1.575,cv);D.rectangle((hx-1,hy-2,hx+1,hy+2),fill='#c07a5e')
  else:
   if vert:
    L((a,cv),(c,cv))
    for s in (-1,1):L((a,cv+s*3),(c,cv+s*3),'#c8c2a8')
   else:
    L((cu,b),(cu,e))
    for s in (-1,1):L((cu+s*3,b),(cu+s*3,e),'#c8c2a8')
 if basket:
  bl,bw=28,15
  if w>=h:
   if w>=2*bl+3:
    for du in [-(bl+1.5),bl+1.5]:one(cx+du,cy,bl,bw,False)
   else:one(cx,cy,min(bl,w-3),bw,False)
  else:
   if h>=2*bl+3:
    for du in [-(bl+1.5),bl+1.5]:one(cx,cy+du,bl,bw,True)
   else:one(cx,cy,bw,min(bl,h-3),True)
 else:
  cl,cw=18,9
  one(cx,cy,cl if h>=w else cw,cw if h>=w else cl,h>=w)
for i in sorted(COURT_IDS):
 p=Polygon(pts(ways[i])).buffer(0);court_paint(i,p,tags(ways[i]))
# ---------------------------------------------------------------------------
# 树木、路灯、长凳、灯塔图元
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
 im=Image.new('RGBA',(30,84));d=ImageDraw.Draw(im)
 if kind=='lamp':
  d.ellipse((8,28,23,31),fill='#87977d');d.line((15,29,15,9),fill='#445a50',width=2);d.rectangle((12,4,18,10),fill='#506454');d.rectangle((13,5,17,8),fill='#f5da97');d.polygon([(11,4),(15,1),(19,4)],fill='#4e6254')
 elif kind=='flood':
  d.ellipse((12,78,26,82),fill='#8b9a82');d.line((19,80,19,30),fill='#6b7568',width=2)
  d.line((19,72,19,34),fill='#8c9484',width=1)
  d.line((11,30,27,30),fill='#55635a',width=2)
  for dx in (-7,0,7):
   d.rectangle((19+dx-2,22,19+dx+2,30),fill='#4d5a53');d.rectangle((19+dx-2,27,19+dx+2,29),fill='#f3e2ac')
   d.line((19+dx-2,22,19+dx+2,22),fill='#3d4a44')
   d.line((19+dx,30,19+dx,32),fill='#55635a')
 else:
  d.line((4,26,4,31),fill='#4f6458',width=2);d.line((24,23,24,28),fill='#4f6458',width=2);d.polygon([(1,24),(22,19),(28,22),(6,28)],fill='#9f7455');d.line((2,23,22,18),fill='#d4b386',width=2);d.line((1,18,23,13),fill='#a78460',width=3)
 return im
for k in ['lamp','bench','flood']:stash(furnishing(k),k)
def _rgb(c):return (int(c[1:3],16),int(c[3:5],16),int(c[5:7],16))
def _hex(r,g,b):return '#%02x%02x%02x'%(max(0,min(255,int(r))),max(0,min(255,int(g))),max(0,min(255,int(b))))
def jit(c,f):
 r,g,b=_rgb(c);return _hex(r*f,g*f,b*f)
def mixc(a,b,t):
 (r1,g1,b1),(r2,g2,b2)=_rgb(a),_rgb(b);return _hex(r1+(r2-r1)*t,g1+(g2-g1)*t,b1+(b2-b1)*t)
# 立面/屋面样式：按建筑功能分配，避免整片同色同窗。
STY={
 'lib':   dict(wall='#bd8a5e',band='#f0e6ca',win='#3c565c',roof='#a79e8a',trim='#f8efd6',mode='grid',plinth='#8e5c42',accent='#8f4f3c'),
 'teach': dict(wall='#e6e0cc',band='#fbf6e6',win='#4d6d74',roof='#c0bba9',trim='#ffffff',mode='ribbon',plinth='#bdb6a0',accent='#7d9a94'),
 'lab':   dict(wall='#cbc8b9',band='#e6e3d2',win='#3f5d67',roof='#b6b5aa',trim='#dfdccb',mode='slit',plinth='#9a978a',accent='#8b9a92'),
 'dorm':  dict(wall='#e3d7c0',band='#f2e8d1',win='#4e7176',roof='#bdb29b',trim='#f4ecd8',mode='balcony',plinth='#b3a68e',accent='#c07f63'),
 'canteen':dict(wall='#dcbe92',band='#f2e6c8',win='#47636a',roof='#b4a184',trim='#f6ecd2',mode='curtain',plinth='#a8875f',accent='#b06a4c'),
 'hall':  dict(wall='#c6c8be',band='#dcded2',win='#4a646a',roof='#aeb4b0',trim='#e6e8dc',mode='slit',plinth='#93958c',accent='#7f8a86'),
 'old':   dict(wall='#b67d64',band='#eddfc2',win='#435c5e',roof='#9c8b79',trim='#efe3c6',mode='grid',plinth='#8a5741',accent='#6f4636'),
 'admin': dict(wall='#ddcba6',band='#f6ecd3',win='#4a666d',roof='#c6bca7',trim='#faf1d8',mode='fin',plinth='#b0a081',accent='#a8916a'),
 'glass': dict(wall='#cfd6d0',band='#eae4d2',win='#4e7c84',roof='#aab6b0',trim='#f0f0e2',mode='curtain',plinth='#9fa79f',accent='#5f8b8b'),
 'brick': dict(wall='#b57f5f',band='#ecdcc0',win='#42595c',roof='#a8927a',trim='#f0e2c6',mode='grid',plinth='#8d5c44',accent='#7a4a37'),
}
# 标志性建筑按 id 指定样式与配色，避免整片同质化。
OVR={
 '1135310331':dict(k='glass',wall='#d2d8cf',win='#4a7d86',roof='#93a49f'),
 '259873143':dict(k='admin',wall='#e8ddc2',roof='#bcae90',mode='fin'),
 '259873145':dict(k='lab',wall='#c9c6b6',roof='#a9a89c'),
 '259864720':dict(k='canteen',wall='#d9c49b',roof='#a99274',mode='curtain',win='#4a6a70'),
 '259865848':dict(k='old',wall='#b57a60',roof='#8d7a6a',floors=1),
 '259864721':dict(k='lab',wall='#c2bfae',roof='#9e9d90'),
 '413594149':dict(k='hall',wall='#c9ccbf',roof='#9aa3a0'),
 '413594151':dict(k='old',wall='#b58066',roof='#8f7d6c'),
 '259869889':dict(k='old',wall='#a9715b',roof='#87786a'),
 '260058591':dict(k='canteen',wall='#d8bb8e',roof='#a68f6c'),
 '259862456':dict(k='admin',wall='#ded0ae',roof='#b6a88c'),
 '260059093':dict(k='brick',wall='#a9714f',roof='#94806a',mode='grid'),
 '1135310388':dict(k='glass',wall='#d6dcd2',win='#527f86',roof='#9aa8a0'),
 '260057936':dict(k='lab',wall='#bfbdae',roof='#a3a296'),
}
for _k,_v in STY.items():
 _v['shade']=jit(_v['wall'],.82);_v['roofd']=jit(_v['roof'],.9)
KW=[('图书馆','lib'),('食堂','canteen'),('教学','teach'),('活动中心','hall'),('体育','hall'),
    ('大厅','hall'),('仓库','hall'),('光源','hall'),('实验','lab'),('研究','lab'),('中心','lab'),
    ('专家楼','old'),('小楼','old'),('四合院','old'),('站','old'),('宿舍','dorm')]
def style_of(p,t,floors,rng):
 nm=t.get('name','')
 for k,s in KW:
  if k in nm:return s
 if t.get('building') in ('dormitory','apartments') or (nm and nm.strip('#').isdigit()):return 'dorm'
 if p.area>2200 and floors<=3:return 'hall'
 if floors>=9:return 'lab'
 return rng.choice(['teach','teach','admin','lab','dorm'])
def art_build(i,p,t):
 q=px(p);minx,miny,maxx,maxy=q.bounds;origin=(int(minx)-45,int(miny)-330)
 ww,hh=int(maxx)-origin[0]+55,int(maxy)-origin[1]+40;im=Image.new('RGBA',(ww,hh));d=ImageDraw.Draw(im);rng=random.Random(int(i))
 ox,oy=origin;pol=lambda a,c:d.polygon([(round(x-ox),round(y-oy)) for x,y in a],fill=c)
 def line(a,c,w=1):
  qq=[(round(x-ox),round(y-oy)) for x,y in a]
  if w<=1:poly1(d,qq,c)
  else:d.line(qq,fill=c,width=w)
 name=t.get('name','');lv=t.get('building:levels','');floors=int(lv) if lv.isdigit() else (2 if p.area<800 else 4)
 key=style_of(p,t,floors,rng)
 ov=OVR.get(i)
 if ov:
  key=ov.get('k',key)
 st=dict(STY[key])
 jf=rng.uniform(.94,1.06);jd=rng.uniform(.96,1.04)
 if ov:
  for kk in ('wall','band','win','roof','trim','plinth','accent','mode'):
   if kk in ov:st[kk]=ov[kk]
  if 'floors' in ov:floors=ov['floors']
 for kk in ['wall','band','roof','plinth']:st[kk]=jit(st[kk],jf if kk!='band' else jd)
 _tint=rng.choice(['#d8c9a8','#cfd3c4','#e6d3bd','#c9cfd2','#dfd6c0'])
 _amt=rng.uniform(.04,.16)
 st['wall']=mixc(st['wall'],_tint,_amt)
 st['roof']=mixc(st['roof'],_tint,_amt*.6)
 st['shade']=jit(st['wall'],.82);st['roofd']=jit(st['roof'],.9)
 # 屋顶形式：老楼/小体量用坡屋顶，大跨实验室用锯齿屋面，其余平屋顶。
 roof_shape='flat'
 _bb=q.bounds;_rr=q.area/max(1.0,(_bb[2]-_bb[0])*(_bb[3]-_bb[1]))
 if _rr>0.8 and (key=='old' or (p.area<520 and floors<=3 and key in ('teach','admin','dorm'))):roof_shape='gable'
 if key=='hall' and p.area>1800:roof_shape='saw'
 def roof(r,z,st_,shape=None):
  shape=shape or roof_shape
  for g in parts(r):
   if g.is_empty or g.area<.05:continue
   polyline=[(x,y-z) for x,y in g.exterior.coords]
   if shape in ('gable','saw'):
    gx0,gy0,gx1,gy1=g.bounds;n=3 if shape=='saw' else 2
    for k in range(n):
     if (gx1-gx0)>=(gy1-gy0):
      a0=gx0+(gx1-gx0)*k/n;a1=gx0+(gx1-gx0)*(k+1)/n;piece=g.intersection(box(a0,gy0-2,a1,gy1+2))
     else:
      b0=gy0+(gy1-gy0)*k/n;b1=gy0+(gy1-gy0)*(k+1)/n;piece=g.intersection(box(gx0-2,b0,gx1+2,b1))
     for gg in parts(piece):
      if gg.is_empty:continue
      pol([(x,y-z) for x,y in gg.exterior.coords],st_['roof'] if k%2==0 else jit(st_['roof'],.9))
      if shape=='saw':line([(x,y-z) for x,y in gg.exterior.coords],jit(st_['trim'],.88))
    line(polyline,'#6f7365')
    if shape=='gable':
     if (gx1-gx0)>=(gy1-gy0):line([(gx0,gy0-z),(gx1,gy0-z)],st_['trim'],2)
     else:line([(gx0,gy0-z),(gx0,gy1-z)],st_['trim'],2)
    continue
   pol(polyline,st_['roof']);line(polyline,'#777c6e');line(polyline[:2],st_['trim'])
   spts=[(round(x-ox),round(y-oy)) for x,y in polyline]
   mk=Image.new('L',im.size,0);ImageDraw.Draw(mk).polygon(spts,fill=255)
   lay=Image.new('RGBA',im.size,(0,0,0,0));ld=ImageDraw.Draw(lay)
   bx0=min(pp[0] for pp in spts);bx1=max(pp[0] for pp in spts);by0=min(pp[1] for pp in spts);by1=max(pp[1] for pp in spts)
   if bx1-bx0<12 or by1-by0<12:continue
   for yy in range(by0+3,by1-1,5):ld.line([(bx0,yy),(bx1,yy)],fill=(80,84,74,26))
   for xx in range(bx0+8,bx1-1,17):ld.line([(xx,by0),(xx,by1)],fill=(80,84,74,13))
   ld.rectangle((bx0+2,by0+2,bx1-2,by0+4),fill=(255,252,238,26))
   ld.rectangle((bx0+2,by1-4,bx1-2,by1-2),fill=(60,64,56,26))
   cpx,cpy=spts[len(spts)//3]
   if (bx1-bx0)*(by1-by0)>2600 and rng.random()<.55:
    sx0=bx0+rng.randint(6,max(8,(bx1-bx0)//3));sy0=by0+rng.randint(6,max(8,(by1-by0)//3))
    for rr2 in range(rng.randint(2,4)):
     for cc2 in range(rng.randint(2,5)):
      px0=sx0+cc2*7;py0=sy0+rr2*6
      if px0+5>bx1-4 or py0+4>by1-4:continue
      ld.rectangle((px0,py0,px0+5,py0+4),fill=(78,96,104,235))
      ld.line([(px0,py0+4),(px0+5,py0+4)],fill=(58,74,80,235))
   if (bx1-bx0)*(by1-by0)>4200 and rng.random()<.5:
    mx0=bx0+(bx1-bx0)//2-6;my0=by0+(by1-by0)//2-4
    ld.rectangle((mx0+1,my0+1,mx0+13,my0+9),fill=(60,64,56,80))
    ld.rectangle((mx0,my0,mx0+12,my0+8),fill=(168,166,152,255))
    ld.rectangle((mx0,my0,mx0+12,my0+2),fill=(196,194,178,255))
    ld.line([(mx0,my0+8),(mx0+12,my0+8)],fill=(96,98,88,255))
    ld.line([(mx0+12,my0+4),(min(bx1-2,mx0+30),my0+4)],fill=(120,122,110,180))
   for j in range(rng.randint(1,3)):
    vw=rng.randint(4,9);vh=rng.randint(3,6)
    vx=cpx+rng.randint(-14,14)-vw//2;vy=cpy+rng.randint(-9,9)-vh//2
    if vx<bx0+2 or vy<by0+2 or vx+vw>bx1-2 or vy+vh>by1-2:continue
    ld.rectangle((vx+1,vy+1,vx+vw+1,vy+vh+1),fill=(70,74,66,70))
    ld.rectangle((vx,vy,vx+vw,vy+vh),fill=(156,158,146,255))
    ld.rectangle((vx,vy,vx+vw,vy+1),fill=(186,188,174,255))
    ld.line([(vx,vy),(vx+vw,vy)],fill=(110,112,102,255))
   lay.putalpha(ImageChops.multiply(lay.getchannel('A'),mk));im.alpha_composite(lay)
 def terrace(r,z,col):
  for g in parts(r):
   if g.is_empty:continue
   polyline=[(x,y-z) for x,y in g.exterior.coords];pol(polyline,col)
   x0,y0,x1,y1=g.bounds
   for yy in range(int(y0)-100,int(y1)+60,4):
    cut=LineString([(x0-3,yy),(x1+3,yy-(x1-x0)*.16)]).intersection(g)
    for gg in ([cut] if cut.geom_type=='LineString' else getattr(cut,'geoms',[])):
     if gg.geom_type=='LineString' and not gg.is_empty:line([(x,y-z) for x,y in gg.coords],'#ad8a6c')
 def facade(r,z,h,st_,nf,mode=None):
  mode=mode or st_['mode']
  for g in parts(r):
   if g.is_empty or g.area<.05:continue
   ring=list(orient(g,1).exterior.coords);edges=sorted(zip(ring,ring[1:]),key=lambda e:(e[0][1]+e[1][1])/2)
   for (x,y),(u,v) in edges:
    dx,dy=u-x,v-y;L=math.hypot(dx,dy)
    if dx>0 or L<.3:continue
    def pt(t,zz):return (x+dx*t,y+dy*t-zz)
    wall=st_['wall'] if dy<=0 else st_['shade']
    pol([pt(0,z),pt(1,z),pt(1,h),pt(0,h)],wall)
    line([pt(0,h),pt(1,h)],st_['trim'],2)
    line([pt(0,z+.5),pt(1,z+.5)],'#5f6459',1)
    if L<4 or nf<=0:continue
    fh=(h-z)/nf
    pol([pt(0,z),pt(1,z),pt(1,z+min(7,fh*.5)),pt(0,z+min(7,fh*.5))],st_['plinth'])
    if fh<4:continue
    if mode=='curtain':
     pol([pt(.03,z+4),pt(.97,z+4),pt(.97,h-4),pt(.03,h-4)],st_['win'])
     m=max(2,int(L/7))
     for k in range(1,m):line([pt(k/m,z+4),pt(k/m,h-4)],'#8fa3a2')
     for j in range(1,nf):line([pt(0,z+j*fh),pt(1,z+j*fh)],jit(st_['band'],.76),2)
     line([pt(0,z+4),pt(1,z+4)],st_['trim'])
     continue
    for j in range(nf):
     b=z+j*fh+.2*fh;e=z+j*fh+.74*fh
     if mode=='ribbon':
      pol([pt(.05,b),pt(.95,b),pt(.95,e),pt(.05,e)],st_['win'])
      m=max(2,int(L/13))
      for k in range(1,m):line([pt(.05+.9*k/m,b),pt(.05+.9*k/m,e)],mixc(st_['win'],st_['band'],.45))
      line([pt(.03,b-.4),pt(.97,b-.4)],st_['band'])
      if j<nf-1:line([pt(0,z+(j+1)*fh-.6),pt(1,z+(j+1)*fh-.6)],jit(st_['wall'],.88))
     elif mode=='slit':
      n=max(2,int(L/9))
      for k in range(n):
       a=(k+.32)/n;f=(k+.64)/n
       pol([pt(a,b),pt(f,b),pt(f,e),pt(a,e)],st_['win'])
      line([pt(0,z+(j+.94)*fh),pt(1,z+(j+.94)*fh)],jit(st_['wall'],.9))
     elif mode=='balcony':
      pol([pt(.1,b),pt(.9,b),pt(.9,e),pt(.1,e)],st_['win'])
      pol([pt(.02,z+j*fh+.06*fh),pt(.98,z+j*fh+.06*fh),pt(.98,z+j*fh+.3*fh),pt(.02,z+j*fh+.3*fh)],jit(st_['band'],.94))
      line([pt(.02,z+j*fh+.3*fh),pt(.98,z+j*fh+.3*fh)],jit(st_['band'],.76))
      line([pt(.02,z+(j+1)*fh+.2),pt(.98,z+(j+1)*fh+.2)],jit(st_['shade'],.92))
     elif mode=='fin':
      pol([pt(.12,b),pt(.88,b),pt(.88,e),pt(.12,e)],st_['win'])
      n=max(2,int(L/11))
      for k in range(n+1):
       a=.1+.8*k/n
       pol([pt(a-.045,b),pt(a+.045,b),pt(a+.045,h-3),pt(a-.045,h-3)],jit(st_['trim'],.98))
     else:
      n=max(1,int(L/10))
      for k in range(n):
       if L/n<4:continue
       a=(k+.18)/n;f=(k+.78)/n
       pol([pt(a,b),pt(f,b),pt(f,e),pt(a,e)],st_['win'])
       line([pt(a,e),pt(f,e)],mixc(st_['win'],st_['band'],.5))
       line([pt(a,b-.5),pt(f,b-.5)],jit(st_['band'],.95))
   roof(g,h,st_)
 def extra(q,st_):
  minx2,miny2,maxx2,maxy2=q.bounds;cx=(minx2+maxx2)/2;yy=maxy2
  pol([(cx-13,yy),(cx-13,yy-9),(cx+13,yy-9),(cx+13,yy)],jit(st_['shade'],.9))
  pol([(cx-11,yy-2),(cx-11,yy-7),(cx+11,yy-7),(cx+11,yy-2)],st_['win'])
  line([(cx-14,yy-9),(cx+14,yy-9)],st_['trim'],2)
  line([(cx-14,yy),(cx+14,yy)],'#5f6459')
  if p.area>700 and rng.random()<.55:
   tx=cx+rng.uniform(-20,20);ty=miny2+rng.uniform(10,max(12,(maxy2-miny2)*.5))
   pol([(tx-5,ty),(tx-5,ty-7),(tx+5,ty-7),(tx+5,ty)],jit(st_['roof'],.92))
   pol([(tx-5,ty-7),(tx+5,ty-7),(tx+5,ty-9),(tx-5,ty-9)],jit(st_['trim'],.95))
 if i=='1135360042':
  st2=dict(STY['canteen']);st2.update(wall='#6f6f5c',roof='#899583',mode='curtain',win='#426064',band='#d3cbb4',shade='#586858',trim='#c8c9b5')
  terrace(q.buffer(10),2,'#c69e77')
  facade(q,2,17,st2,1)
  roof(q.buffer(2),19,dict(st2,roof='#5e756c'))
  up=q.intersection(box(minx-1,miny-1,(minx+maxx)*.5+12,maxy+1))
  facade(up,19,29,dict(STY['teach'],wall='#e0dbc5',shade='#c4c9af',band='#f0ebd5'),1)
  roof(up,29,dict(STY['teach'],roof='#c8c9b5'))
  for dx,dy in [(-18,1),(8,0),(28,-2)]:
   xx,yy=(minx+maxx)/2+dx,maxy+dy+4;line([(xx,yy),(xx,yy-11)],'#695744',2)
   pol([(xx-8,yy-10),(xx-5,yy-14),(xx+2,yy-17),(xx+9,yy-12),(xx+4,yy-9),(xx-4,yy-8)],'#ebd4a3')
   line([(xx-8,yy-10),(xx+2,yy-17),(xx+4,yy-9)],'#bca983')
  for dx,dy in [(-25,-2),(-3,4),(22,0)]:
   xx,yy=(minx+maxx)/2+dx,maxy+dy
   line([(xx,yy),(xx,yy-4)],'#6e5946',2)
   pol([(xx-3,yy-4),(xx,yy-6),(xx+4,yy-5),(xx+2,yy-3)],'#e0c097')
   line([(xx+5,yy-2),(xx+7,yy-3),(xx+7,yy-5)],'#826747',2)
  xx,yy=maxx-3,maxy-5
  pol([(xx-5,yy),(xx-3,yy-9),(xx+3,yy-9),(xx+4,yy)],'#a2835d');pol([(xx-3,yy-2),(xx-2,yy-8),(xx+2,yy-8),(xx+2,yy-2)],'#47665c')
 elif i=='259873139':
  lib_st=dict(STY['lib'],wall='#cdc1a4',shade='#b0a488',roof='#9aa08e',trim='#efe6cd',mode='grid',win='#3f6068')
  facade(q,0,36,lib_st,3)
  roof(q,36,lib_st)
  cx,cy=p.centroid.coords[0];tower=px(box(cx-10,cy-13,cx+15,cy+20))
  tw=dict(STY['lib'],wall='#b8825a',shade='#986a48',mode='grid',roof='#a1917a')
  facade(tower,36,118,tw,11)
  for a0,b0,a1,b1 in [(cx-8,cy-11,cx-3,cy+16),(cx+7,cy-11,cx+12,cy+16)]:
   cc=px(box(a0,b0,a1,b1));facade(cc,118,126,dict(tw,wall='#c9a27a'),0)
  roof(tower,118,dict(tw,roof='#a89680'))
  xx,yy=tr(cx+3,cy+4);line([(xx-13,yy-125),(xx,yy-138),(xx+14,yy-125),(xx-13,yy-125)],'#f5e8ca',3)
 elif i=='260057933':
  hall_st=dict(STY['hall'],wall='#c6a184',roof='#84999a')
  facade(q,0,26,hall_st,1)
  cx,cy=p.centroid.coords[0];oval=px(scale(Point(cx,cy).buffer(1,quad_segs=30),42,29,origin=(cx,cy))).intersection(q)
  roof(oval,27,dict(hall_st,roof='#84999a'),'flat')
  for rr in [.88,.76,.64,.52]:
   o=scale(oval,rr,rr);line([(x,y-27) for x,y in o.exterior.coords],'#bcc8b7',2)
 else:
  h=floors*(11.9 if '第三' in name else 10.6)
  if key=='hall':h=max(h,14)
  if key=='old':h=min(h,16)
  facade(q,0,h,st,floors)
  extra(q,st)
 bbox=im.getbbox()
 if bbox:
  kk='b'+i;stash(im.crop(bbox),kk);obj(kk,origin[0]+bbox[0],origin[1]+bbox[1],q.bounds[3]-2)
 return name
for i,p,t in structures:
 art_build(i,p,t)
geometry=[p for _,p,_ in structures]
# Bridge decking and handrail. Deck goes on the ground and the front rail is independently sorted.
for l,w,i in bridges:
 gg=px(l.buffer(w*.53,cap_style=2,join_style=2));paint(gg.buffer(1.0),'#747c70');paint(gg,'#e2d3b0')
 if l.geom_type!='LineString':continue
 for off in [-1,1]:
  rail=px(l.offset_curve(off*w*.48))
  if rail.geom_type!='LineString':continue
  a=list(rail.coords);D.line([(round(x),round(y)-3) for x,y in a],fill='#dbd3b9',width=1)
  for v in range(0,int(rail.length),9):
   pt=rail.interpolate(v);x,y=pt.coords[0];D.line((x,y,x,y-5),fill='#ebe3c4',width=2)
avoid=unary_union([*geometry,*water,*plants,*plazas,*[l.buffer(w/2+1.5) for l,w in roads],*[l.buffer(w) for l,w,i in bridges],Polygon([(FCX+u,FCY+v) for u,v in [(-FHU,-FHV),(FHU,-FHV),(FHU,FHV),(-FHU,FHV)]])])
clear=camp.difference(avoid)
taken=set()
def plant(x,y):
 pt=Point(x,y);cell=(round(x/6),round(y/6))
 if cell in taken or not clear.covers(pt):return
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
for j in range(7200):
 x=R.uniform(-845,1210);y=R.uniform(-625,405)
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
TUNNEL=LINK_B.buffer(5.0);bridge=unary_union([l.buffer(w*.6) for l,w,i in bridges]).union(TUNNEL);walk=camp.buffer(-1).difference(unary_union([*geometry,*water])).union(bridge).buffer(-.24)
nav=Image.new('1',(W,H));paint(px(walk),1,ImageDraw.Draw(nav),0);nav.save(out/'nav.png')
marks=[]
from shapely.ops import nearest_points
for label,x,y,about in [('九曲桥',-480,150,'曲折的桥面连接湖心岛与西岸，岸线与岛按地图轮廓绘制。'),('西区 1958',-393,124,'沿水岸可以看到外挑的平台、深色窗框和低矮的白墙。'),('西区图书馆',-300,145,'低裙房托起赭色塔楼，浅色顶带和屋顶标志勾出天际线。'),('第三教学楼',-525,53,'A、B 楼的楼翼折转相接，邻近 C 楼较低。'),('同步辐射实验室',-728,-221,'实验大厅位于西区西南部。屋顶细节为游戏化示意。'),('西区学生食堂',-620,302,'食堂及学生宿舍位于北侧生活区。'),('西区田径场',-751.3,147.7,'400 米八道塑胶跑道环抱人造草皮球场；北端铅球区，南端跳远沙坑。'),('肥西路校门',-50,78,'西区与中区隔肥西路相望，斑马线两侧各有一道校门。'),('中区学生活动中心',55,47,'中区北侧的活动中心，镜渊最早的测试点之一。'),('金寨路地下通道',610,84,'中区与东区之间的地下通道，下穿金寨路，灯带常年不熄。'),('东区图书馆',840,-106,'东区中轴上的图书馆，六层，阅览室朝南。'),('第一教学楼',764,105,'东区最老的教学楼之一，浅墙、长窗与灰檐。'),('东区学生食堂',968,-101,'东区食堂，通高玻璃幕墙。'),('礼堂',723,-418,'东区礼堂，坡屋面藏在树里。')]:
 pt=nearest_points(walk.buffer(-1),Point(x,y))[0];sx,sy=tr(pt.x,pt.y);marks.append(dict(name=label,x=sx,y=sy,about=about))
lb=px(lake).bounds
lcx,lcy=(lb[0]+lb[2])/2,(lb[1]+lb[3])/2
lw,ls=lake.centroid.x,lake.centroid.y
hx,hy=tr(lake.centroid.x,lake.centroid.y)
lakeside=[max(0,round(hx-320)),max(0,round(hy-165)),min(W,round(hx+320)),min(H,round(hy+165))]
bg.save(out/'ground.png',optimize=True);objs.sort(key=lambda o:o[3]);print('scene',len(structures),'buildings,',len(taken),'trees',W,H,flush=True)
print('marks',[m['name'] for m in marks],'lakeside',lakeside,flush=True)
(out/'scene.json').write_text(json.dumps(dict(w=W,h=H,sprites=assets,objects=objs,marks=marks,buildings=len(structures),lakeside=lakeside),ensure_ascii=False,separators=(',',':')),encoding='utf-8')
