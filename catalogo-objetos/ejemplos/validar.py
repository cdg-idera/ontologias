#!/usr/bin/env python3
"""
Validador local del Catálogo de Objetos Geográficos de IDERA V2.2.
No requiere GraphDB.

Uso:
    python validar.py 04-shacl-conforme.ttl
    python validar.py 05-shacl-no-conforme.ttl
    python validar.py 07-geometria-incompatible.ttl --verbose
"""

from pathlib import Path
import argparse
from rdflib import Graph, Namespace
from pyshacl import validate

SH = Namespace("http://www.w3.org/ns/shacl#")

def cargar(grafo, archivo):
    archivo = Path(archivo)
    if not archivo.exists():
        raise FileNotFoundError(f"No se encontró: {archivo}")
    grafo.parse(archivo, format="turtle")

def nombre_corto(term):
    if term is None:
        return "-"
    s = str(term)
    for sep in ("#", "/"):
        if sep in s:
            s = s.rsplit(sep, 1)[-1]
    return s or str(term)

def imprimir_resumen(report_graph):
    resultados = list(report_graph.subjects(
        predicate=None,
        object=SH.ValidationResult
    ))
    # Fallback robusto: buscar por rdf:type.
    if not resultados:
        from rdflib.namespace import RDF
        resultados = list(report_graph.subjects(RDF.type, SH.ValidationResult))

    for i, r in enumerate(resultados, 1):
        focus = report_graph.value(r, SH.focusNode)
        value = report_graph.value(r, SH.value)
        path = report_graph.value(r, SH.resultPath)
        message = report_graph.value(r, SH.resultMessage)
        source_shape = report_graph.value(r, SH.sourceShape)

        print(f"\nViolación {i}:")
        if focus is not None:
            print(f"  Instancia: {nombre_corto(focus)}")
        if path is not None:
            print(f"  Propiedad: {nombre_corto(path)}")
        if value is not None and value != focus:
            print(f"  Valor:     {value}")
        if source_shape is not None:
            print(f"  Shape:     {nombre_corto(source_shape)}")
        if message is not None:
            print(f"  Motivo:    {message}")

def main():
    p = argparse.ArgumentParser(description="Validador local IDERA")
    p.add_argument("datos", help="Archivo Turtle a validar")
    p.add_argument("--base", default="..",
                   help="Directorio del catálogo (por defecto: ..)")
    p.add_argument("--verbose", action="store_true",
                   help="Muestra el informe completo de pySHACL")
    args = p.parse_args()

    base = Path(args.base)
    datos_path = Path(args.datos)

    ontologia = base / "catalogo-idera.ttl"
    shacl_conformidad = base / "catalogo-idera-shacl.ttl"
    shacl_geometria = base / "catalogo-idera-shacl-geometria.ttl"

    grafo_validacion = Graph()
    shapes = Graph()

    cargar(grafo_validacion, ontologia)
    triples_ontologia = len(grafo_validacion)
    cargar(grafo_validacion, datos_path)
    triples_total = len(grafo_validacion)

    cargar(shapes, shacl_conformidad)
    cargar(shapes, shacl_geometria)

    conforms, report_graph, report_text = validate(
        data_graph=grafo_validacion,
        shacl_graph=shapes,
        inference="rdfs",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
        meta_shacl=False,
        advanced=True,
        inplace=False,
    )

    print(f"\nValidando: {datos_path.name}")
    print("=" * 52)
    print("RESULTADO:", "CONFORME" if conforms else "NO CONFORME")
    print("=" * 52)

    if conforms:
        print("El archivo satisface las restricciones SHACL aplicables.")
    else:
        imprimir_resumen(report_graph)

    if args.verbose:
        print("\n--- Informe completo de pySHACL ---")
        print(report_text)

    raise SystemExit(0 if conforms else 1)

if __name__ == "__main__":
    main()
