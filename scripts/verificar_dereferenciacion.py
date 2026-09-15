from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote

from rdflib import Graph, URIRef


BASE = "https://cdg-idera.github.io/ontologias/catalogo-objetos/"
TTL = Path("catalogo-objetos/catalogo-idera.ttl")
RAIZ = Path("catalogo-objetos")


# ============================================================
# Leer ontología
# ============================================================

g = Graph()
g.parse(TTL, format="turtle")

print(f"Ontología cargada: {len(g)} triples")


# ============================================================
# Obtener todos los IRIs internos
# ============================================================

internos = set()

for s, p, o in g:
    for termino in (s, p, o):
        if (
            isinstance(termino, URIRef)
            and str(termino).startswith(BASE)
        ):
            internos.add(str(termino))


# El IRI raíz ya corresponde a la página principal
recursos = sorted(
    iri for iri in internos
    if iri != BASE
)


# ============================================================
# Convertir IRI a página local
# ============================================================

def ruta_html(iri):

    relativo = iri[len(BASE):].strip("/")
    relativo = unquote(relativo)

    return RAIZ / Path(relativo) / "index.html"


# ============================================================
# Verificar páginas
# ============================================================

con_pagina = []
sin_pagina = []

for iri in recursos:

    ruta = ruta_html(iri)

    if ruta.exists():
        con_pagina.append((iri, ruta))
    else:
        sin_pagina.append((iri, ruta))


# ============================================================
# Analizador de enlaces HTML
# ============================================================

class AnalizadorEnlaces(HTMLParser):

    def __init__(self):
        super().__init__()
        self.enlaces = []

    def handle_starttag(self, tag, attrs):

        if tag != "a":
            return

        for nombre, valor in attrs:
            if nombre == "href" and valor:
                self.enlaces.append(valor)


# ============================================================
# Verificar enlaces internos
# ============================================================

enlaces_revisados = 0
enlaces_rotos = []

for iri, pagina in con_pagina:

    parser = AnalizadorEnlaces()

    try:
        contenido = pagina.read_text(encoding="utf-8")
        parser.feed(contenido)

    except Exception as e:
        enlaces_rotos.append(
            (pagina, f"ERROR HTML: {e}")
        )
        continue

    for href in parser.enlaces:

        # Solo enlaces dentro de nuestro namespace
        if not href.startswith(BASE):
            continue

        # La raíz del catálogo ya existe como página principal
        if href.rstrip("/") == BASE.rstrip("/"):
            continue

        # El TTL es un archivo, no una página semántica
        if href == BASE + "catalogo-idera.ttl":
            continue

        enlaces_revisados += 1

        destino = ruta_html(href)

        if not destino.exists():
            enlaces_rotos.append(
                (pagina, href)
            )


# ============================================================
# Resultado
# ============================================================

print()
print("========================================")
print("VERIFICACIÓN FINAL DE DEREFERENCIACIÓN")
print("========================================")
print(f"IRIs internos RDF:          {len(internos)}")
print(f"Recursos a dereferenciar:   {len(recursos)}")
print(f"Con página generada:        {len(con_pagina)}")
print(f"Sin página generada:        {len(sin_pagina)}")
print(f"Enlaces internos revisados: {enlaces_revisados}")
print(f"Enlaces internos rotos:     {len(enlaces_rotos)}")
print("========================================")


if sin_pagina:

    print()
    print("RECURSOS SIN PÁGINA:")
    print()

    for iri, ruta in sin_pagina:
        print(iri)
        print(f"  -> {ruta}")


if enlaces_rotos:

    print()
    print("ENLACES INTERNOS ROTOS:")
    print()

    for origen, destino in enlaces_rotos:
        print(f"Origen:  {origen}")
        print(f"Destino: {destino}")
        print()


if not sin_pagina and not enlaces_rotos:

    print()
    print(
        "OK: todos los recursos tienen página "
        "y todos los enlaces internos comprobados resuelven localmente."
    )