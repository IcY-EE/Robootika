"""AI-kabelaua koostegeomeetria (mm). x: a->h paremale, z: rida 8 -> rida 1 -> konsool (kasvab mängija poole), y: üles.
Üks allikas nii 3D-mudelile kui 1:1 joonisele."""
import json
SQ=33.5; HB=134.0; OUT=144.0; BH=34.0
POCK=30.0; OX=HB+POCK+5.0   # pöördetasku laius ja laua poollaius x-suunas
CZ0,CZ1=144.0,224.0; CH=48.0           # konsool
FILES='abcdefgh'
fx=lambda f:-HB+SQ*(f+0.5)
rz=lambda r: HB-SQ*(r+0.5)
P=2.54; LEDP=1000/60   # LED-ide samm ribal
# LED ei ole ruudu keskel (jääks nupu alla), vaid ruudu nurgas: riba jookseb rea keskjoonest LED_DZ võrra
# mängija pool, LED on ruudu keskest LED_DX võrra riba liikumise suunas (paaritud read +x, paaris read -x).
# Kaugus keskest ~17 mm > nupu raadius 14 mm (ja kroon 15,5 mm), nii et LED-ava jääb nupust välja.
LED_DX=13.5; LED_DZ=10.5
Y_TOP=33.0; Y_REED=32.0; Y_LEDB=29.0; Y_WIRE=27.0; Y_MCP=4.0
def led_index(f,r): return 13*r+(4*(f//2) if r%2==0 else 4*((7-f)//2))
def sensor(f,r): return r*4+f//2
G={'boxes':[],'reeds':[],'strips':[],'leds':[],'wires':[],'labels':[],'squares':[],'pins':[]}
def box(name,cat,x0,x1,y0,y1,z0,z1,color,**kw): G['boxes'].append(dict(n=name,c=cat,x0=x0,x1=x1,y0=y0,y1=y1,z0=z0,z1=z1,col=color,**kw))
def wire(kind,pts,label=''): G['wires'].append(dict(k=kind,p=[[round(a,2) for a in q] for q in pts],l=label))
# --- laud
box('Laua põhi','base',-OX,OX,0,2,-OUT,OUT,'#5F5E5A')
box('Raam (tagasein)','base',-OX,OX,0,BH,-OUT,-HB,'#444441')
# Laua ja konsooli vahel seina pole: pealmise plaadi esiserv toetub tugipostidele
for px in (-45.0,15.0,75.0,135.0): box('Tugipost 8 × 8 mm (pealmise plaadi esiserv)','post',px-4,px+4,0,Y_TOP,HB+1,HB+9,'#444441')
box('Tugipost 8 × 8 mm (pealmise plaadi esiserv)','post',-109,-101,0,Y_TOP,HB+1,HB+9,'#444441')
for x0,x1 in((-OX,-OX+5),(OX-5,OX)): box('Raam (külgsein)','base',x0,x1,0,BH,-OUT,OUT,'#444441')
for x0,x1 in((-HB-1.5,-HB),(HB,HB+1.5)): box('Taskuvahesein (avadega ribale)','base',x0,x1,0,Y_LEDB-3,-HB,HB,'#5F5E5A')
box('Pealmine plaat 1 mm','top',-OX,OX,Y_TOP,BH,-OUT,OUT,'#444441')
for r in range(8):
    for f in range(8):
        G['squares'].append(dict(f=f,r=r,x=fx(f),z=rz(r),d=(f+r)%2==0,n=FILES[f]+str(r+1)))
# --- reed-lülitid (klaas ruudu keskelt +x suunas)
for r in range(8):
    for f in range(r%2,8,2):
        G['reeds'].append(dict(x0=fx(f),x1=fx(f)+10.5,z=rz(r),y=Y_REED,i=sensor(f,r),n=FILES[f]+str(r+1)))
# --- LED-riba: ÜKS pidev tükk, rea lõpus pehme aas pöördetaskus (ei lõigata)
import math
N_RIGHT,N_LEFT=9,9   # LED-sammud rea viimasest tumedast LED-ist järgmise rea esimese tumeda LED-ini
H_LOOP=18.0            # kui sügavale aas tasku põhja poole vajub
def loop_pts(side,z0,z1,a,n=40):
    return [(side*(HB+a*math.sin(t)),Y_LEDB-H_LOOP*math.sin(t),z0+(z1-z0)*(1-math.cos(t))/2) for t in [math.pi*i/n for i in range(n+1)]]
def plen(pts): return sum(math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1))
path=[]; s_led0=None; loops=[]
x_start=fx(0)+LED_DX-LEDP/2
lz=lambda r: rz(r)+LED_DZ
path.append((x_start,Y_LEDB,lz(0)))
cur_s=0.0
led_first={}   # rea esimese tumeda ruudu LED-i kaarepikkus
led_first[0]=LEDP/2
for r in range(8):
    z=lz(r); d=1 if r%2==0 else -1
    first_s=led_first[r]
    if r==7:
        end=fx(1)-LED_DX-LEDP/2  # viimane rida lõpeb b8 LED-i taga
        path.append((end,Y_LEDB,z)); break
    side=d; edge=side*HB
    path.append((edge,Y_LEDB,z))
    s_edge=plen(path)
    N=N_RIGHT if side>0 else N_LEFT
    target=first_s+(12+N)*LEDP            # järgmise rea esimese tumeda LED-i kaarepikkus
    xn=fx(7)-LED_DX if side>0 else fx(0)+LED_DX   # järgmise rea esimese tumeda ruudu LED (h või a)
    need=target-s_edge-abs(edge-xn)        # aasa pikkus
    lo,hi=1.0,80.0
    for _ in range(60):
        m=(lo+hi)/2
        if plen(loop_pts(side,z,lz(r+1),m))<need: lo=m
        else: hi=m
    lp=loop_pts(side,z,lz(r+1),(lo+hi)/2); loops.append(dict(side=side,a=(lo+hi)/2,len=need,r=r))
    path+=lp[1:]
    led_first[r+1]=target
G['strip_path']=[[round(v,2) for v in q] for q in path]
G['loops']=loops
# LED-id kaarepikkuse järgi
cum=[0.0]
for i in range(len(path)-1): cum.append(cum[-1]+math.dist(path[i],path[i+1]))
def at(sv):
    for i in range(len(cum)-1):
        if cum[i]<=sv<=cum[i+1]:
            t=(sv-cum[i])/(cum[i+1]-cum[i]) if cum[i+1]>cum[i] else 0
            return [path[i][j]+(path[i+1][j]-path[i][j])*t for j in range(3)]
    return list(path[-1])
dark_s={}
for r in range(8):
    fs=list(range(r%2,8,2)); fs=fs if r%2==0 else fs[::-1]
    for k,f in enumerate(fs): dark_s[(f,r)]=led_first[r]+4*k*LEDP
nled=int((cum[-1]-LEDP/2)/LEDP)+1
inv={round(v/LEDP-0.5):fr for fr,v in dark_s.items()}
LEDMAP={}
for i in range(nled):
    sv=LEDP/2+i*LEDP; p=at(sv); fr=inv.get(i)
    if fr: LEDMAP[FILES[fr[0]]+str(fr[1]+1)]=i
    G['leds'].append(dict(x=round(p[0],2),y=round(p[1],2),z=round(p[2],2),i=i,sq=bool(fr),loop=abs(p[0])>HB+0.5))
G['ledholes']=[dict(n=FILES[f]+str(r+1),x=round(fx(f)+(LED_DX if r%2==0 else -LED_DX),2),z=round(rz(r)+LED_DZ,2),i=LEDMAP[FILES[f]+str(r+1)]) for (f,r) in dark_s]
G['ledmap']=LEDMAP; G['nled']=nled; G['strip_len']=round(cum[-1])
def led_index(f,r): return LEDMAP[FILES[f]+str(r+1)]
# --- MCP23017 moodulid (21 x 26.5), päis 2 veergu vasakul (GP), 1 veerg paremal (toide/I2C)
MCP=[dict(n='MCP23017 #1 (0x20)',x=-100.0,z=67.0,rows=range(0,4)),dict(n='MCP23017 #2 (0x21)',x=-100.0,z=-67.0,rows=range(4,8))]
for m in MCP:
    box(m['n'],'mcp',m['x']-10.5,m['x']+10.5,Y_MCP,Y_MCP+1.6,m['z']-13.25,m['z']+13.25,'#185FA5')
    m['gp']=[(m['x']-8.9+(0 if k<8 else P), m['z']-11.43+(k%8)*P*1.25) for k in range(16)]
    m['pw']={nm:(m['x']+8.9,m['z']-8.9+j*P) for j,nm in enumerate(['VCC','GND','SDA','SCL','RST','A0','A1','A2'])}
    for x,z in m['gp']: G['pins'].append(dict(x=x,z=z,y=Y_MCP+1.6))
    for x,z in m['pw'].values(): G['pins'].append(dict(x=x,z=z,y=Y_MCP+1.6))
# --- reed juhtmed
YP=Y_MCP+1.6
for mi,m in enumerate(MCP):
    w=0
    for r in m['rows']:
        z=rz(r)
        for k,f in enumerate(range(r%2,8,2)):
            cx=fx(f); i=sensor(f,r); gx,gz=m['gp'][i%16]
            zs=z-7.5-k*1.4; tx=-131.5+w*0.85
            wire('sig',[(cx+10.5,Y_REED,z),(cx+12.5,Y_REED,z),(cx+12.5,Y_REED,z-6.5),(cx+12.5,Y_WIRE,z-6.5),(cx+12.5,Y_WIRE,zs),(tx,Y_WIRE,zs),(tx,Y_WIRE-1-0.3*(w%4),gz),(gx,Y_WIRE-1-0.3*(w%4),gz),(gx,YP,gz)],f'{FILES[f]}{r+1} → MCP {"#1" if mi==0 else "#2"} {"GPA" if i%16<8 else "GPB"}{i%8}')
            w+=1
# --- GND siin: igas reas üks juhe, vasakul ühine püstjuhe
GX=-133.0
for r in range(8):
    z=rz(r); fs=list(range(r%2,8,2))
    for f in fs:
        cx=fx(f); wire('gnd',[(cx,Y_REED,z),(cx-2,Y_REED,z),(cx-2,Y_REED,z+3.5),(cx-2,Y_WIRE+0.6,z+3.5),(cx-2,Y_WIRE+0.6,z+9)],'')   # alla enne LED-riba (riba z+5,5…+15,5)
    wire('gnd',[(fx(fs[-1])-2,Y_WIRE+0.6,z+9),(GX,Y_WIRE+0.6,z+9)],f'GND rida {r+1}')
wire('gnd',[(GX,Y_WIRE+0.6,rz(7)+9),(GX,Y_WIRE+0.6,HB-2),(GX,6,HB-2),(GX,6,CZ0+6)],'Reed-lülitite ühine GND')
# --- konsool
box('Konsooli põhi','cbase',-OX,OX,0,2,CZ0,CZ1,'#5F5E5A')
box('Konsooli sein','cbase',-OX,OX,0,CH-3,CZ1-4,CZ1,'#444441')
box('Konsooli sein','cbase',-OX,-OX+4,0,CH-3,CZ0,CZ1,'#444441'); box('Konsooli sein','cbase',OX-4,OX,0,CH-3,CZ0,CZ1,'#444441')
box('Kaas','lid',-OX,OX,CH-3,CH,CZ0,CZ1,'#5F5E5A',hole=[[20-36.5,20+36.5,184-11.85,184+11.85]])
AX,AZ=-117.0,184.0
box('Arduino korpus 81 × 58 × 18','ard',AX+34.3-81,AX+34.3,2,5,AZ-29,AZ+29,'#E6F1FB',op=0.5)
# --- Arduino UNO R4 WiFi päris mõõtudes (UNO standardkoordinaadid u,v mm; u=0 USB-poolne serv, v=0 toitepäise serv)
YB=5.0; T_PCB=1.6; YT=YB+T_PCB
U0=AX-34.29
def W(u,v): return (U0+u, AZ+26.67-v)
G['ard']=dict(y=YB,t=T_PCB,outline=[list(W(u,v)) for u,v in [(0,0),(66.04,0),(68.58,2.54),(68.58,40.64),(66.04,43.18),(66.04,50.8),(63.5,53.34),(0,53.34)]],
  holes=[list(W(u,v)) for u,v in [(13.97,2.54),(15.24,50.8),(66.04,7.62),(66.04,35.56)]])
def part(name,u0,u1,v0,v1,y0,y1,col,cat='ardd'):
    (x0,z0),(x1,z1)=W(u0,v0),W(u1,v1); box(name,cat,min(x0,x1),max(x0,x1),y0,y1,min(z0,z1),max(z0,z1),col)
dig={}; dn=['D0','D1','D2','D3','D4','D5','D6','D7']
for j,nm in enumerate(dn): dig[nm]=W(63.5-j*2.54,50.8)
for j,nm in enumerate(['D8','D9','D10','D11','D12','D13','GND2','AREF','SDA','SCL']): dig[nm]=W(41.66-j*2.54,50.8)
pwr={}
for j,nm in enumerate(['NC','IOREF','RESET','3V3','5V','GND','GND3','VIN']): pwr[nm]=W(27.94+j*2.54,2.54)
for j,nm in enumerate(['A0','A1','A2','A3','A4','A5']): pwr[nm]=W(50.8+j*2.54,2.54)
YH=YT+8.5
part('Digitaalpäis D0–D7','ardh',44.45,64.77,49.53,52.07,YT,YH,'#2C2C2A') if False else None
part('Digitaalpäis D0–D7',44.45,64.77,49.53,52.07,YT,YH,'#1E1E1C')
part('Digitaalpäis D8–SCL',17.53,42.93,49.53,52.07,YT,YH,'#1E1E1C')
part('Toitepäis',26.67,46.99,1.27,3.81,YT,YH,'#1E1E1C')
part('Analoogpäis A0–A5',49.53,64.77,1.27,3.81,YT,YH,'#1E1E1C')
part('ICSP päis 2×3',62.99,68.07,22.86,30.48,YT,YT+8.5,'#1E1E1C')
part('USB-C pesa',-1.5,6.5,33.0,42.0,YT,YT+3.2,'#B4B2A9')
part('Toitepesa (DC 5,5 mm)',-1.8,12.4,3.3,12.3,YT,YT+11,'#1E1E1C')
part('ESP32-S3-MINI-1 WiFi moodul',14.5,30.0,4.5,20.0,YT,YT+2.4,'#C8C6BE')
part('ESP32 antenn',8.5,14.5,4.5,20.0,YT,YT+0.8,'#1E1E1C')
part('Renesas RA4M1 protsessor (QFP-64)',30.0,40.0,36.0,46.0,YT,YT+1.3,'#2C2C2A')
part('Reset nupp',3.0,9.0,44.0,50.0,YT,YT+2.5,'#D3D1C7')
part('Qwiic I2C pistik',61.5,67.5,13.0,17.5,YT,YT+3,'#F1EFE8')
part('Pingeregulaator',22.0,26.0,22.0,27.0,YT,YT+1.8,'#444441')
part('Kondensaatorid',17.0,21.0,24.0,30.0,YT,YT+1.5,'#5F5E5A')
G['ard_matrix']=[list(W(41.0+i*1.85,16.0+j*2.1)) for i in range(12) for j in range(8)]
G['ard_labels']=dict(logo=list(W(25,34)),y=YT)
for d in (dig,pwr):
    for x,z in d.values(): G['pins'].append(dict(x=x,z=z,y=YH))
# jaotusplaat (5V, GND, SDA, SCL siinid + 330 Ω + 1000 µF)
JX,JZ=-30.0,190.0
box('Jaotusplaat 40 × 30','dist',JX-20,JX+20,4,5.6,JZ-15,JZ+15,'#C0DD97')
J={'5V':(JX-15,JZ-10),'GND':(JX-15,JZ-3.5),'SDA':(JX-15,JZ+3),'SCL':(JX-15,JZ+9.5)}
for nm,(x,z) in J.items(): box(f'Siin {nm}','distb',x,x+30,5.6,6.4,z-0.8,z+0.8,'#B4B2A9')
box('Takisti 330 Ω','res',JX+4,JX+12,5.6,8,JZ+12,JZ+14,'#F0997B')
G['cap']=dict(x=JX+15,z=JZ-6,y=5.6,r=5,h=16)
YJ=6.4
def jp(nm,dx): x,z=J[nm]; return (x+dx,z)
# Arduino -> jaotusplaat
for nm,src in (('5V',pwr['5V']),('GND',pwr['GND']),('SDA',dig['SDA']),('SCL',dig['SCL'])):
    x,z=src; tx,tz=jp(nm,2)
    wire({'5V':'v5','GND':'gnd','SDA':'sda','SCL':'scl'}[nm],[(x,YH,z),(x,YH+4,z),(x,YH+4,z+(6 if z<AZ else -6)),(tx,YH+4,z+(6 if z<AZ else -6)),(tx,YH+4,tz),(tx,YJ,tz)],f'Arduino {nm} → jaotusplaat')
# MCP -> jaotusplaat (4 juhet) + MCP sillad
kinds={'VCC':'v5','GND':'gnd','SDA':'sda','SCL':'scl'}; jn={'VCC':'5V','GND':'GND','SDA':'SDA','SCL':'SCL'}
for mi,m in enumerate(MCP):
    for j,pn in enumerate(['VCC','GND','SDA','SCL']):
        x,z=m['pw'][pn]; lx=m['x']+12+j*1.2+mi*5.5; tx,tz=jp(jn[pn],5+mi*8+j*1.2)
        wire(kinds[pn],[(x,YP,z),(x,YP+2,z),(lx,YP+2,z),(lx,YP+2,HB-4),(lx,6,HB-4),(lx,6,CZ0+20+mi*3+j),(tx,6,CZ0+20+mi*3+j),(tx,6,tz),(tx,YJ,tz)],f'MCP {"#1" if mi==0 else "#2"} {pn} → jaotusplaat {jn[pn]}')
    vx,vz=m['pw']['VCC']; rx,rzz=m['pw']['RST']
    wire('v5',[(vx,YP,vz),(vx+1.6,YP+1,vz),(rx+1.6,YP+1,rzz),(rx,YP,rzz)],'RST → VCC')
    gx,gz=m['pw']['GND']
    for a in ('A0','A1','A2'):
        ax_,az_=m['pw'][a]; tgt=(vx,vz) if (mi==1 and a=='A0') else (gx,gz)
        wire('v5' if tgt==(vx,vz) else 'gnd',[(ax_,YP,az_),(ax_+3,YP+0.6,az_),(ax_+3,YP+0.6,tgt[1]),(tgt[0],YP,tgt[1])],f'{a} → {"VCC" if tgt==(vx,vz) else "GND"}')
# reed GND -> jaotusplaat
tx,tz=jp('GND',22); wire('gnd',[(GX,6,CZ0+6),(GX,6,CZ0+14),(tx,6,CZ0+14),(tx,6,tz),(tx,YJ,tz)],'Reed GND → jaotusplaat')
# LED: D6 -> 330 Ω -> riba DIN (rida 1 algus), 5V/GND jaotusplaadilt
d6x,d6z=dig['D6']; s0=dict(x0=G['strip_path'][0][0],z=G['strip_path'][0][2])
wire('led',[(d6x,YH,d6z),(d6x,YH+6,d6z),(d6x,YH+6,JZ+13),(JX+4,YH+6,JZ+13),(JX+4,8,JZ+13)],'D6 → 330 Ω')
wire('led',[(JX+12,8,JZ+13),(JX+12,YH+8,JZ+13),(JX+12,YH+8,CZ0+3),(s0['x0']-4,YH+8,CZ0+3),(s0['x0']-4,Y_LEDB,CZ0+3),(s0['x0']-4,Y_LEDB,s0['z']),(s0['x0'],Y_LEDB,s0['z'])],'330 Ω → LED DIN (a1)')
for nm,kind,dz in (('5V','v5',-3),('GND','gnd',3)):
    tx,tz=jp(nm,28)
    wire(kind,[(tx,YJ,tz),(tx,YH+10+dz*0.3,tz),(tx,YH+10+dz*0.3,CZ0+5+dz),(s0['x0']-7+dz*0.5,YH+10,CZ0+5+dz),(s0['x0']-7+dz*0.5,Y_LEDB,CZ0+5+dz),(s0['x0']-7+dz*0.5,Y_LEDB,s0['z']+dz),(s0['x0'],Y_LEDB,s0['z']+dz)],f'{nm} → LED-riba')
# LCD + nupud kaane all
LX,LZ=50.0,184.0; LY=CH-3
box('LCD plaat 80 × 35','lcd',LX-40,LX+40,LY-9,LY-7.4,LZ-17.5,LZ+17.5,'#3B6D11',lid=1)
box('LCD raam 72,3 × 23','lcd',LX-36.15,LX+36.15,LY-7.4,LY+0.6,LZ-11.5,LZ+11.5,'#2C2C2A',lid=1)
box('I2C moodul','lcd',LX-22,LX+20,LY-21,LY-9,LZ-10,LZ+10,'#2C2C2A',lid=1)
G['lcdscreen']=dict(x=LX,z=LZ,y=LY+0.62,w=64.5,h=14.5)
lp={nm:(LX+40+2,LZ-3.8+j*P) for j,nm in enumerate(['GND','VCC','SDA','SCL'])}
for nm,(x,z) in lp.items():
    tx,tz=jp({'VCC':'5V'}.get(nm,nm),12+(['GND','VCC','SDA','SCL'].index(nm))*1.2)
    wire({'GND':'gnd','VCC':'v5','SDA':'sda','SCL':'scl'}[nm],[(x,LY-14,z),(x+3,LY-14,z),(x+3,LY-20,z),(x+3,22,z),(x+3,22,tz+20),(tx,22,tz+20),(tx,22,tz),(tx,YJ,tz)],f'LCD {nm} → jaotusplaat')
BZ=184.0; BXS=[110.0,128.0,146.0]
box('Nupuplaat 60 × 20','btnpcb',98,158,LY-10,LY-8.4,BZ-10,BZ+10,'#C0DD97',lid=1)
G['buttons']=[dict(x=x,z=BZ,y=LY,t=t) for x,t in zip(BXS,['UUS','?','AI'])]
for x,pin in zip(BXS,['D2','D3','D4']):
    px,pz=dig[pin]
    wire('sig2',[(x+3,LY-10,BZ+3),(x+3,LY-14,BZ+3),(x+3,LY-14,BZ+8),(x+3,26,BZ+8),(x+3,26,CZ0+9-BXS.index(x)*1.5),(px,26,CZ0+9-BXS.index(x)*1.5),(px,26,pz),(px,YH,pz)],f'Nupp → {pin}')
tx,tz=jp('GND',16)
wire('gnd',[(BXS[0]-3,LY-10,BZ-3),(BXS[-1]-3,LY-10,BZ-3)],'nuppude GND')
wire('gnd',[(BXS[0]-3,LY-10,BZ-3),(BXS[0]-3,30,BZ-3),(tx,30,BZ-3),(tx,30,tz),(tx,YJ,tz)],'Nupud GND → jaotusplaat')
G['mcp']=[dict(n=m['n'],x=m['x'],z=m['z']) for m in MCP]
G['pos']=dict(LX=LX,LZ=LZ,BXS=BXS,BZ=BZ,AX=AX,AZ=AZ,JX=JX,JZ=JZ,MCP=[(m['x'],m['z']) for m in MCP])
G['dims']=dict(LED_DX=LED_DX,LED_DZ=LED_DZ,OX=OX,POCK=POCK,SQ=SQ,HB=HB,OUT=OUT,BH=BH,CZ0=CZ0,CZ1=CZ1,CH=CH)
json.dump(G,open('geom.json','w'))
print(len(G['wires']),'juhet',len(G['boxes']),'kasti')
