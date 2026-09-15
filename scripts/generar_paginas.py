from pathlib import Path
from html import escape

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, SKOS


# ============================================================
# Configuración
# ============================================================

BASE = "https://cdg-idera.github.io/ontologias/catalogo-objetos/"
IDERA = Namespace(BASE)

TTL = Path("catalogo-objetos/catalogo-idera.ttl")
RAIZ = Path("catalogo-objetos")


# ============================================================
# Leer ontología
# ============================================================

g = Graph()
g.parse(TTL, format="turtle")

print(f"Ontología cargada: {len(g)} triples")


# ============================================================
# Funciones auxiliares
# ============================================================

def valor(recurso, propiedad):
    if recurso is None:
        return ""
    v = g.value(recurso, propiedad)
    return "" if v is None else str(v)


def codigo_iri(recurso):
    if recurso is None:
        return ""
    return str(recurso).rstrip("/").split("/")[-1]


def enlace(recurso, texto):
    if recurso is None:
        return escape(texto)

    return (
        f'<a href="{escape(str(recurso))}">'
        f'{escape(texto)}</a>'
    )


def estilos():
    return """
<style>
body {
    font-family: Arial, sans-serif;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 20px;
    line-height: 1.6;
}

h1 {
    margin-bottom: 0;
}

.codigo {
    color: #555;
    font-size: 1.2em;
}

dt {
    font-weight: bold;
    margin-top: 15px;
}

dd {
    margin-left: 0;
}

code {
    background: #f4f4f4;
    padding: 3px 6px;
}

.cabecera {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 25px;
}

.cabecera img {
    width: 38px;
    height: auto;
}

.cabecera span {
    font-size: 1em;
    font-weight: bold;
}
</style>
"""


def cabecera(profundidad=2):
    ruta_logo = "../" * profundidad + "images/idera.jpg"

    return f"""
<header class="cabecera">
<img src="{ruta_logo}" alt="IDERA">
<span>Catálogo de Objetos Geográficos de IDERA V2.2</span>
</header>
"""


def inicio_html(titulo, descripcion, profundidad=2):
    return f"""<!DOCTYPE html>
<html lang="es">

<head>
<meta charset="UTF-8">

<title>{escape(titulo)} — Catálogo IDERA</title>

<meta name="description"
      content="{escape(descripcion)}">

<link rel="alternate"
      type="text/turtle"
      href="{BASE}catalogo-idera.ttl">

{estilos()}

</head>

<body>

{cabecera(profundidad)}

<main>
"""


def fin_html():
    return """
</main>

<hr>

<footer>
<p>
Ontología del Catálogo de Objetos Geográficos de IDERA ·
GTT Ciencia de Datos Geoespaciales de IDERA
</p>
</footer>

</body>
</html>
"""


# ============================================================
# CLASES
# ============================================================

def generar_clases():

    clases = sorted(
        set(g.subjects(RDF.type, IDERA.ClaseCatalogo)),
        key=lambda x: valor(x, IDERA.codigo)
    )

    for clase in clases:

        codigo = valor(clase, IDERA.codigo)
        nombre = valor(clase, RDFS.label)
        definicion = valor(clase, SKOS.definition)

        subclases = sorted(
            set(g.subjects(IDERA.esSubclaseDe, clase)),
            key=lambda x: valor(x, IDERA.codigo)
        )

        lista = ""

        for subclase in subclases:
            codigo_sub = valor(subclase, IDERA.codigo)
            nombre_sub = valor(subclase, RDFS.label)

            lista += (
                "<li>"
                + enlace(subclase, f"{codigo_sub} — {nombre_sub}")
                + "</li>\n"
            )

        html = inicio_html(nombre, f"Clase {codigo}: {nombre}")

        html += f"""
<h1>{escape(nombre)}</h1>

<div class="codigo">Clase · {escape(codigo)}</div>

<h2>Definición</h2>
<p>{escape(definicion)}</p>

<h2>Subclases</h2>
<ul>
{lista}
</ul>

<h2>Identificador persistente</h2>
<p><code>{escape(str(clase))}</code></p>
"""

        html += fin_html()

        salida = RAIZ / "clase" / codigo / "index.html"
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(html, encoding="utf-8")

    return len(clases)


# ============================================================
# SUBCLASES
# ============================================================

