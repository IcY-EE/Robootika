"""1:1 koostejoonis A4 lehtedele (vaade ülevalt). Loeb geom.json-i, kirjutab joonis.html-i,
mille Chromium prindib PDF-iks:  python3 joonis.py && python3 joonis.py pdf ../../hardware/koostejoonis-1-1-A4.pdf"""
import json, sys, math
G = json.load(open('geom.json')); D = G['dims']
HB, SQ, OX, OUT, CZ0, CZ1 = D['HB'], D['SQ'], D['OX'], D['OUT'], D['CZ0'], D['CZ1']
WC = {'sig': '#1D9E75', 'gnd': '#2C2C2A', 'v5': '#E24B4A', 'sda': '#378ADD', 'scl': '#EF9F27', 'led': '#7F77DD', 'sig2': '#639922'}
WN = {'sig': 'Reed-lüliti → MCP', 'gnd': 'GND', 'v5': '5 V', 'sda': 'SDA', 'scl': 'SCL', 'led': 'LED andmed', 'sig2': 'Nupud → D2–D4'}
f2 = lambda v: f'{v:.2f}'

def drawing():
    s = []
    a = s.append
    # laua ja konsooli kontuurid
    a(f'<rect x="{-OX}" y="{-OUT}" width="{2*OX}" height="{2*OUT}" fill="#fff" stroke="#444" stroke-width="0.6"/>')
    a(f'<rect x="{-OX}" y="{CZ0}" width="{2*OX}" height="{CZ1-CZ0}" fill="#fff" stroke="#444" stroke-width="0.6"/>')
    for sx in (-1, 1):
        x0 = HB if sx > 0 else -OX + 5
        a(f'<rect x="{x0 if sx>0 else x0}" y="{-HB}" width="{OX-5-HB}" height="{2*HB}" fill="#F4F3EF" stroke="none"/>')
        a(f'<text x="{sx*(HB+17)}" y="{-HB+6}" class="t3" text-anchor="middle">pöördetasku</text>')
    # ruudud
    for q in G['squares']:
        a(f'<rect x="{f2(q["x"]-SQ/2)}" y="{f2(q["z"]-SQ/2)}" width="{SQ}" height="{SQ}" fill="{"#EBDCC6" if q["d"] else "#FFFFFF"}" stroke="#C9C7BE" stroke-width="0.25"/>')
        a(f'<text x="{f2(q["x"]-SQ/2+1.5)}" y="{f2(q["z"]-SQ/2+4)}" class="t2">{q["n"]}</text>')
    # nupu jälg (Ø 28) tumedatel ruutudel – näitab, et LED-ava jääb välja
    for q in G['squares']:
        if q['d']:
            a(f'<circle cx="{f2(q["x"])}" cy="{f2(q["z"])}" r="14" fill="none" stroke="#B4B2A9" stroke-width="0.3" stroke-dasharray="1.5 1"/>')
    # elektroonika kastid
    for b in G['boxes']:
        c = b['c']
        if c in ('base', 'top', 'cbase', 'lid', 'ardd', 'distb', 'lcd', 'btnpcb'):
            continue
        fill = {'mcp': '#DCE9F7', 'post': '#888780', 'ard': '#EEF4FB', 'dist': '#E5F0D6', 'res': '#F0997B'}.get(c, 'none')
        a(f'<rect x="{f2(b["x0"])}" y="{f2(b["z0"])}" width="{f2(b["x1"]-b["x0"])}" height="{f2(b["z1"]-b["z0"])}" fill="{fill}" stroke="#5F5E5A" stroke-width="0.3"/>')
        if c in ('mcp', 'dist'):
            a(f'<text x="{f2((b["x0"]+b["x1"])/2)}" y="{f2((b["z0"]+b["z1"])/2)}" class="t2" text-anchor="middle">{b["n"].split(" (")[0] if c=="dist" else b["n"]}</text>')
    # kaane all (LCD, nupuplaat) katkendjoonega
    for b in G['boxes']:
        if b['c'] in ('lcd', 'btnpcb') and 'raam' not in b['n']:
            a(f'<rect x="{f2(b["x0"])}" y="{f2(b["z0"])}" width="{f2(b["x1"]-b["x0"])}" height="{f2(b["z1"]-b["z0"])}" fill="none" stroke="#3B6D11" stroke-width="0.35" stroke-dasharray="2 1"/>')
            a(f'<text x="{f2((b["x0"]+b["x1"])/2)}" y="{f2(b["z0"]-1)}" class="t2" text-anchor="middle">{b["n"]} (kaane all)</text>')
    for bt in G['buttons']:
        a(f'<circle cx="{bt["x"]}" cy="{bt["z"]}" r="6" fill="none" stroke="#3B6D11" stroke-width="0.35"/><text x="{bt["x"]}" y="{bt["z"]+1}" class="t2" text-anchor="middle">{bt["t"]}</text>')
    # Arduino
    a('<polygon points="' + ' '.join(f'{f2(x)},{f2(z)}' for x, z in G['ard']['outline']) + '" fill="#D6E6F5" stroke="#185FA5" stroke-width="0.4"/>')
    for x, z in G['ard']['holes']:
        a(f'<circle cx="{f2(x)}" cy="{f2(z)}" r="1.6" fill="#fff" stroke="#185FA5" stroke-width="0.3"/>')
    ax, az = G['pos']['AX'], G['pos']['AZ']
    a(f'<text x="{ax}" y="{az}" class="t1" text-anchor="middle">Arduino UNO R4 WiFi</text>')
    # LED-riba
    pts = ' '.join(f'{f2(p[0])},{f2(p[2])}' for p in G['strip_path'])
    a(f'<polyline points="{pts}" fill="none" stroke="#7F77DD" stroke-opacity="0.18" stroke-width="10" stroke-linejoin="round"/>')
    a(f'<polyline points="{pts}" fill="none" stroke="#7F77DD" stroke-width="0.3" stroke-dasharray="3 2"/>')
    for l in G['leds']:
        a(f'<rect x="{f2(l["x"]-2.5)}" y="{f2(l["z"]-2.5)}" width="5" height="5" fill="{"#FAC775" if l["sq"] else "#fff"}" stroke="#7F77DD" stroke-width="0.25"/>')
    for h in G['ledholes']:
        a(f'<circle cx="{f2(h["x"])}" cy="{f2(h["z"])}" r="2" fill="none" stroke="#C0392B" stroke-width="0.4"/>')
        a(f'<text x="{f2(h["x"])}" y="{f2(h["z"]+5.6)}" class="t2" text-anchor="middle" fill="#7F77DD">LED {h["i"]}</text>')
    # juhtmed
    for w in G['wires']:
        p = ' '.join(f'{f2(q[0])},{f2(q[2])}' for q in w['p'])
        a(f'<polyline points="{p}" fill="none" stroke="{WC[w["k"]]}" stroke-width="0.35" stroke-linejoin="round"/>')
    # reed-lülitid
    for r in G['reeds']:
        a(f'<rect x="{f2(r["x0"])}" y="{f2(r["z"]-1)}" width="10.5" height="2" rx="1" fill="#B5D4F4" stroke="#185FA5" stroke-width="0.3"/>')
    return '\n'.join(s)

