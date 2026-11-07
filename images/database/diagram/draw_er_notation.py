"""データベース 03 章 7 節の比較図（鳥の足記法 / UML のクラス図の表記）を描く。

使い方:
    python3 draw_er_notation.py er    # er.svg と er_svg.html を出力
    python3 draw_er_notation.py uml   # uml.svg と uml_svg.html を出力

PNG にするときは、出力した HTML を Chrome で開いて書き出す（例）:
    google-chrome --headless=new --hide-scrollbars --force-device-scale-factor=2 \
        --window-size=700,760 --screenshot=$PWD/er.png file://$PWD/er_svg.html
書き出した後、余白を切り取って er-03-01-crows-foot.png / er-03-02-uml.png として保存する。
2 枚の大きさを揃えるため、両方に同じ範囲の切り取りを使う。
"""
import math, sys
F='"Noto Sans CJK JP", sans-serif'
MODE=sys.argv[1]  # 'er' or 'uml'
attrs = {
 'Department': [('string','name')],
 'Teacher':    [('string','name')],
 'Student':    [('string','name'),('int','enrolled_year')],
 'Course':     [('string','title'),('int','credits')],
 'Enrollment': [('int','academic_year'),('int','score')],
}
pos = {'Department':(230,20),'Teacher':(430,150),'Student':(30,340),'Course':(430,340),'Enrollment':(230,550)}
W,H,L=180,36,24
bh=lambda n: H+12+L*len(attrs[n])
s=[]
for n,(x,y) in pos.items():
    s+= [f'<rect x="{x}" y="{y}" width="{W}" height="{bh(n)}" fill="#ECECFF" stroke="#9370DB" stroke-width="1.5"/>',
         f'<line x1="{x}" y1="{y+H}" x2="{x+W}" y2="{y+H}" stroke="#9370DB" stroke-width="1.5"/>',
         f'<text x="{x+W/2}" y="{y+24}" text-anchor="middle" font-weight="bold" font-size="16">{n}</text>']
    for i,(t,a) in enumerate(attrs[n]):
        ty=y+H+24+L*i
        if MODE=='er':
            s+= [f'<text x="{x+12}" y="{ty}" font-size="14" fill="#666">{t}</text>', f'<text x="{x+66}" y="{ty}" font-size="14">{a}</text>']
        else:
            T={'string':'String','int':'int'}[t]
            s.append(f'<text x="{x+12}" y="{ty}" font-size="14">{a} : {T}</text>')
def bottom(n,dx=0): x,y=pos[n]; return (x+W/2+dx,y+bh(n))
def top(n,dx=0): x,y=pos[n]; return (x+W/2+dx,y)
rels=[(bottom('Department',-50),top('Student'),'所属'),(bottom('Department',50),top('Teacher'),'所属'),
      (bottom('Teacher'),top('Course'),'担当'),(bottom('Student'),top('Enrollment',-50),'履修する'),
      (bottom('Course'),top('Enrollment',50),'履修される')]
CX,CY=320,350; MC='#C2185B'
def unit(px,py,qx,qy):
    d=math.hypot(qx-px,qy-py); return (qx-px)/d,(qy-py)/d
def mult(px,py,qx,qy,t,at_bottom):
    ux,uy=unit(px,py,qx,qy); ax,ay=px+ux*30,py+uy*30
    nx,ny=-uy,ux
    if nx*(CX-ax)+ny*(CY-ay)<0: nx,ny=-nx,-ny
    if abs(nx)<0.3: nx,ny=-1,0
    tx,ty=ax+nx*12,ay+ny*12+(12 if at_bottom else -2)
    anc='start' if nx>0.3 else 'end' if nx<-0.3 else 'middle'
    return tx,ty,anc
def ln(a,b,c,d,w=1.8): return f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c:.1f}" y2="{d:.1f}" stroke="{MC}" stroke-width="{w}"/>'
def one(px,py,qx,qy):          # ||：ちょうど 1
    ux,uy=unit(px,py,qx,qy); nx,ny=-uy,ux; out=[]
    for k in (10,17):
        cx,cy=px+ux*k,py+uy*k; out.append(ln(cx-nx*8,cy-ny*8,cx+nx*8,cy+ny*8))
    return out
def zero_many(px,py,qx,qy):    # o{：0 以上
    ux,uy=unit(px,py,qx,qy); nx,ny=-uy,ux; fx,fy=px+ux*16,py+uy*16
    out=[ln(fx,fy,px+nx*9,py+ny*9),ln(fx,fy,px,py),ln(fx,fy,px-nx*9,py-ny*9)]
    cx,cy=px+ux*24,py+uy*24
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" fill="#fff" stroke="{MC}" stroke-width="1.8"/>')
    return out
for (x1,y1),(x2,y2),lab in rels:
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="1.5"/>')
    mx,my=(x1+x2)/2,(y1+y2)/2; tw=15*len(lab)+10
    s+= [f'<rect x="{mx-tw/2}" y="{my-12}" width="{tw}" height="24" fill="#fff"/>',
         f'<text x="{mx}" y="{my+5}" text-anchor="middle" font-size="14">{lab}</text>']
    if MODE=='er':
        s+= one(x1,y1,x2,y2) + zero_many(x2,y2,x1,y1)
    else:
        a=mult(x1,y1,x2,y2,'1',True); b=mult(x2,y2,x1,y1,'0..*',False)
        if lab=='所属' and x2>x1: b=(530,140,'start')   # Department–Teacher は線の外側に置く
        for (tx,ty,anc),t in ((a,'1'),(b,'0..*')):
            s.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anc}" font-size="15" font-weight="bold" fill="{MC}">{t}</text>')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="680" font-family=\'{F}\' fill="#333">'+''.join(s)+'</svg>'
open(f'{MODE}.svg','w').write(svg)
open(f'{MODE}_svg.html','w').write('<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#fff}</style>'+svg)