def generar_subclases():

    subclases = sorted(
        set(g.subjects(RDF.type, IDERA.SubclaseCatalogo)),
        key=lambda x: valor(x, IDERA.codigo)
    )

    for subclase in subclases:

        codigo = valor(subclase, IDERA.codigo)
        nombre = valor(subclase, RDFS.label)
        definicion = valor(subclase, SKOS.definition)

        clase = g.value(subclase, IDERA.esSubclaseDe)

        codigo_clase = valor(clase, IDERA.codigo)
        nombre_clase = valor(clase, RDFS.label)

        objetos = sorted(
            set(g.subjects(IDERA.perteneceASubclase, subclase)),
            key=lambda x: valor(x, IDERA.codigo)
        )

        lista = ""

        for objeto in objetos:
            codigo_og = valor(objeto, IDERA.codigo)
            nombre_og = valor(objeto, RDFS.label)

            lista += (
                "<li>"
                + enlace(objeto, f"{codigo_og} — {nombre_og}")
                + "</li>\n"
            )

        html = inicio_html(
            nombre,
            f"Subclase {codigo}: {nombre}"
        )

        html += f"""
<h1>{escape(nombre)}</h1>

<div class="codigo">Subclase · {escape(codigo)}</div>

<h2>Definición</h2>
<p>{escape(definicion)}</p>

<h2>Descripción en el catálogo</h2>

<dl>
<dt>Clase</dt>
<dd>{enlace(clase, f"{codigo_clase} — {nombre_clase}")}</dd>
</dl>

<h2>Objetos geográficos</h2>
<ul>
{lista}
</ul>

<h2>Identificador persistente</h2>
<p><code>{escape(str(subclase))}</code></p>
"""

        html += fin_html()

        salida = RAIZ / "subclase" / codigo / "index.html"
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(html, encoding="utf-8")

    return len(subclases)


# ============================================================
# OBJETOS GEOGRÁFICOS
# ============================================================

def generar_objetos():

    objetos = sorted(
        set(
            g.subjects(
                RDF.type,
                IDERA.ObjetoGeograficoCatalogado
            )
        ),
        key=lambda x: valor(x, IDERA.codigo)
    )

    for og in objetos:

        codigo = valor(og, IDERA.codigo)
        nombre = valor(og, RDFS.label)
        definicion = valor(og, SKOS.definition)

        geometria = valor(og, IDERA.tipoGeometrico)
        dbyf = valor(og, IDERA.dbyf)

        subclase = g.value(
            og,
            IDERA.perteneceASubclase
        )

        codigo_sub = valor(subclase, IDERA.codigo)
        nombre_sub = valor(subclase, RDFS.label)

        feature = g.value(
            og,
            IDERA.defineClaseImplementable
        )

        atributos = sorted(
            set(g.objects(og, IDERA.tieneAtributo)),
            key=lambda x: codigo_iri(x)
        )

        lista = ""

        for atributo in atributos:

            codigo_atributo = codigo_iri(atributo)
            nombre_atributo = valor(atributo, RDFS.label)

            texto = codigo_atributo

            if nombre_atributo:
                texto += f" — {nombre_atributo}"

            lista += (
                "<li>"
                + enlace(atributo, texto)
                + "</li>\n"
            )

        html = inicio_html(
            nombre,
            f"Objeto Geográfico {codigo}: {nombre}"
        )

        html += f"""
<h1>{escape(nombre)}</h1>

<div class="codigo">
Objeto Geográfico · {escape(codigo)}
</div>

<h2>Definición</h2>
<p>{escape(definicion)}</p>

<h2>Descripción en el catálogo</h2>

<dl>

<dt>Tipo geométrico</dt>
<dd>{escape(geometria)}</dd>

<dt>DBYF</dt>
<dd>{escape(dbyf)}</dd>

<dt>Subclase</dt>
<dd>
{enlace(subclase, f"{codigo_sub} — {nombre_sub}")}
</dd>

<dt>Clase OWL implementable</dt>
<dd>
{enlace(feature, str(feature) if feature else "—")}
</dd>

</dl>

<h2>Atributos</h2>

<ul>
{lista}
</ul>

<h2>Identificador persistente</h2>
<p><code>{escape(str(og))}</code></p>
"""

        html += fin_html()

        salida = RAIZ / "og" / codigo / "index.html"
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(html, encoding="utf-8")

    return len(objetos)


# ============================================================
# ATRIBUTOS
# ============================================================

