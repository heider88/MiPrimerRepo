"""Genera versiones vectoriales (SVG) del fondo, el QR y la maqueta de la postal.

Uso:  PYTHONPATH=/tmp/pylib python3 generar_svg.py
Todo se dibuja con formas y degradados nativos (sin imágenes incrustadas ni filtros),
para que Illustrator lo abra como vectores editables, agrupados por capas con nombre.
"""
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

import qrcode
import qrcode.image.svg

TEXTOS = {
    "semestre_numero": "#",
    "semestre_letras": "ro",
    "taller": "Problemas Sociales Colombianos",
    "docente": "[Nombre del docente]",
    "estudiantes": "[Nombres de los integrantes del Grupo B]",
    "proyecto": "¿Cuántos Dani hay en Usme?",
    "descripcion": [
        "Pieza sonora sobre Dani, un joven de 19 años de Usme que terminó el",
        "colegio y no estudia ni trabaja. Cerca de uno de cada cinco jóvenes en",
        "Colombia vive esa situación.",
    ],
    "qr_url": "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/mercado-laboral-de-la-juventud",
}

OUT = Path(__file__).parent
W, H = 2400, 1200
FONT = "'Noto Sans', 'Montserrat', Arial, sans-serif"


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pts(points):
    return " ".join(f"{f(x)},{f(y)}" for x, y in points)


# ------------------------------------------------------------ FONDO
def defs_fondo():
    return """
  <linearGradient id="gCuarto" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#160d2e"/><stop offset="0.6" stop-color="#24154a"/><stop offset="1" stop-color="#2e1b58"/>
  </linearGradient>
  <linearGradient id="gCielo" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#2c2366"/><stop offset="0.45" stop-color="#7a4a92"/>
    <stop offset="0.75" stop-color="#e0767a"/><stop offset="1" stop-color="#f6b26b"/>
  </linearGradient>
  <radialGradient id="gSol"><stop offset="0" stop-color="#ffd696" stop-opacity="0.85"/><stop offset="1" stop-color="#ffd696" stop-opacity="0"/></radialGradient>
  <radialGradient id="gPantalla"><stop offset="0" stop-color="#8cc8ff" stop-opacity="0.5"/><stop offset="1" stop-color="#8cc8ff" stop-opacity="0"/></radialGradient>
  <radialGradient id="gRostro"><stop offset="0" stop-color="#96cdff" stop-opacity="0.35"/><stop offset="1" stop-color="#96cdff" stop-opacity="0"/></radialGradient>
  <radialGradient id="gAlarma"><stop offset="0" stop-color="#ff465a" stop-opacity="0.45"/><stop offset="1" stop-color="#ff465a" stop-opacity="0"/></radialGradient>
  <linearGradient id="gLuzPiso" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#f6b26b" stop-opacity="0.14"/><stop offset="1" stop-color="#f6b26b" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="gFaro" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#ffebaa" stop-opacity="0.45"/><stop offset="1" stop-color="#ffebaa" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="gVineta" cx="0.5" cy="0.5" r="0.75">
    <stop offset="0.55" stop-color="#080414" stop-opacity="0"/><stop offset="1" stop-color="#080414" stop-opacity="0.75"/>
  </radialGradient>
  <clipPath id="clipVentana"><rect x="1480" y="150" width="680" height="610"/></clipPath>
"""


