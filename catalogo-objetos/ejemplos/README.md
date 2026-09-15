# Ejemplos de uso del Catálogo de Objetos Geográficos de IDERA V2.2

Este directorio contiene ejemplos ejecutables en RDF/Turtle para mostrar
cómo utilizar la ontología del Catálogo de Objetos Geográficos de IDERA V2.2
con datos geoespaciales concretos.

Los ejemplos se mantienen separados de la ontología principal y no forman
parte del contenido normativo del Catálogo IDERA.

## Archivos

### 01-parcela.ttl

Ejemplo básico de una instancia concreta del Objeto Geográfico **Parcela**
(código IDERA `110101`).

La instancia se declara mediante:

`rdf:type → feature/110101`

Esto permite que el identificador físico de la entidad sea independiente
del nombre utilizado por el Catálogo IDERA.

---

### 02-mapeo-atributo-local.ttl

Demuestra cómo una fuente puede conservar sus propios nombres de propiedades.

Por ejemplo:

`ex:superficie → idera:correspondeAtributo → atributo/ARA`

No es necesario que el productor renombre físicamente su propiedad como
`property/ARA`.

---

### 03-parcela-cobertura-parcial.ttl

Ejemplo destinado a analizar la **cobertura semántica**.

Parcela posee seis atributos asociados en el Catálogo IDERA:

- CCA
- PDA
- TPA
- ARA
- NMP
- SAG

La instancia del ejemplo implementa solamente dos de ellos mediante
propiedades locales mapeadas semánticamente.

Por lo tanto:

- atributos catalogados: 6
- atributos implementados: 2
- atributos no implementados: 4
- cobertura: 33,3 %

La ausencia de los restantes atributos no implica por sí misma una
violación SHACL, ya que la asociación de un atributo con un Objeto
Geográfico no establece automáticamente su obligatoriedad.

---

### 04-shacl-conforme.ttl

Ejemplo de una instancia cuyos valores satisfacen las restricciones
de tipo de dato utilizadas por el módulo SHACL de conformidad.

También demuestra que una propiedad local puede ser validada mediante
su correspondencia semántica con un atributo IDERA.

---

### 05-shacl-no-conforme.ttl

Ejemplo deliberadamente no conforme.

La propiedad local está correctamente asociada con un atributo IDERA,
pero el valor proporcionado no pertenece a la familia de tipos de datos
esperada para ese atributo.

Permite comprobar que:

**correspondencia semántica correcta ≠ valor necesariamente válido**

---

### 06-geometria-compatible.ttl

Ejemplo de una Parcela representada mediante una geometría `POLYGON`.

El módulo SHACL geométrico puede relacionar:

`instancia → clase implementable → Objeto Geográfico → tipo geométrico`

y comprobar la compatibilidad con la geometría GeoSPARQL utilizada.

---

### 07-geometria-incompatible.ttl

Ejemplo deliberadamente incompatible desde el punto de vista geométrico.

La instancia pertenece a la clase implementable correspondiente a
**Parcela**, cuyo tipo geométrico catalogado es Polígono, pero utiliza
una geometría `POINT`.

Este ejemplo permite provocar y estudiar una incompatibilidad mediante
el módulo SHACL geométrico.

## Conformidad y cobertura

Los ejemplos distinguen dos conceptos diferentes:

**Conformidad**

Evalúa si los datos presentes satisfacen las restricciones explícitamente
modeladas mediante SHACL.

**Cobertura**

Evalúa qué proporción de los atributos asociados a un Objeto Geográfico
del Catálogo IDERA está efectivamente representada por una fuente de datos.

Por ello, una instancia puede ser **conforme** y, al mismo tiempo, presentar
una **cobertura parcial** del Catálogo.

## Consultas SPARQL

El subdirectorio `consultas/` contiene consultas SPARQL destinadas a
analizar los ejemplos en un repositorio RDF como GraphDB.

```text
consultas/
├── verificar-conformidad.rq
└── calcular-cobertura.rq
```

## Validación SHACL

El proyecto utiliza dos módulos de validación:

- `catalogo-idera-shacl.ttl`: validación de conformidad semántica y de tipos de datos.
- `catalogo-idera-shacl-geometria.ttl`: validación opcional de compatibilidad geométrica.

`catalogo-idera-shacl.ttl` es el módulo oficial de conformidad del proyecto.
La misma versión se utiliza tanto en **GraphDB** como en **pySHACL**; ya no
existe una versión “portable” separada.

### Opción A — GraphDB

Cargar los recursos principales de la siguiente manera:

| Archivo | Named Graph |
|---|---|
| `catalogo-idera.ttl` | `https://cdg-idera.github.io/ontologias/catalogo-objetos/graph/catalogo` |
| `catalogo-idera-shacl.ttl` | `http://rdf4j.org/schema/rdf4j#SHACLShapeGraph` |
| `catalogo-idera-shacl-geometria.ttl` | `http://rdf4j.org/schema/rdf4j#SHACLShapeGraph` |

Los ejemplos pueden cargarse en:

`https://cdg-idera.github.io/ontologias/catalogo-objetos/graph/datos-evaluacion`

Pruebas verificadas:

- `04-shacl-conforme.ttl` → importación aceptada.
- `05-shacl-no-conforme.ttl` → importación rechazada por SHACL.
- `06-geometria-compatible.ttl` → geometría aceptada.
- `07-geometria-incompatible.ttl` → geometría rechazada por SHACL.

En particular, la prueba del ejemplo `05` confirmó que el módulo de
conformidad obtiene el tipo esperado desde la propia ontología mediante
`idera:tipoAtributo`, sin depender de cláusulas `VALUES`.

Cuando GraphDB rechaza una transacción por SHACL, el informe de validación
puede mostrarse como parte del error de importación sin que necesariamente
quede persistido como datos consultables en el repositorio.

### Opción B — Python / pySHACL

Instalar las dependencias:

```bash
pip install rdflib pyshacl
```

El script `validar.py` utiliza:

```text
../catalogo-idera.ttl
../catalogo-idera-shacl.ttl
../catalogo-idera-shacl-geometria.ttl
```

Para la validación local, el script combina la ontología y los datos del
ejemplo en el grafo de datos utilizado por pySHACL y carga por separado
los módulos SHACL.

Ejemplos:

```bash
python validar.py 04-shacl-conforme.ttl
python validar.py 05-shacl-no-conforme.ttl
python validar.py 06-geometria-compatible.ttl
python validar.py 07-geometria-incompatible.ttl
```

Resultados verificados:

```text
04-shacl-conforme.ttl        → CONFORME
05-shacl-no-conforme.ttl     → NO CONFORME
06-geometria-compatible.ttl  → CONFORME
07-geometria-incompatible.ttl → NO CONFORME
```

Para visualizar el informe completo de pySHACL:

```bash
python validar.py 05-shacl-no-conforme.ttl --verbose
```

De esta forma, las mismas reglas de conformidad pueden ejecutarse tanto
en un repositorio GraphDB como en un entorno Python independiente.

## Recursos relacionados

Ontología principal:

`../catalogo-idera.ttl`

SHACL de conformidad:

`../catalogo-idera-shacl.ttl`

SHACL geométrico:

`../catalogo-idera-shacl-geometria.ttl`

## Nota metodológica

Los ejemplos son recursos demostrativos de implementación.

Las decisiones introducidas para facilitar validación, mapeo semántico
o evaluación de cobertura no deben interpretarse como requisitos
adicionales establecidos por el Catálogo de Objetos Geográficos de
IDERA V2.2.