def generar_atributos():

    atributos = sorted(
        set(
            g.subjects(
                RDF.type,
                IDERA.AtributoCatalogado
            )
        ),
        key=lambda x: valor(x, IDERA.codigo)
    )

    for atributo in atributos:

        codigo = valor(atributo, IDERA.codigo)

        # Para los atributos sin código declarado,
        # utilizamos el último componente de su IRI.
        if not codigo:
            codigo = codigo_iri(atributo)

        nombre = valor(atributo, RDFS.label)
        definicion = valor(atributo, SKOS.definition)

        tipo = valor(
            atributo,
            IDERA.tipoAtributo
        )

        tiene_dominio = valor(
            atributo,
            IDERA.tieneDominio
        )

        propiedad = g.value(
            atributo,
            IDERA.definePropiedadImplementable
        )

        dominios = sorted(
            set(
                g.subjects(
                    IDERA.esValorDeDominioDe,
                    atributo
                )
            ),
            key=lambda x: valor(
                x,
                IDERA.codigoValorDominio
            )
        )

        lista_dominios = ""

        for dominio in dominios:

            codigo_dominio = valor(
                dominio,
                IDERA.codigoValorDominio
            )

            nombre_dominio = valor(
                dominio,
                RDFS.label
            )

            texto = codigo_dominio

            if nombre_dominio:
                texto += f" — {nombre_dominio}"

            lista_dominios += (
                "<li>"
                + enlace(dominio, texto)
                + "</li>\n"
            )

        html = inicio_html(
            nombre,
            f"Atributo {codigo}: {nombre}"
        )

        html += f"""
<h1>{escape(nombre)}</h1>

<div class="codigo">
Atributo · {escape(codigo)}
</div>

<h2>Definición</h2>
<p>{escape(definicion)}</p>

<h2>Descripción en el catálogo</h2>

<dl>

<dt>Tipo de atributo</dt>
<dd>{escape(tipo) if tipo else "—"}</dd>

<dt>Tiene dominio</dt>
<dd>{escape(tiene_dominio) if tiene_dominio else "—"}</dd>

<dt>Propiedad OWL implementable</dt>
<dd>
{enlace(
    propiedad,
    str(propiedad) if propiedad else "—"
)}
</dd>

</dl>
"""

        if dominios:
            html += f"""
<h2>Valores de dominio</h2>

<ul>
{lista_dominios}
</ul>
"""

        html += f"""
<h2>Identificador persistente</h2>

<p><code>{escape(str(atributo))}</code></p>
"""

        html += fin_html()

        salida = (
            RAIZ
            / "atributo"
            / codigo
            / "index.html"
        )

        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(html, encoding="utf-8")

    return len(atributos)


# ============================================================
# VALORES DE DOMINIO
# ============================================================

def generar_dominios():

    dominios = sorted(
        set(
            g.subjects(
                RDF.type,
                IDERA.ValorDominio
            )
        ),
        key=lambda x: str(x)
    )

    for dominio in dominios:

        codigo = valor(
            dominio,
            IDERA.codigoValorDominio
        )

        nombre = valor(
            dominio,
            RDFS.label
        )

        observacion = valor(
            dominio,
            IDERA.observacionFuente
        )

        atributo = g.value(
            dominio,
            IDERA.esValorDeDominioDe
        )

        codigo_atributo = valor(
            atributo,
            IDERA.codigo
        )

        if not codigo_atributo:
            codigo_atributo = codigo_iri(atributo)

        nombre_atributo = valor(
            atributo,
            RDFS.label
        )

        # La ruta se toma del propio IRI:
        # dominio/BSC/2 -> BSC / 2
        partes = str(dominio).rstrip("/").split("/")

        codigo_ruta = partes[-1]
        atributo_ruta = partes[-2]

        html = inicio_html(
            nombre,
            f"Valor de dominio {codigo}: {nombre}",
            profundidad=3
        )

        html += f"""
<h1>{escape(nombre)}</h1>

<div class="codigo">
Valor de dominio · {escape(codigo)}
</div>
"""

        if observacion:
            html += f"""
<h2>Observación de la fuente</h2>

<p>{escape(observacion)}</p>
"""

        html += f"""
<h2>Descripción en el catálogo</h2>

<dl>

<dt>Valor de dominio de</dt>

<dd>
{enlace(
    atributo,
    f"{codigo_atributo} — {nombre_atributo}"
)}
</dd>

</dl>

<h2>Identificador persistente</h2>

<p><code>{escape(str(dominio))}</code></p>
"""

        html += fin_html()

        salida = (
            RAIZ
            / "dominio"
            / atributo_ruta
            / codigo_ruta
            / "index.html"
        )

        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(html, encoding="utf-8")

    return len(dominios)


