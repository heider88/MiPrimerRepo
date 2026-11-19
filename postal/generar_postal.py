"""Genera la imagen de fondo, el QR y una maqueta de la postal "¿Cuántos Dani hay en Usme?".

Uso:  PYTHONPATH=/tmp/pylib python3 generar_postal.py
Edite el bloque TEXTOS para cambiar semestre, docente, estudiantes o el enlace del QR.
"""
import math
import random
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- TEXTOS
TEXTOS = {
    "semestre_numero": "#",          # p. ej. "3"
    "semestre_letras": "ro",         # p. ej. "ro", "do", "to", "vo", "no", "mo"
    "taller": "Problemas Sociales Colombianos",
    "docente": "[Nombre del docente]",
    "estudiantes": "[Nombres de los integrantes del Grupo B]",
    "proyecto": "¿Cuántos Dani hay en Usme?",
    "descripcion": (
        "Pieza sonora sobre Dani, un joven de 19 años de Usme que terminó el colegio "
        "y no estudia ni trabaja. Cerca de uno de cada cinco jóvenes en Colombia vive "
        "esa situación."
    ),
    # Enlace provisional: reemplazar por el enlace al audio del proyecto.
    "qr_url": "https://www.dane.gov.co/index.php/estadisticas-por-tema/mercado-laboral/mercado-laboral-de-la-juventud",
}

OUT = Path(__file__).parent
W, H = 2400, 1200          # proporción 2:1, igual que la pieza de la plantilla
S = 2                      # sobremuestreo para bordes suaves
FONT = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf"
random.seed(11)


def font(size, weight=400):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def s(v):
    return int(v * S)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def hexc(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def vertical_gradient(w, h, stops):
    img = Image.new("RGBA", (w, h))
    px = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0) if p1 > p0 else 0
                px.line([(0, y), (w, y)], fill=lerp(c0, c1, k))
                break
    return img


def radial_glow(size, color, radius, blur):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = radius
    r = blur
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    return layer.filter(ImageFilter.GaussianBlur(r * 0.6))