def fondo_body():
    rnd = random.Random(11)
    o = []
    o.append('<g id="Cuarto"><rect width="2400" height="1200" fill="url(#gCuarto)"/></g>')

    # ---- Ventana
    wx0, wy0, wx1, wy1 = 1480, 150, 2160, 760
    sw, sh = wx1 - wx0, wy1 - wy0
    v = ['<g id="Ventana_paisaje" clip-path="url(#clipVentana)">',
         f'<rect x="{wx0}" y="{wy0}" width="{sw}" height="{sh}" fill="url(#gCielo)"/>']
    v.append('<g id="Estrellas">')
    for _ in range(40):
        x, y = wx0 + rnd.randint(0, sw), wy0 + rnd.randint(0, int(sh * 0.35))
        r = rnd.choice([0.8, 1.2, 1.2, 1.6])
        v.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="{rnd.randint(25, 65) / 100}"/>')
    v.append('</g>')
    v.append(f'<circle id="Sol" cx="{f(wx0 + sw * 0.62)}" cy="{f(wy0 + sh * 0.86)}" r="150" fill="url(#gSol)"/>')

    def cerros(base, amp, color, seed, name):
        r2 = random.Random(seed)
        p = [(wx0, wy1)]
        x = 0
        while x <= sw:
            y = wy0 + base - amp * (0.5 + 0.5 * math.sin(x / sw * math.pi * 2.3 + seed)) - r2.randint(0, 18)
            p.append((wx0 + x, y))
            x += 30
        p.append((wx1, wy1))
        return f'<polygon id="{name}" points="{pts(p)}" fill="{color}"/>'

    v.append(cerros(sh * 0.80, 70, "#5a3a7a", 1, "Cerros_lejanos"))
    v.append(cerros(sh * 0.88, 45, "#3a2558", 4, "Cerros_cercanos"))

    v.append('<g id="Casas_Usme">')
    r3 = random.Random(7)
    x = 0
    luces = []
    while x < sw:
        bw, bh = r3.randint(40, 80), r3.randint(35, 90)
        top = sh - 40 - bh
        v.append(f'<rect x="{wx0 + x}" y="{wy0 + top}" width="{bw}" height="{bh + 40}" fill="#22163d"/>')
        for wy in range(top + 10, sh - 50, 22):
            for wxx in range(x + 8, x + bw - 12, 20):
                if r3.random() < 0.35:
                    luces.append(f'<rect x="{wx0 + wxx}" y="{wy0 + wy}" width="8" height="10" fill="#ffd27a" opacity="0.86"/>')
        x += bw + r3.randint(0, 6)
    v.append('</g><g id="Luces_casas">' + "".join(luces) + '</g>')

    bx, by = wx0 + sw * 0.18, wy1 - 78
    v.append(f'<rect id="Calle" x="{wx0}" y="{wy1 - 40}" width="{sw}" height="40" fill="#1a1130"/>')
    v.append('<g id="Bus">')
    v.append(f'<polygon points="{pts([(bx + 230, by + 38), (bx + 420, by + 20), (bx + 420, by + 64)])}" fill="url(#gFaro)"/>')
    for i in range(4):
        yy = by + 10 + i * 11
        v.append(f'<line x1="{f(bx - 140 + i * 20)}" y1="{f(yy)}" x2="{f(bx - 10)}" y2="{f(yy)}" stroke="#fff" stroke-opacity="0.2" stroke-width="2"/>')
    v.append(f'<rect x="{f(bx)}" y="{f(by)}" width="230" height="52" rx="10" fill="#b8324a"/>')
    for i in range(6):
        v.append(f'<rect x="{f(bx + 14 + i * 34)}" y="{f(by + 9)}" width="26" height="17" fill="#ffe3a3" opacity="0.9"/>')
    for cx in (bx + 45, bx + 185):
        v.append(f'<circle cx="{f(cx)}" cy="{f(by + 53)}" r="11" fill="#0e0a1c"/>')
    v.append('</g></g>')
    o.extend(v)

    marco = "#3d2c66"
    o.append(f'<g id="Marco_ventana" fill="none" stroke="{marco}">'
             f'<rect x="{wx0}" y="{wy0}" width="{sw}" height="{sh}" stroke-width="22"/>'
             f'<line x1="{(wx0 + wx1) / 2}" y1="{wy0}" x2="{(wx0 + wx1) / 2}" y2="{wy1}" stroke-width="14"/>'
             f'<line x1="{wx0}" y1="{f(wy0 + sh * 0.42)}" x2="{wx1}" y2="{f(wy0 + sh * 0.42)}" stroke-width="14"/></g>')
    o.append(f'<g id="Cortina"><polygon points="{pts([(wx0 - 60, wy0 - 40), (wx0 + 70, wy0 - 40), (wx0 + 10, wy1 + 120), (wx0 - 90, wy1 + 140)])}" fill="#3b2468"/>')
    for i in range(4):
        o.append(f'<line x1="{wx0 - 40 + i * 28}" y1="{wy0 - 30}" x2="{wx0 - 70 + i * 24}" y2="{wy1 + 120}" stroke="#2c1a50" stroke-width="5"/>')
    o.append('</g>')
    o.append(f'<polygon id="Luz_ventana_piso" points="{pts([(wx0, wy1), (wx1, wy1), (1900, 1200), (900, 1200)])}" fill="url(#gLuzPiso)"/>')

    # ---- Cama y Dani
    o.append('<g id="Cama_Dani">')
    o.append('<rect x="560" y="860" width="900" height="400" rx="30" fill="#22183f"/>')
    o.append('<rect x="560" y="780" width="60" height="420" rx="18" fill="#1b1233"/>')
    o.append('<rect x="630" y="820" width="250" height="85" rx="40" fill="#6b5aa6"/>')
    bl = [(620, 930), (760, 905), (840, 900)]
    for i in range(41):
        x = 840 + i * 16
        y = 870 - 45 * math.sin(i / 40 * math.pi) - 12 * math.sin(i / 3.0)
        bl.append((x, y))
    bl += [(1500, 880), (1530, 960), (1520, 1200), (620, 1200)]
    o.append(f'<polygon id="Cobija" points="{pts(bl)}" fill="#4a3585"/>')
    o.append('<g id="Pliegues" fill="none" stroke="#3a2870" stroke-width="6">')
    for i in range(5):
        x0 = 900 + i * 110
        # arco de 200° a 320° sobre una elipse de 160x180
        cx, cy, rx, ry = x0 + 80, 950, 80, 90
        a0, a1 = math.radians(200), math.radians(320)
        p0 = (cx + rx * math.cos(a0), cy + ry * math.sin(a0))
        p1 = (cx + rx * math.cos(a1), cy + ry * math.sin(a1))
        o.append(f'<path d="M{f(p0[0])},{f(p0[1])} A{rx},{ry} 0 0 1 {f(p1[0])},{f(p1[1])}"/>')
    o.append('</g>')
    o.append('<circle cx="930" cy="760" r="170" fill="url(#gPantalla)"/>')
    o.append('<g id="Dani"><circle cx="800" cy="825" r="55" fill="#140d26"/>'
             '<ellipse cx="797" cy="792" rx="62" ry="37" fill="#0f0a1f"/>'
             '<polyline points="850,890 925,830 955,780" fill="none" stroke="#140d26" stroke-width="30" stroke-linecap="round" stroke-linejoin="round"/>'
             '<circle cx="820" cy="810" r="55" fill="url(#gRostro)"/></g>')
    o.append('<g id="Celular" transform="translate(960 750) rotate(28) translate(-35 -60)">'
             '<rect width="70" height="120" rx="12" fill="#0b0816"/>'
             '<rect x="5" y="8" width="59" height="102" rx="8" fill="#bfe6ff"/>'
             + "".join(f'<rect x="10" y="{16 + i * 22}" width="48" height="14" rx="4" fill="#7fb7ff" opacity="0.8"/>' for i in range(4))
             + '</g>')
    o.append('</g>')

    # ---- Notificaciones
    colores = ["#ff5a7a", "#5ad1ff", "#ffd24a", "#8cff9e", "#c08bff", "#ff9a4a"]
    burbujas = [(1010, 560, 230, 1.00), (1130, 470, 250, 0.92), (980, 380, 200, 0.80), (1180, 300, 240, 0.70),
                (1050, 190, 210, 0.55), (1250, 110, 190, 0.42), (900, 90, 170, 0.32), (1290, 400, 160, 0.60)]
    rn = random.Random(5)
    o.append('<g id="Notificaciones">')
    for i, (bx, by, bw, a) in enumerate(burbujas):
        op = f(0.92 * a)
        o.append(f'<g id="Notificacion_{i + 1}" opacity="{op}">'
                 f'<rect x="{bx + 4}" y="{by + 10}" width="{bw}" height="64" rx="18" fill="#140032" opacity="0.35"/>'
                 f'<rect x="{bx}" y="{by}" width="{bw}" height="64" rx="18" fill="#f8f4ff"/>'
                 f'<rect x="{bx + 12}" y="{by + 12}" width="40" height="40" rx="10" fill="{colores[i % 6]}"/>'
                 f'<rect x="{bx + 64}" y="{by + 16}" width="{bw - 94}" height="12" rx="6" fill="#3c286e"/>'
                 f'<rect x="{bx + 64}" y="{by + 38}" width="{bw - 134}" height="10" rx="5" fill="#8c78be"/>'
                 f'<circle cx="{bx + bw - 5}" cy="{by + 5}" r="17" fill="#ff3c5a"/>'
                 f'<text x="{bx + bw - 5}" y="{by + 11.5}" font-family="{FONT}" font-weight="700" font-size="18" fill="#fff" text-anchor="middle">{rn.randint(2, 99)}</text>'
                 '</g>')
    o.append('</g>')

    # ---- Mesa de noche y alarma
    o.append('<g id="Mesa_alarma">'
             '<rect x="260" y="900" width="260" height="300" fill="#1d1438"/>'
             '<rect x="245" y="885" width="290" height="30" fill="#2a1d4f"/>'
             '<circle cx="390" cy="832" r="180" fill="url(#gAlarma)"/>'
             '<rect x="300" y="780" width="180" height="105" rx="20" fill="#0d0919"/>'
             f'<text x="390" y="855" font-family="{FONT}" font-weight="700" font-size="64" fill="#ff4a63" text-anchor="middle">6:00</text>'
             '<g id="Ondas_alarma" fill="none" stroke="#ff5a6e" stroke-width="6">')
    for i, r in enumerate((130, 175, 220)):
        op = f((150 - i * 40) / 255)
        for a0, a1 in ((300, 360), (180, 240)):
            p0 = (390 + r * math.cos(math.radians(a0)), 832 + r * math.sin(math.radians(a0)))
            p1 = (390 + r * math.cos(math.radians(a1)), 832 + r * math.sin(math.radians(a1)))
            o.append(f'<path d="M{f(p0[0])},{f(p0[1])} A{r},{r} 0 0 1 {f(p1[0])},{f(p1[1])}" stroke-opacity="{op}"/>')
    o.append('</g></g>')

    o.append('<rect id="Vineta" width="2400" height="1200" fill="url(#gVineta)"/>')
    return "\n".join(o)