# ============================================================
# CLASES OWL IMPLEMENTABLES
# ============================================================

def generar_features():

    features = sorted(
        set(g.subjects(RDF.type, URIRef(
            "http://www.w3.org/2002/07/owl#Class"
        ))),
        key=lambda x: codigo_iri(x)
    )

    # Solo clases pertenecientes al namespace /feature/
    features = [
        f for f in features
        if str(f).startswith(BASE + "feature/")
    ]

    for feature in features:

        codigo = codigo_iri(feature)
        nombre = valor(feature, RDFS.label)

        superclase = g.value(
            feature,
            RDFS.subClassOf
        )

        og = g.value(
            feature,
            IDERA.implementaObjetoGeografico
        )

        codigo_og = valor(og, IDERA.codigo)
        nombre_og = valor(og, RDFS.label)

        html = inicio_html(
            nombre,
            f"Clase OWL implementable {codigo}: {nombre}"
        )

        html += f"""
<h1>{escape(nombre)}</h1>

<div class="codigo">
Clase OWL implementable · {escape(codigo)}
</div>

<h2>Descripción semántica</h2>

<dl>

<dt>Tipo RDF</dt>
<dd>owl:Class</dd>

<dt>Subclase de</dt>
<dd>
<a href="{escape(str(superclase))}">
{escape(str(superclase))}
</a>
</dd>

<dt>Implementa el Objeto Geográfico</dt>
<dd>
{enlace(
    og,
    f"{codigo_og} — {nombre_og}"
)}
</dd>

</dl>

<h2>Identificador persistente</h2>

<p><code>{escape(str(feature))}</code></p>
"""

        html += fin_html()

        salida = (
            RAIZ
            / "feature"
            / codigo
            / "index.html"
        )

        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(html, encoding="utf-8")

    return len(features)


# ============================================================
# PROPIEDADES OWL IMPLEMENTABLES
# ============================================================

def generar_properties():

    datatype_property = URIRef(
        "http://www.w3.org/2002/07/owl#DatatypeProperty"
    )

    properties = sorted(
        set(g.subjects(RDF.type, datatype_property)),
        key=lambda x: codigo_iri(x)
    )

    # Solo propiedades pertenecientes al namespace /property/
    properties = [
        p for p in properties
        if str(p).startswith(BASE + "property/")
    ]

    for propiedad in properties:

        codigo = codigo_iri(propiedad)
        nombre = valor(propiedad, RDFS.label)

        atributo = g.value(
            propiedad,
            IDERA.implementaAtributo
        )

        codigo_atributo = valor(
            atributo,
            IDERA.codigo
        )

        if not codigo_atributo:
            codigo_atributo = codigo_iri(atributo)

        nombre_atributo = valor(
            atributo,
            RDFS.label
        )

        html = inicio_html(
            nombre,
            f"Propiedad OWL implementable {codigo}: {nombre}"
        )

        html += f"""
<h1>{escape(nombre)}</h1>

<div class="codigo">
Propiedad OWL implementable · {escape(codigo)}
</div>

<h2>Descripción semántica</h2>

<dl>

<dt>Tipo RDF</dt>
<dd>owl:DatatypeProperty</dd>

<dt>Implementa el atributo</dt>
<dd>
{enlace(
    atributo,
    f"{codigo_atributo} — {nombre_atributo}"
)}
</dd>

</dl>

<h2>Identificador persistente</h2>

<p><code>{escape(str(propiedad))}</code></p>
"""

        html += fin_html()

        salida = (
            RAIZ
            / "property"
            / codigo
            / "index.html"
        )

        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(html, encoding="utf-8")

    return len(properties)

# ============================================================
# TÉRMINOS ESTRUCTURALES DE LA ONTOLOGÍA
# ============================================================

