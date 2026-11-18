"""AI-kabelaua prinditavad osad. Maailmakoordinaadid nagu geom.json-is (x paremale, y üles, z mängija poole).
Iga osa kirjutatakse CSG-käsufailiks, mille tool/csg teeb STL-iks."""
import json, math
G=json.load(open('geom.json')); D=G['dims']; POS=G['pos']
OX,OUT,HB,SQ=D['OX'],D['OUT'],D['HB'],D['SQ']; CZ0,CZ1,CH=D['CZ0'],D['CZ1'],D['CH']
TOPY0,TOPY1=33.0,34.0
fx=lambda f:-HB+SQ*(f+0.5); rz=lambda r:HB-SQ*(r+0.5)
ZB=[HB-SQ*k for k in range(1,8)]  # ridade vahelised piirid
XB=[-HB+SQ*k for k in range(1,8)]
class Part:
    def __init__(s,name,flipY=None): s.n=name; s.L=[]; s.flip=flipY
    def _y(s,y0,y1): return (s.flip-y1,s.flip-y0) if s.flip is not None else (y0,y1)
    def _z(s,z0,z1): return (z0,z1) if s.flip is not None else (-z1,-z0)
    def _zp(s,z): return z if s.flip is not None else -z
    def box(s,x0,x1,y0,y1,z0,z1,op='+'):
        Y0,Y1=s._z(min(z0,z1),max(z0,z1)); Z0,Z1=s._y(min(y0,y1),max(y0,y1))
        s.L.append(f'{op} B {min(x0,x1):.3f} {Y0:.3f} {Z0:.3f} {max(x0,x1):.3f} {Y1:.3f} {Z1:.3f}')
    def vcyl(s,x,z,y0,y1,r,op='+',r1=None,seg=48):
        Z0,Z1=s._y(y0,y1)
        if r1 is None: s.L.append(f'{op} C {x:.3f} {s._zp(z):.3f} {Z0:.3f} {Z1:.3f} {r:.3f} {seg}')
        else:
            ra,rb=(r,r1) if s.flip is None else (r1,r)
            s.L.append(f'{op} K {x:.3f} {s._zp(z):.3f} {Z0:.3f} {Z1:.3f} {ra:.3f} {rb:.3f} {seg}')
    def xcyl(s,y,z,x0,x1,r,op='+'):
        Zc=s._y(y,y)[0]; s.L.append(f'{op} X {s._zp(z):.3f} {Zc:.3f} {x0:.3f} {x1:.3f} {r:.3f}')
    def zcyl(s,x,y,z0,z1,r,op='+'):
        Zc=s._y(y,y)[0]; Y0,Y1=s._z(z0,z1); s.L.append(f'{op} Y {x:.3f} {Zc:.3f} {Y0:.3f} {Y1:.3f} {r:.3f}')
    def clip(s,x0,x1,y0,y1,z0,z1): s.box(x0,x1,y0,y1,z0,z1,'*')
    def save(s): open(f'csg/{s.n}.csg','w').write('\n'.join(s.L)+'\n'); return s.n
def ring(p,x0,x1,z0,z1,t,y0,y1):
    p.box(x0-t,x1+t,y0,y1,z0-t,z0); p.box(x0-t,x1+t,y0,y1,z1,z1+t); p.box(x0-t,x0,y0,y1,z0,z1); p.box(x1,x1+t,y0,y1,z0,z1)
M3=1.7
LED_R=3.5   # LED-ava raadius pealmises plaadis ja tumedates ruutudes
# ---------------- LAUD (põhi) ----------------
def board_base(p):
    p.box(-OX,OX,0,2,-OUT,OUT)                              # põhi
    p.box(-OX,OX,0,TOPY0,-OUT,-HB)                          # tagasein
    for sx in(-1,1):
        p.box(sx*(OX-5),sx*OX,0,TOPY0,-OUT,OUT)             # külgseinad
        p.box(sx*HB,sx*(HB+1.5),0,26,-HB,HB)                # pöördetasku vahesein (riba läheb üle)
    for b in G['boxes']:
        if b['c']=='post': p.box(b['x0'],b['x1'],0,TOPY0,b['z0'],b['z1'])
    # sambad pealmise plaadi ribide all (3 x 3 mm), mitte MCP / juhtmekimbu alas
    for xb in XB:
        if xb<-80: continue
        for zb in ZB: p.box(xb-2,xb+2,2,28.8,zb-2,zb+2)
    # MCP23017 hällid (moodul 21 x 26,5)
    for mx,mz in POS['MCP']:
        ring(p,mx-11.1,mx+11.1,mz-13.85,mz+13.85,1.2,2,8)
        for dx in(-1,1):
            for dz in(-1,1): p.box(mx+dx*10.1-1.5,mx+dx*10.1+1.5,2,4,mz+dz*12.85-1.5,mz+dz*12.85+1.5)
    # liiteklotsid koos M3 aukudega
    for zc in(-120,-50,50,120):
        p.box(-8,8,2,12,zc-5,zc+5); p.xcyl(7,zc,-9,9,M3,'-')
    for xc in(-150,-50,50,150):
        p.box(xc-5,xc+5,2,12,-8,8); p.zcyl(xc,7,-9,9,M3,'-')
    for xc in(-150,-20,45,110):
        p.box(xc-5,xc+5,2,12,OUT-8,OUT); p.zcyl(xc,7,OUT-9,OUT+1,M3,'-')