def svg_doc(defs, body):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'
            f'<defs>{defs}</defs>\n{body}\n</svg>\n')


# ------------------------------------------------------------ QR
def qr_path():
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2,
                      image_factory=qrcode.image.svg.SvgPathImage)
    q.add_data(TEXTOS["qr_url"])
    q.make(fit=True)
    n = q.modules_count + 4  # con borde
    d = []
    for r, row in enumerate(q.modules):
        for c, on in enumerate(row):
            if on:
                d.append(f"M{c + 2},{r + 2}h1v1h-1z")
    return n, "".join(d)


def qr_svg():
    n, d = qr_path()
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 {n} {n}" shape-rendering="crispEdges">\n'
            f'<rect id="Fondo_QR" width="{n}" height="{n}" fill="#fff"/>\n'
            f'<path id="Modulos_QR" d="{d}" fill="#24154a"/>\n</svg>\n')


# ------------------------------------------------------------ MAQUETA
def maqueta_svg():
    t = {k: escape(v) if isinstance(v, str) else [escape(x) for x in v] for k, v in TEXTOS.items()}
    extra_defs = """
  <linearGradient id="gCapaMorada" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#46288c" stop-opacity="0.92"/>
    <stop offset="0.91" stop-color="#46288c" stop-opacity="0.2"/>
    <stop offset="1" stop-color="#46288c" stop-opacity="0.2"/>
  </linearGradient>"""
    n, d = qr_path()
    qs, qx, qy = 300, W - 300 - 120, H - 300 - 120
    sc = qs / n
    b = [f'<g id="Fondo_proyecto">{fondo_body()}</g>',
         '<rect id="Capa_morada" width="2400" height="1200" fill="url(#gCapaMorada)"/>',
         f'<g id="Textos" font-family="{FONT}" fill="#fff">',
         f'<text x="130" y="305" font-size="150" font-weight="800">{t["semestre_numero"]}'
         f'<tspan font-size="56" font-weight="700" dx="6">{t["semestre_letras"]}</tspan></text>',
         f'<text x="320" y="290" font-size="62" font-weight="700">{t["taller"]}</text>',
         f'<text x="130" y="383" font-size="34"><tspan font-weight="700">Docente:</tspan>'
         f'<tspan dx="18" fill="#e1d7ff">{t["docente"]}</tspan></text>',
         '<text x="130" y="488" font-size="34" font-weight="700">Estudiante(s):</text>',
         f'<text x="130" y="533" font-size="34" fill="#e1d7ff">{t["estudiantes"]}</text>',
         f'<text x="130" y="748" font-size="100" font-weight="800">{t["proyecto"]}</text>',
         '<text font-size="34" fill="#e1d7ff">'
         + "".join(f'<tspan x="130" y="{827 + i * 48}">{line}</tspan>' for i, line in enumerate(t["descripcion"]))
         + '</text></g>',
         '<g id="Logos_referencia" fill="none" stroke="#fff" stroke-opacity="0.67" stroke-width="4">'
         '<rect x="1560" y="120" width="340" height="180" rx="20"/><rect x="1960" y="120" width="340" height="180" rx="20"/></g>',
         f'<g id="Logos_texto" font-family="{FONT}" fill="#fff" text-anchor="middle">'
         '<text x="1730" y="226" font-size="46" font-weight="700" opacity="0.8">ITERA V.01</text>'
         '<text x="2130" y="226" font-size="46" font-weight="700" opacity="0.8">DDM</text>'
         '<text x="1930" y="338" font-size="22" opacity="0.67">Logos originales de la plantilla (no mover)</text></g>',
         f'<g id="QR"><rect x="{qx - 20}" y="{qy - 20}" width="{qs + 40}" height="{qs + 40}" rx="24" fill="#fff"/>'
         f'<path transform="translate({qx} {qy}) scale({f(sc)})" d="{d}" fill="#24154a" shape-rendering="crispEdges"/>'
         f'<text x="{qx + qs / 2}" y="{qy + qs + 59}" font-family="{FONT}" font-size="26" font-weight="600" fill="#fff" text-anchor="middle">Escanea: más información</text></g>']
    return svg_doc(defs_fondo() + extra_defs, "\n".join(b))


if __name__ == "__main__":
    (OUT / "fondo_proyecto.svg").write_text(svg_doc(defs_fondo(), fondo_body()), encoding="utf-8")
    (OUT / "qr_contenido_complementario.svg").write_text(qr_svg(), encoding="utf-8")
    (OUT / "postal_maqueta.svg").write_text(maqueta_svg(), encoding="utf-8")
    print("listo")