def generar_terminos_ontologia():

    OWL = Namespace("http://www.w3.org/2002/07/owl#")

    familias = (
        "clase/",
        "subclase/",
        "og/",
        "atributo/",
        "dominio/",
        "feature/",
        "property/"
    )

    # Todos los IRIs internos utilizados en el grafo
    internos = set()

    for s, p, o in g:
        for termino in (s, p, o):
            if (
                isinstance(termino, URIRef)
                and str(termino).startswith(BASE)
            ):
                internos.add(termino)

    # Excluir:
    # - IRI raíz de la ontología
    # - las siete familias que ya tienen páginas
    terminos = []

    for termino in internos:

        iri = str(termino)

        if iri == BASE:
            continue

        relativo = iri[len(BASE):]

        if relativo.startswith(familias):
            continue

        terminos.append(termino)

    terminos = sorted(
        terminos,
        key=lambda x: str(x)
    )

    for termino in terminos:

        identificador = str(termino)[len(BASE):].strip("/")

        etiqueta = valor(
            termino,
            RDFS.label
        )

        comentario = valor(
            termino,
            RDFS.comment
        )

        tipos = sorted(
            set(g.objects(termino, RDF.type)),
            key=lambda x: str(x)
        )

        dominios = sorted(
            set(g.objects(termino, RDFS.domain)),
            key=lambda x: str(x)
        )

        rangos = sorted(
            set(g.objects(termino, RDFS.range)),
            key=lambda x: str(x)
        )

        inversas = sorted(
            set(g.objects(termino, OWL.inverseOf)),
            key=lambda x: str(x)
        )

        titulo = etiqueta if etiqueta else identificador

        html = inicio_html(
            titulo,
            f"Término de la ontología: {titulo}",
            profundidad=1
        )

        html += f"""
<h1>{escape(titulo)}</h1>

<div class="codigo">
Término de la ontología
</div>
"""

        if comentario:
            html += f"""
<h2>Descripción</h2>

<p>{escape(comentario)}</p>
"""

        html += """
<h2>Descripción semántica</h2>

<dl>
"""

        if tipos:

            html += "<dt>Tipo RDF</dt>\n"

            for tipo in tipos:
                html += (
                    "<dd>"
                    f'<a href="{escape(str(tipo))}">'
                    f'{escape(str(tipo))}'
                    "</a>"
                    "</dd>\n"
                )

        if dominios:

            html += "<dt>Dominio</dt>\n"

            for dominio in dominios:
                etiqueta_dominio = valor(
                    dominio,
                    RDFS.label
                )

                texto = (
                    etiqueta_dominio
                    if etiqueta_dominio
                    else str(dominio)
                )

                html += (
                    "<dd>"
                    + enlace(dominio, texto)
                    + "</dd>\n"
                )

        if rangos:

            html += "<dt>Rango</dt>\n"

            for rango in rangos:
                etiqueta_rango = valor(
                    rango,
                    RDFS.label
                )

                texto = (
                    etiqueta_rango
                    if etiqueta_rango
                    else str(rango)
                )

                html += (
                    "<dd>"
                    + enlace(rango, texto)
                    + "</dd>\n"
                )

        if inversas:

            html += "<dt>Propiedad inversa</dt>\n"

            for inversa in inversas:
                etiqueta_inversa = valor(
                    inversa,
                    RDFS.label
                )

                texto = (
                    etiqueta_inversa
                    if etiqueta_inversa
                    else str(inversa)
                )

                html += (
                    "<dd>"
                    + enlace(inversa, texto)
                    + "</dd>\n"
                )

        html += f"""
</dl>

<h2>Identificador persistente</h2>

<p><code>{escape(str(termino))}</code></p>
"""

        html += fin_html()

        salida = (
            RAIZ
            / identificador
            / "index.html"
        )

        salida.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        salida.write_text(
            html,
            encoding="utf-8"
        )

    return len(terminos)

# ============================================================
# Ejecutar
# ============================================================

print()
print("Generando páginas semánticas...")

n_clases = generar_clases()
n_subclases = generar_subclases()
n_objetos = generar_objetos()
n_atributos = generar_atributos()
n_dominios = generar_dominios()
n_features = generar_features()
n_properties = generar_properties()
n_terminos = generar_terminos_ontologia()

total = (
    n_clases
    + n_subclases
    + n_objetos
    + n_atributos
    + n_dominios
    + n_features
    + n_properties
    + n_terminos
)

print()
print("========================================")
print("GENERACIÓN COMPLETADA")
print("========================================")
print(f"Clases:              {n_clases}")
print(f"Subclases:           {n_subclases}")
print(f"Objetos geográficos: {n_objetos}")
print(f"Atributos:           {n_atributos}")
print(f"Valores de dominio:  {n_dominios}")
print(f"Clases OWL:          {n_features}")
print(f"Propiedades OWL:     {n_properties}")
print(f"Términos ontológicos: {n_terminos}")
print("----------------------------------------")
print(f"Total de páginas:    {total}")
print("========================================")