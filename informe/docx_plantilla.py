# -*- coding: utf-8 -*-
"""
Utilidades para generar documentos Word a partir de la plantilla institucional
(informe/_plantilla/plantilla.docx) respetando sus estilos:
  Título1  -> títulos numerados (I., II., ...) que alimentan el índice
  Estilo5  -> subtítulos numerados (nivel 2 del índice)
  Estilo4  -> párrafos de texto
  Estilo3 + numId 9 -> viñetas
  PIEDEFOTO -> pies de figura y tabla
"""
import os, re, shutil, struct, zipfile
from xml.sax.saxutils import escape

PLANTILLA = os.path.join(os.path.dirname(__file__), "_plantilla", "plantilla.docx")
ANCHO_UTIL_DXA = 12240 - 2 * 1418          # carta, márgenes de la plantilla
EMU_POR_PULGADA = 914400

# ---------------------------------------------------------------- texto
def _runs(texto, base_rpr="", resaltar=False):
    """Convierte **negrita**, *cursiva* y [[COMPLETAR]] en runs de Word."""
    partes = re.split(r"(\*\*.+?\*\*|\*[^*]+?\*|\[\[.+?\]\])", texto)
    out = []
    for p in partes:
        if not p:
            continue
        rpr = base_rpr
        if p.startswith("**"):
            p, rpr = p[2:-2], rpr + "<w:b/>"
        elif p.startswith("[["):
            p, rpr = "[" + p[2:-2] + "]", rpr + '<w:b/><w:highlight w:val="yellow"/>'
        elif p.startswith("*"):
            p, rpr = p[1:-1], rpr + "<w:i/>"
        out.append('<w:r><w:rPr>%s</w:rPr><w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, escape(p)))
    return "".join(out)

def h1(t):
    return '<w:p><w:pPr><w:pStyle w:val="Ttulo1"/></w:pPr>%s</w:p>' % _runs(t)

def h2(t):
    return ('<w:p><w:pPr><w:pStyle w:val="Estilo5"/><w:spacing w:before="240" w:after="80"/>'
            '<w:rPr><w:sz w:val="24"/></w:rPr></w:pPr>%s</w:p>') % _runs(t, "<w:sz w:val=\"24\"/>")

def h3(t):
    return ('<w:p><w:pPr><w:pStyle w:val="Estilo4"/><w:keepNext/><w:spacing w:before="160" w:after="60"/></w:pPr>%s</w:p>'
            % _runs(t, '<w:b/><w:color w:val="404040"/>'))

def p(t):
    return ('<w:p><w:pPr><w:pStyle w:val="Estilo4"/><w:spacing w:after="120"/></w:pPr>%s</w:p>' % _runs(t))

def vineta(t):
    return ('<w:p><w:pPr><w:pStyle w:val="Estilo3"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="9"/></w:numPr>'
            '<w:spacing w:after="60"/><w:ind w:left="360"/></w:pPr>%s</w:p>'
            % _runs(t, '<w:color w:val="595959"/><w:sz w:val="22"/><w:szCs w:val="22"/>'))

def referencia(t):
    return ('<w:p><w:pPr><w:pStyle w:val="Estilo3"/><w:spacing w:line="480" w:lineRule="auto"/>'
            '<w:ind w:left="709" w:hanging="709"/></w:pPr>%s</w:p>'
            % _runs(t, '<w:color w:val="595959"/><w:sz w:val="22"/>'))

def pie(t):
    return ('<w:p><w:pPr><w:pStyle w:val="PIEDEFOTO"/><w:spacing w:before="60" w:after="200"/></w:pPr>%s</w:p>'
            % _runs(t))

def salto_pagina():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

# ---------------------------------------------------------------- tablas
def tabla(encabezados, filas, anchos_rel, alinear=None, tam=18):
    total = ANCHO_UTIL_DXA
    anchos = [int(total * a / sum(anchos_rel)) for a in anchos_rel]
    anchos[-1] = total - sum(anchos[:-1])
    alinear = alinear or ["left"] * len(encabezados)
    borde = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
    xml = ['<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>' % total,
           "".join(borde.format(b) for b in ["top", "bottom", "insideH"]),
           '</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="70" w:type="dxa"/>'
           '<w:right w:w="70" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>',
           "".join('<w:gridCol w:w="%d"/>' % a for a in anchos), "</w:tblGrid>"]

    def celda(texto, ancho, jc, cabecera):
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="404040"/>' if cabecera else ""
        rpr = '<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (tam, tam)
        rpr += '<w:b/><w:color w:val="FFFFFF"/>' if cabecera else '<w:color w:val="404040"/>'
        return ('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s<w:vAlign w:val="center"/></w:tcPr>'
                '<w:p><w:pPr><w:spacing w:before="30" w:after="30" w:line="240" w:lineRule="auto"/>'
                '<w:jc w:val="%s"/></w:pPr>%s</w:p></w:tc>') % (ancho, shd, jc, _runs(str(texto), rpr))

    xml.append('<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>')
    xml += [celda(e, a, "center" if j else "left", True) for j, (e, a) in enumerate(zip(encabezados, anchos))]
    xml.append("</w:tr>")
    for f in filas:
        xml.append("<w:tr><w:trPr><w:cantSplit/></w:trPr>")
        xml += [celda(v, a, al, False) for v, a, al in zip(f, anchos, alinear)]
        xml.append("</w:tr>")
    xml.append("</w:tbl>")
    return "".join(xml) + '<w:p><w:pPr><w:spacing w:after="0"/></w:pPr></w:p>'

# ---------------------------------------------------------------- imágenes
def _tam_png(ruta):
    with open(ruta, "rb") as f:
        f.read(16)
        return struct.unpack(">II", f.read(8))

class Documento:
    def __init__(self):
        self.bloques, self.imagenes = [], []

    def add(self, *xs):
        self.bloques.extend(xs)

    def figura(self, ruta, texto_pie, ancho_pulg=6.3, alt=""):
        n = len(self.imagenes) + 1
        rid, nombre = "rIdFig%d" % n, "fig_informe_%d.png" % n
        self.imagenes.append((rid, nombre, ruta))
        w, h = _tam_png(ruta)
        cx = int(ancho_pulg * EMU_POR_PULGADA); cy = int(cx * h / w)
        dib = ('<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="0"/><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
               '<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
               '<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{id}" name="Figura {n}" descr="{alt}"/>'
               '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
               '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
               '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
               '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
               '<pic:nvPicPr><pic:cNvPr id="{id}" name="{nombre}"/><pic:cNvPicPr/></pic:nvPicPr>'
               '<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
               '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
               '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
               '</wp:inline></w:drawing></w:r></w:p>').format(cx=cx, cy=cy, id=5000 + n, n=n,
                                                                alt=escape(alt or texto_pie), nombre=nombre, rid=rid)
        self.add(dib, pie(texto_pie))

    # ------------------------------------------------------------ ensamblado
    def guardar(self, salida, portada, pie_pagina, con_indice=True):
        tmp = salida + "_tmp"
        shutil.rmtree(tmp, ignore_errors=True)
        with zipfile.ZipFile(PLANTILLA) as z:
            z.extractall(tmp)
        for raiz, _, archivos in os.walk(tmp):          # plantilla externa: sin enlaces simbólicos
            for a in archivos:
                if os.path.islink(os.path.join(raiz, a)):
                    os.remove(os.path.join(raiz, a))

        ruta_doc = os.path.join(tmp, "word", "document.xml")
        x = open(ruta_doc, encoding="utf-8").read()

        # Portada (cada campo existe dos veces: cuadro de texto y su respaldo VML)
        for buscar, reemplazo in portada:
            if buscar not in x:
                raise ValueError("No se encontró en la plantilla: " + buscar)
            x = x.replace(buscar, reemplazo)

        # Cuerpo: se reemplaza desde las instrucciones (o desde el índice) hasta sectPr
        marca = ("ubicando el mouse sobre ella" if con_indice else ">Contenido<")
        i = x.index(marca)
        ini = max(m.start() for m in re.finditer(r"<w:p[ >]", x[:i]))
        if con_indice:
            # conserva el cierre del campo TOC; quita solo el párrafo de instrucciones en adelante
            pass
        fin = x.rindex("<w:sectPr")
        cuerpo = ("" if not con_indice else salto_pagina()) + "".join(self.bloques)
        x = x[:ini] + cuerpo + x[fin:]
        # El campo TOC de la plantilla trae \f (solo entradas TC): se quita para indexar los títulos
        x = x.replace(r"TOC \f \h", r"TOC \h")
        # Con configuración regional es-CL el separador de listas es ";" (con "," Word no reconoce los estilos)
        x = x.replace("Título1,1,Estilo5,2", "Título1;1;Estilo5;2")
        open(ruta_doc, "w", encoding="utf-8").write(x)

        # Pie de página de las páginas interiores
        ruta_pie = os.path.join(tmp, "word", "footer2.xml")
        f = open(ruta_pie, encoding="utf-8").read()
        f = f.replace("Nombre del informe", escape(pie_pagina))
        open(ruta_pie, "w", encoding="utf-8").write(f)

        # Imágenes y relaciones
        rels_p = os.path.join(tmp, "word", "_rels", "document.xml.rels")
        rels = open(rels_p, encoding="utf-8").read()
        nuevas = ""
        for rid, nombre, ruta in self.imagenes:
            shutil.copy(ruta, os.path.join(tmp, "word", "media", nombre))
            nuevas += ('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                       'relationships/image" Target="media/%s"/>' % (rid, nombre))
        rels = rels.replace("</Relationships>", nuevas + "</Relationships>")
        open(rels_p, "w", encoding="utf-8").write(rels)

        # Propiedades: limpiar autor/título heredados de la plantilla
        core_p = os.path.join(tmp, "docProps", "core.xml")
        c = open(core_p, encoding="utf-8").read()
        c = re.sub(r"<dc:title>.*?</dc:title>", "<dc:title>%s</dc:title>" % escape(pie_pagina), c)
        c = re.sub(r"<dc:creator>.*?</dc:creator>", "<dc:creator></dc:creator>", c)
        c = re.sub(r"<cp:lastModifiedBy>.*?</cp:lastModifiedBy>", "<cp:lastModifiedBy></cp:lastModifiedBy>", c)
        open(core_p, "w", encoding="utf-8").write(c)

        if os.path.exists(salida):
            os.remove(salida)
        with zipfile.ZipFile(salida, "w", zipfile.ZIP_DEFLATED) as z:
            # [Content_Types].xml primero, como espera Word
            z.write(os.path.join(tmp, "[Content_Types].xml"), "[Content_Types].xml")
            for raiz, _, archivos in os.walk(tmp):
                for a in archivos:
                    rel = os.path.relpath(os.path.join(raiz, a), tmp).replace(os.sep, "/")
                    if rel != "[Content_Types].xml":
                        z.write(os.path.join(raiz, a), rel)
        shutil.rmtree(tmp)