# ---------------- PEALMINE PLAAT ----------------
def top_plate(p):
    p.box(-OX,OX,TOPY0,TOPY1,-OUT,OUT)
    for zb in ZB: p.box(-HB,HB,29,TOPY0,zb-0.6,zb+0.6)      # ribid ridade vahel
    for sx in(-1,1): p.box(sx*(OX-5.3),sx*(OX-6.8),31,TOPY0,-HB+0.3,OUT-1)   # asetusäär külgseinte sees
    p.box(-OX+6.8,OX-6.8,31,TOPY0,-HB+0.3,-HB+1.8)                          # asetusäär tagaseina ees
    for r in G['reeds']:                                    # reed-lüliti juhikud
        for sz in(-1,1): p.box(r['x0']-0.5,r['x1']+0.5,31,TOPY0,r['z']+sz*1.2,r['z']+sz*2.2)
    for r in G['reeds']:                                    # LED-ava iga tumeda ruudu keskel (Ø 7 mm)
        p.vcyl(r['x0'],r['z'],TOPY0-1.2,TOPY1+0.5,LED_R,'-')
    for r in range(8):                                      # LED-riba klambrid heledate ruutude all
        z=rz(r)
        for f in range((r+1)%2,8,2):
            x=fx(f)
            for sz in(-1,1):
                p.box(x-3,x+3,28.2,TOPY0,z+sz*5.4,z+sz*6.4)
                p.box(x-3,x+3,28.2,29.0,z+sz*4.6,z+sz*5.4)