# lehtedeks jagamine
X0, X1, Z0, Z1 = -176, 176, -152, 230
TW, TH = (X1 - X0) / 2, (Z1 - Z0) / 2
TILES = [('ülemine vasak', X0, Z0), ('ülemine parem', X0 + TW, Z0), ('alumine vasak', X0, Z0 + TH), ('alumine parem', X0 + TW, Z0 + TH)]

def crosses(x0, z0):
    s = []
    for gx in range(-150, 151, 50):
        for gz in range(-150, 231, 50):
            if x0 - 1 <= gx <= x0 + TW + 1 and z0 - 1 <= gz <= z0 + TH + 1:
                s.append(f'<path d="M{gx-5},{gz}H{gx+5}M{gx},{gz-5}V{gz+5}" stroke="#E24B4A" stroke-width="0.3"/><circle cx="{gx}" cy="{gz}" r="1.2" fill="none" stroke="#E24B4A" stroke-width="0.3"/><text x="{gx+1.5}" y="{gz-1.5}" class="t3" fill="#E24B4A">{gx},{gz}</text>')
    return '\n'.join(s)

CSS = """@page{size:A4;margin:0}body{margin:0;font-family:Inter,Arial,sans-serif;color:#2C2C2A}
.pg{width:210mm;height:297mm;box-sizing:border-box;padding:10mm;page-break-after:always;position:relative;overflow:hidden}
.t1{font-size:3.2px;font-weight:600}.t2{font-size:2.2px}.t3{font-size:1.8px;fill:#888780}
h1{font-size:20pt;margin:0 0 4mm}h2{font-size:12pt;margin:6mm 0 2mm}p,li,td{font-size:9pt;line-height:1.4}
table{border-collapse:collapse;width:100%}td{border-bottom:0.2mm solid #ddd;padding:1mm 2mm;vertical-align:top}td:first-child{width:38mm;color:#5F5E5A}
.lg{display:grid;grid-template-columns:repeat(3,1fr);gap:1mm 4mm;font-size:8.5pt}.lg i{display:inline-block;width:8mm;height:1mm;margin-right:2mm;vertical-align:middle}
.hd{font-size:8pt;color:#5F5E5A;margin-bottom:2mm}"""