# ------------------------------------------------------------ FONDO
def fondo():
    w, h = s(W), s(H)
    img = vertical_gradient(w, h, [(0, hexc("#160d2e")), (0.6, hexc("#24154a")), (1, hexc("#2e1b58"))])
    d = ImageDraw.Draw(img, "RGBA")

    # --- Ventana con el amanecer sobre los cerros de Usme
    wx0, wy0, wx1, wy1 = s(1480), s(150), s(2160), s(760)
    sky = vertical_gradient(wx1 - wx0, wy1 - wy0, [
        (0, hexc("#2c2366")), (0.45, hexc("#7a4a92")), (0.75, hexc("#e0767a")), (1, hexc("#f6b26b"))])
    sd = ImageDraw.Draw(sky, "RGBA")
    sw, sh = sky.size
    # estrellas que se apagan
    for _ in range(40):
        x, y = random.randint(0, sw), random.randint(0, int(sh * 0.35))
        r = random.choice([1, 2, 2, 3])
        sd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, random.randint(60, 160)))
    # sol naciente
    sun = radial_glow((sw, sh), (255, 214, 150, 200), (int(sw * 0.62), int(sh * 0.86)), s(90))
    sky.alpha_composite(sun)
    # cerros (dos planos)
    def cerros(base, amp, color, seed):
        rnd = random.Random(seed)
        pts = [(0, sh)]
        x = 0
        while x <= sw:
            y = base - amp * (0.5 + 0.5 * math.sin(x / sw * math.pi * 2.3 + seed)) - rnd.randint(0, s(18))
            pts.append((x, y))
            x += s(30)
        pts += [(sw, sh)]
        sd.polygon(pts, fill=color)
    cerros(sh * 0.80, s(70), hexc("#5a3a7a"), 1)
    cerros(sh * 0.88, s(45), hexc("#3a2558"), 4)
    # casas del barrio con luces encendidas
    x = 0
    rnd = random.Random(7)
    while x < sw:
        bw = rnd.randint(s(40), s(80))
        bh = rnd.randint(s(35), s(90))
        top = sh - s(40) - bh
        sd.rectangle([x, top, x + bw, sh], fill=hexc("#22163d"))
        for wy in range(top + s(10), sh - s(50), s(22)):
            for wxx in range(x + s(8), x + bw - s(12), s(20)):
                if rnd.random() < 0.35:
                    sd.rectangle([wxx, wy, wxx + s(8), wy + s(10)], fill=hexc("#ffd27a", 220))
        x += bw + rnd.randint(0, s(6))
    # calle y bus que pasa de largo
    sd.rectangle([0, sh - s(40), sw, sh], fill=hexc("#1a1130"))
    bx, by = int(sw * 0.18), sh - s(78)
    sd.rounded_rectangle([bx, by, bx + s(230), by + s(52)], radius=s(10), fill=hexc("#b8324a"))
    for i in range(6):
        sd.rectangle([bx + s(14 + i * 34), by + s(9), bx + s(40 + i * 34), by + s(26)], fill=hexc("#ffe3a3", 230))
    for cx in (bx + s(45), bx + s(185)):
        sd.ellipse([cx - s(11), by + s(42), cx + s(11), by + s(64)], fill=hexc("#0e0a1c"))
    beam = Image.new("RGBA", sky.size, (0, 0, 0, 0))
    ImageDraw.Draw(beam).polygon([(bx + s(230), by + s(38)), (bx + s(420), by + s(20)), (bx + s(420), by + s(64))],
                                 fill=(255, 235, 170, 90))
    sky.alpha_composite(beam.filter(ImageFilter.GaussianBlur(s(8))))
    # estelas de movimiento
    for i in range(4):
        yy = by + s(10 + i * 11)
        sd.line([(bx - s(140 - i * 20), yy), (bx - s(10), yy)], fill=(255, 255, 255, 50), width=s(2))
    img.paste(sky, (wx0, wy0))
    # marco y cruces de la ventana
    d.rectangle([wx0, wy0, wx1, wy1], outline=hexc("#3d2c66"), width=s(22))
    d.line([((wx0 + wx1) // 2, wy0), ((wx0 + wx1) // 2, wy1)], fill=hexc("#3d2c66"), width=s(14))
    d.line([(wx0, wy0 + (wy1 - wy0) * 0.42), (wx1, wy0 + (wy1 - wy0) * 0.42)], fill=hexc("#3d2c66"), width=s(14))
    # cortina
    d.polygon([(wx0 - s(60), wy0 - s(40)), (wx0 + s(70), wy0 - s(40)), (wx0 + s(10), wy1 + s(120)), (wx0 - s(90), wy1 + s(140))],
              fill=hexc("#3b2468"))
    for i in range(4):
        d.line([(wx0 - s(40) + i * s(28), wy0 - s(30)), (wx0 - s(70) + i * s(24), wy1 + s(120))], fill=hexc("#2c1a50"), width=s(5))

    # luz de la ventana que cae sobre el cuarto
    light = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(light).polygon([(wx0, wy1), (wx1, wy1), (s(1900), h), (s(900), h)], fill=(246, 178, 107, 45))
    img.alpha_composite(light.filter(ImageFilter.GaussianBlur(s(40))))

    # --- Cama con Dani acostado mirando el celular
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([s(560), s(860), s(1460), s(1260)], radius=s(30), fill=hexc("#22183f"))      # base
    d.rounded_rectangle([s(560), s(780), s(620), s(1200)], radius=s(18), fill=hexc("#1b1233"))       # cabecero
    d.rounded_rectangle([s(630), s(820), s(880), s(905)], radius=s(40), fill=hexc("#6b5aa6"))        # almohada
    # cobija con pliegues
    blanket = [(s(620), s(930)), (s(760), s(905)), (s(840), s(900))]
    for i in range(0, 41):
        x = s(840) + i * s(16)
        y = s(870) - s(45) * math.sin(i / 40 * math.pi) - s(12) * math.sin(i / 3.0)
        blanket.append((x, y))
    blanket += [(s(1500), s(880)), (s(1530), s(960)), (s(1520), s(1260)), (s(620), s(1260))]
    d.polygon(blanket, fill=hexc("#4a3585"))
    for i in range(5):
        x0 = s(900 + i * 110)
        d.arc([x0, s(860), x0 + s(160), s(1040)], 200, 320, fill=hexc("#3a2870"), width=s(6))
    # cabeza y brazo
    d.ellipse([s(745), s(770), s(855), s(880)], fill=hexc("#140d26"))
    d.ellipse([s(735), s(755), s(860), s(830)], fill=hexc("#0f0a1f"))                                 # pelo
    d.line([(s(850), s(890)), (s(925), s(830)), (s(955), s(780))], fill=hexc("#140d26"), width=s(30), joint="curve")
    # celular con pantalla encendida
    phone = Image.new("RGBA", (s(70), s(120)), (0, 0, 0, 0))
    pd = ImageDraw.Draw(phone)
    pd.rounded_rectangle([0, 0, s(70) - 1, s(120) - 1], radius=s(12), fill=hexc("#0b0816"))
    pd.rounded_rectangle([s(5), s(8), s(64), s(110)], radius=s(8), fill=hexc("#bfe6ff"))
    for i in range(4):
        pd.rounded_rectangle([s(10), s(16 + i * 22), s(58), s(30 + i * 22)], radius=s(4), fill=hexc("#7fb7ff", 200))
    phone = phone.rotate(-28, expand=True, resample=Image.BICUBIC)
    glow = radial_glow((w, h), (140, 200, 255, 120), (s(930), s(760)), s(170))
    img.alpha_composite(glow)
    img.alpha_composite(phone, (s(905), s(690)))
    d = ImageDraw.Draw(img, "RGBA")
    # rostro iluminado por la pantalla
    face = radial_glow((w, h), (150, 205, 255, 70), (s(820), s(810)), s(55))
    img.alpha_composite(face)

    # --- Notificaciones que suben desde el celular
    notif = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    nd = ImageDraw.Draw(notif, "RGBA")
    icon_colors = ["#ff5a7a", "#5ad1ff", "#ffd24a", "#8cff9e", "#c08bff", "#ff9a4a"]
    bubbles = [
        (1010, 560, 230, 1.00), (1130, 470, 250, 0.92), (980, 380, 200, 0.80), (1180, 300, 240, 0.70),
        (1050, 190, 210, 0.55), (1250, 110, 190, 0.42), (900, 90, 170, 0.32), (1290, 400, 160, 0.60),
    ]
    for i, (bx, by, bw, a) in enumerate(bubbles):
        alpha = int(235 * a)
        bh = 64
        nd.rounded_rectangle([s(bx), s(by), s(bx + bw), s(by + bh)], radius=s(18), fill=(248, 244, 255, alpha))
        c = hexc(icon_colors[i % len(icon_colors)], alpha)
        nd.rounded_rectangle([s(bx + 12), s(by + 12), s(bx + 52), s(by + 52)], radius=s(10), fill=c)
        nd.rounded_rectangle([s(bx + 64), s(by + 16), s(bx + bw - 30), s(by + 28)], radius=s(6), fill=(60, 40, 110, alpha))
        nd.rounded_rectangle([s(bx + 64), s(by + 38), s(bx + bw - 70), s(by + 48)], radius=s(5), fill=(140, 120, 190, alpha))
        # contador rojo
        nd.ellipse([s(bx + bw - 22), s(by - 12), s(bx + bw + 12), s(by + 22)], fill=(255, 60, 90, alpha))
        nd.text((s(bx + bw - 5), s(by + 5)), str(random.randint(2, 99)), fill=(255, 255, 255, alpha),
                font=font(s(18), 700), anchor="mm")
    sh_ = notif.filter(ImageFilter.GaussianBlur(s(14)))
    shadow = Image.new("RGBA", (w, h), (20, 0, 60, 0))
    shadow.putalpha(sh_.split()[3].point(lambda v: int(v * 0.5)))
    img.alpha_composite(shadow, (0, s(10)))
    img.alpha_composite(notif)

    # --- Mesa de noche con la alarma de las 6:00
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([s(260), s(900), s(520), s(1260)], fill=hexc("#1d1438"))
    d.rectangle([s(245), s(885), s(535), s(915)], fill=hexc("#2a1d4f"))
    d.rounded_rectangle([s(300), s(780), s(480), s(885)], radius=s(20), fill=hexc("#0d0919"))
    alarm_glow = radial_glow((w, h), (255, 70, 90, 110), (s(390), s(832)), s(110))
    img.alpha_composite(alarm_glow)
    d = ImageDraw.Draw(img, "RGBA")
    d.text((s(390), s(832)), "6:00", fill=hexc("#ff4a63"), font=font(s(64), 700), anchor="mm")
    for i, r in enumerate((130, 175, 220)):
        d.arc([s(390 - r), s(832 - r), s(390 + r), s(832 + r)], 300, 360, fill=(255, 90, 110, 150 - i * 40), width=s(6))
        d.arc([s(390 - r), s(832 - r), s(390 + r), s(832 + r)], 180, 240, fill=(255, 90, 110, 150 - i * 40), width=s(6))

    # viñeta suave
    vig = Image.new("L", (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-s(300), -s(250), w + s(300), h + s(250)], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(s(160)))
    dark = Image.new("RGBA", (w, h), (8, 4, 20, 255))
    dark.putalpha(vig.point(lambda v: int((255 - v) * 0.75)))
    img.alpha_composite(dark)

    return img.resize((W, H), Image.LANCZOS).convert("RGB")


# ------------------------------------------------------------ QR
def qr():
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=20, border=2)
    q.add_data(TEXTOS["qr_url"])
    q.make(fit=True)
    return q.make_image(fill_color="#24154a", back_color="white").convert("RGB")


# ------------------------------------------------------------ MAQUETA
def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return lines


def maqueta(bg, qr_img):
    img = bg.convert("RGBA")
    # capa morada como la de la plantilla, más densa a la izquierda para leer los textos
    ov = Image.new("RGBA", img.size)
    od = ImageDraw.Draw(ov)
    for x in range(W):
        t = x / W
        a = int(185 * max(0.0, 1 - t * 1.1) + 50)
        od.line([(x, 0), (x, H)], fill=(70, 40, 140, a))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img, "RGBA")
    white, soft = (255, 255, 255, 255), (225, 215, 255, 255)

    x0 = 130
    d.text((x0, 150), TEXTOS["semestre_numero"], fill=white, font=font(150, 800))
    nw = d.textlength(TEXTOS["semestre_numero"], font=font(150, 800))
    d.text((x0 + nw + 6, 238), TEXTOS["semestre_letras"], fill=white, font=font(56, 700))
    d.text((x0 + nw + 90, 222), TEXTOS["taller"], fill=white, font=font(62, 700))
    d.text((x0, 345), "Docente:", fill=white, font=font(34, 700))
    d.text((x0 + 170, 345), TEXTOS["docente"], fill=soft, font=font(34, 400))
    d.text((x0, 450), "Estudiante(s):", fill=white, font=font(34, 700))
    d.text((x0, 495), TEXTOS["estudiantes"], fill=soft, font=font(34, 400))

    d.text((x0, 640), TEXTOS["proyecto"], fill=white, font=font(100, 800))
    fdesc = font(34, 400)
    for i, line in enumerate(wrap(d, TEXTOS["descripcion"], fdesc, 1150)):
        d.text((x0, 790 + i * 48), line, fill=soft, font=fdesc)

    # espacios reservados para los logos (en la pieza real se dejan los originales)
    for (lx, label) in ((1560, "ITERA V.01"), (1960, "DDM")):
        d.rounded_rectangle([lx, 120, lx + 340, 300], radius=20, outline=(255, 255, 255, 170), width=4)
        d.text((lx + 170, 210), label, fill=(255, 255, 255, 200), font=font(46, 700), anchor="mm")
    d.text((1930, 330), "Logos originales de la plantilla (no mover)", fill=(255, 255, 255, 170),
           font=font(22, 400), anchor="mm")

    # QR en el recuadro inferior derecho
    qs = 300
    qx, qy = W - qs - 120, H - qs - 120
    d.rounded_rectangle([qx - 20, qy - 20, qx + qs + 20, qy + qs + 20], radius=24, fill=(255, 255, 255, 255))
    img.paste(qr_img.resize((qs, qs), Image.NEAREST), (qx, qy))
    d.text((qx + qs // 2, qy + qs + 50), "Escanea: más información", fill=white, font=font(26, 600), anchor="mm")
    return img.convert("RGB")


if __name__ == "__main__":
    bg = fondo()
    bg.save(OUT / "fondo_proyecto.png")
    q = qr()
    q.save(OUT / "qr_contenido_complementario.png")
    maqueta(bg, q).save(OUT / "postal_maqueta.png")
    print("listo")