def tiles():
    p=Part('kabelaud_tumedad_ruudud_32tk')
    for i in range(32):
        x=(i%6)*36; z=(i//6)*36; p.box(x,x+33,0,0.6,z,z+33); p.vcyl(x+16.5,z+16.5,-0.1,0.7,LED_R,'-')
    return p.save()
# ---------------- KONSOOL ----------------
ARD=[b for b in G['boxes'] if b['n'].startswith('Arduino korpus')][0]
USB=[b for b in G['boxes'] if b['n']=='USB-C pesa'][0]; DC=[b for b in G['boxes'] if b['n'].startswith('Toitepesa')][0]
LIDB=[(-155,150),(-75,214),(-12,150),(-12,214),(12,150),(12,214),(155,150),(155,214)]
def console(p):
    p.box(-OX,OX,0,2,OUT,CZ1)
    p.box(-OX,OX,0,CH-3,CZ1-4,CZ1)
    for sx in(-1,1): p.box(sx*(OX-4),sx*OX,0,CH-3,OUT,CZ1)
    p.box(-OX-1,-OX+6,USB['y0']-2,USB['y1']+2.5,USB['z0']-2.5,USB['z1']+2.5,'-')   # USB-C ava
    p.box(-OX-1,-OX+6,DC['y0']-1,DC['y1']+1.5,DC['z0']-1.5,DC['z1']+1.5,'-')       # toitepesa ava
    ring(p,ARD['x0']-0.6,ARD['x1']+0.6,ARD['z0']-0.6,ARD['z1']+0.6,1.6,2,6)     # Arduino korpuse pesa
    p.box(-OX+4,ARD['x0']-0.6,2,6,ARD['z0']-2.2,ARD['z1']+2.2,'-') if False else None
    JX,JZ=POS['JX'],POS['JZ']
    for dx in(-1,1):
        for dz in(-1,1): p.box(JX+dx*18-2,JX+dx*18+2,2,4,JZ+dz*13-2,JZ+dz*13+2)    # jaotusplaadi tugijalad
    for x,z in LIDB: p.vcyl(x,z,0,CH-3,4); p.vcyl(x,z,CH-15,CH-2.9,1.35,'-')       # kaane kruvipuksid (M3)
    for xc in(-150,-20,45,110): p.box(xc-5,xc+5,2,12,OUT,OUT+8); p.zcyl(xc,7,OUT-1,OUT+9,M3,'-')
    for zc in(160,200): p.box(-8,8,2,12,zc-5,zc+5); p.xcyl(7,zc,-9,9,M3,'-')
def lid(p):
    LX,LZ,BXS,BZ=POS['LX'],POS['LZ'],POS['BXS'],POS['BZ']; Y0=CH-3
    p.box(-OX,OX,Y0,CH,OUT,CZ1)
    p.box(-OX+4.3,OX-4.3,TOPY1+0.2,Y0,OUT,OUT+2)                                 # tagaserv (katab konsooli tagakülje)
    for sx in(-1,1): p.box(sx*(OX-4.3),sx*(OX-5.8),Y0-3,Y0,OUT+2,CZ1-4.3)        # asetusserv külgedel
    p.box(-OX+5.8,OX-5.8,Y0-3,Y0,CZ1-5.8,CZ1-4.3)                                # asetusserv ees
    for x,z in LIDB:
        p.vcyl(x,z,Y0-3.1,Y0,4.6,'-')                                            # serv puksi kohalt ära
        p.vcyl(x,z,Y0-0.1,CH+0.1,M3,'-'); p.vcyl(x,z,CH-1.7,CH+0.1,M3,'-',r1=3.2)  # kruviauk + peitpea
    p.box(LX-36.65,LX+36.65,Y0-1,CH+1,LZ-11.85,LZ+11.85,'-')                     # LCD aken
    for dx in(-1,1):
        for dz in(-1,1):
            x,z=LX+dx*37.5,LZ+dz*15.5; p.vcyl(x,z,41,Y0,2.75); p.vcyl(x,z,40.9,Y0-0.6,1.1,'-')
    for x in BXS: p.vcyl(x,BZ,Y0-1,CH+1,6.3,'-')                                 # nupuaugud
    for x in(101,155): p.vcyl(x,BZ,38.7,Y0,3); p.vcyl(x,BZ,38.6,Y0-0.6,1.1,'-')  # nupuplaadi puksid
# ---------------- VÄIKSED OSAD ----------------
def pieces():
    p=Part('kabelaud_nupud_12tk_Ø28')
    for i in range(12):
        x=(i%4)*32; z=(i//4)*32
        p.vcyl(x,z,0,6.4,14); p.vcyl(x,z,6.4,7,14,r1=13.4); p.vcyl(x,z,-0.1,2.2,3.15,'-')
    return p.save()
def crowns():
    p=Part('kabelaud_kroonid_8tk')
    for i in range(8):
        x=(i%4)*36; z=(i//4)*36
        p.vcyl(x,z,0,4,15.5); p.vcyl(x,z,-0.1,2.2,14.3,'-')
        for k in range(6):
            a=2*math.pi*k/6; p.vcyl(x+10*math.cos(a),z+10*math.sin(a),4,6,2)
    return p.save()
def caps():
    p=Part('kabelaud_nupukatted_3tk')
    for i in range(3):
        x=i*20; p.vcyl(x,0,0,5.5,6); p.vcyl(x,0,5.5,7,7.5); p.vcyl(x,0,4.5,7.1,1.95,'-')
    return p.save()
def quarters(name,fn,flip,regions):
    out=[]
    for tag,(x0,x1,z0,z1) in regions.items():
        p=Part(f'{name}_{tag}',flip); fn(p); p.clip(x0,x1,-50,100,z0,z1); out.append(p.save())
    return out
Q={'vasak_taga':(-OX-1,0,-OUT-1,0),'parem_taga':(0,OX+1,-OUT-1,0),'vasak_ees':(-OX-1,0,0,OUT),'parem_ees':(0,OX+1,0,OUT)}
H={'vasak':(-OX-1,0,OUT,CZ1+1),'parem':(0,OX+1,OUT,CZ1+1)}
files=[]
files+=quarters('kabelaud_alus',board_base,None,Q)
files+=quarters('kabelaud_pealmine_plaat',top_plate,TOPY1,{k:(v[0],v[1],v[2],v[3] if v[3]!=0 else 0) for k,v in Q.items()})
files+=quarters('kabelaud_konsool',console,None,H)
files+=quarters('kabelaud_kaas',lid,CH,H)
files+=[pieces(),crowns(),caps(),tiles()]
print('\n'.join(files))