def html():
    dr = drawing()
    led = D
    pages = []
    lgd = ''.join(f'<div><i style="background:{c}"></i>{WN[k]}</div>' for k, c in WC.items())
    lgd += '<div><i style="background:#7F77DD;opacity:.3;height:3mm"></i>LED-riba 10 mm</div><div><i style="background:#FAC775;height:3mm;width:3mm"></i>LED tumeda ruudu all</div><div><i style="border:0.4mm solid #C0392B;border-radius:50%;width:3mm;height:3mm;background:none"></i>LED-ava Ø 4 mm</div>'
    pages.append(f'''<div class="pg"><h1>AI-kabelaud – 1:1 koostejoonis</h1>
<p>Vaade <b>ülevalt läbi laua</b>: kõik osad ja juhtmed on joonistatud täpselt sinna, kuhu need laua sisse jäävad. Ehitamisel on laud tagurpidi, siis on pilt peegelpildis.</p>
<h2>Printimine</h2><ol><li>Prindi lehed 2–5 <b>A4 püstpaigutuses, mõõtkava 100 %</b> („tegelik suurus“, mitte „sobita lehele“).</li>
<li>Kontrolli joonlauaga allolevat 100 mm joont. Kui see pole täpselt 100 mm, on mõõtkava vale.</li>
<li>Lõika lehed servast ja kleebi kokku nii, et punased ristid (iga 50 mm järel, koordinaatidega) jääksid kohakuti.</li></ol>
<svg width="100mm" height="6mm" viewBox="0 0 100 6"><path d="M0,1V5M0,3H100M100,1V5" stroke="#2C2C2A" stroke-width="0.4"/></svg><div style="font-size:8pt">100 mm</div>
<h2>Mõõdud</h2><table>
<tr><td>Laud</td><td>{2*OX:.0f} × {2*OUT:.0f} × {D["BH"]:.0f} mm, mänguväli {2*HB:.0f} mm, ruut {SQ} mm, külgedel {D["POCK"]:.0f} mm pöördetaskud</td></tr>
<tr><td>Konsool</td><td>{2*OX:.0f} × {CZ1-CZ0:.0f} × {D["CH"]:.0f} mm, laua ja konsooli vahel seina pole</td></tr>
<tr><td>Kihid laua sees (alt üles)</td><td>põhi 0–2 · MCP 4–6 · juhtmed ~27 · LED-riba 29–31 · reed-lülitid 31–33 · pealmine plaat 33–34 mm</td></tr>
<tr><td>Reed-lüliti</td><td>Ø 2 × 10,5 mm, klaasi üks ots ruudu keskel (nupu magneti all)</td></tr>
<tr><td>LED-riba</td><td>üks tükk, {G["nled"]} LED-i, ~{G["strip_len"]/1000:.2f} m, aasad pöördetaskutes (ei lõigata). Riba jookseb rea keskjoonest {led["LED_DZ"]} mm mängija pool.</td></tr>
<tr><td>LED-ava</td><td>Ø 4 mm tumeda ruudu <b>nurgas</b>: keskest {led["LED_DX"]} mm riba suunas ja {led["LED_DZ"]} mm mängija poole (~{math.hypot(led["LED_DX"],led["LED_DZ"]):.0f} mm keskest). Nupp Ø 28 (hall katkendring) ega kroon Ø 31 ei kata ava.</td></tr>
<tr><td>LED-i number</td><td>21 × rida + 4 × k (k = tumeda ruudu järjekord reas riba suunas); a1 = 0, h2 = 21, c3 = 46, b8 = 159</td></tr>
<tr><td>MCP23017</td><td>21 × 26,5 mm, #1 ridade 2–3 all, #2 ridade 6–7 all, vasakul serval</td></tr>
<tr><td>Kaane all</td><td>LCD 80 × 35 (raam 72,3 × 23), 3 nuppu Ø 12</td></tr></table>
<h2>Juhtmete värvid</h2><div class="lg">{lgd}</div>
<p style="font-size:8pt;color:#5F5E5A">Juhtmed on soovituslikud: reed-lülitite signaalid kogunevad vasakusse serva ja lähevad MCP-ni, GND jookseb igas reas eraldi juhtmena.</p>
<svg style="width:62mm;height:{62*(Z1-Z0)/(X1-X0):.1f}mm" viewBox="{X0} {Z0} {X1-X0} {Z1-Z0}">{dr}
<path d="M{X0+TW},{Z0}V{Z1}M{X0},{Z0+TH}H{X1}" stroke="#E24B4A" stroke-width="1" stroke-dasharray="4 3"/></svg>
<div style="font-size:8pt;color:#5F5E5A">Ülevaade (vähendatud): punased jooned näitavad, kuidas laud lehtedeks jaguneb.</div></div>''')
    for i, (nm, x0, z0) in enumerate(TILES):
        pages.append(f'''<div class="pg"><div class="hd">Leht {i+2}/5 · {nm} · mõõtkava 1:1 · vaade ülevalt</div>
<svg style="width:{TW}mm;height:{TH}mm;border:0.2mm solid #999" viewBox="{x0} {z0} {TW} {TH}">{dr}{crosses(x0, z0)}</svg></div>''')
    return f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{"".join(pages)}</body></html>'

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'pdf':
        import os
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); pg = b.new_page()
            pg.goto('file://' + os.path.abspath('joonis.html')); pg.pdf(path=sys.argv[2], format='A4', print_background=True, prefer_css_page_size=True)
            b.close()
    else:
        open('joonis.html', 'w').write(html()); print('joonis.html')
