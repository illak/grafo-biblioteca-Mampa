# 📚 Biblioteca Física Mampa — Grafo interactivo de la colección

Visualización interactiva del catálogo de la **Biblioteca Física Mampa** (ISEP, Córdoba, Argentina): un grafo que conecta cada libro con sus autores, palabras clave, áreas geográficas y colecciones, y que permite explorar la colección navegándola como un universo.

El proyecto incluye **dos visualizaciones complementarias**, ambas como archivos HTML autocontenidos (los datos van embebidos, no hay backend):

| Archivo | Descripción |
|---|---|
| `grafo_biblioteca_mampa.html` | **Versión 2D** (D3.js). Funciona 100 % offline. Vista de análisis y exploración clásica. |
| `grafo_biblioteca_mampa_3d.html` | **Versión 3D** (Three.js). Experiencia inmersiva: el usuario puede "meterse" dentro del grafo y recorrerlo como un espacio. Requiere internet solo para cargar las librerías desde CDN. |

<!-- 📸 sugerencia: agregar capturas aquí -->
<!-- ![Vista 2D](docs/captura-2d.png) -->
<!-- ![Vista 3D](docs/captura-3d.png) -->

---

## ✨ Qué se puede hacer

- **Explorar por facetas**: los libros (📖) se conectan a 4 tipos de nodos — autores, palabras clave, áreas geográficas y colecciones — cada uno con su color. Los filtros permiten encender/apagar cada tipo de relación.
- **Foco por vecindario**: clic en cualquier nodo muestra su "subuniverso" (vecinos a 1, 2 o 3 saltos) y un panel de detalle con sus conexiones.
- **Enlace al catálogo**: cada libro enlaza a su ficha en el OPAC de Koha (`opac-detail.pl?biblionumber=N`).
- **Búsqueda** por título, autor, tema o colección, y **Top 10** por categoría.
- **Control de densidad**: la vista general puede ocultar nodos de faceta con pocos libros (≥1 / ≥2 / ≥3) para reducir el ruido visual sin perder datos — los nodos ocultos siguen accesibles por búsqueda y foco.

### Exclusivo de la versión 3D

- **Navegación inmersiva**: el zoom "atraviesa" el grafo (al llegar al límite, el pivote cede hacia adelante y se penetra la escena), doble clic/tap avanza hacia donde se apunta, y el arrastre rota la cámara sobre su propio eje (mirar alrededor, estilo primera persona). Botón **⌂ Recentrar** para volver a la vista completa.
- **✦ Tour automático**: recorrido con vuelos de cámara entre nodos destacados, intercalando aleatoriamente autores, temas, áreas y colecciones. Si se inicia dentro de un subuniverso, el tour se limita a él.
- **Placa de contexto**: al enfocar un nodo, una placa indica qué subuniverso se está explorando.
- **Etiquetas con nivel de detalle (LOD)**: al alejarse solo se etiquetan los nodos importantes; al acercarse aparecen los menores y, muy de cerca, los títulos de los libros.
- **Interfaz pensada para móvil**: la barra de controles se oculta/muestra a demanda (botón ☰) y arranca oculta en pantallas táctiles para apreciar el grafo completo.

---

## 🔧 Cómo se generan los datos

Los datos **no se consultan en tiempo de ejecución**: un pipeline los transforma desde Koha hasta quedar embebidos en el HTML.

```
Koha (MySQL / MARC XML)
   │  reporte SQL (scripts/koha_export_mampa.sql)
   ▼
Export a Excel (hoja "new", nivel ejemplar)
   │  script Python con pandas (scripts/build_graph.py)
   ▼
graph_data.json  (~885 KB, claves compactas)
   │  ensamblador (scripts/assemble*.py) reemplaza __DATA__ y __ENGINE__
   ▼
HTML autocontenido
```

1. **Reporte SQL en Koha**: extrae los metadatos del MARC XML con `ExtractValue()`. Detalle importante para quien trabaje con Koha: cuando un campo MARC es repetible (700 autores adicionales, 650 temas, etc.), `ExtractValue` con un XPath múltiple devuelve los valores **pegados con un espacio**. El reporte usa predicados posicionales (`[1]`, `[2]`, …) combinados con `CONCAT_WS(' | ', NULLIF(...), ...)` para obtenerlos separados por `|`. Este catálogo además usa `650$b` (en lugar del estándar `$a`) para los temas.
2. **Script de construcción** (`pandas`): deduplica por `biblionumber` (el export viene a nivel ejemplar), separa los campos multivalor por `|`, limpia puntuación de catalogación, y arma nodos (con grado y color por tipo) y aristas libro→faceta. Salida: `graph_data.json` con claves cortas para minimizar peso.
3. **Ensamblador**: inyecta el JSON y el motor JS en la plantilla HTML (marcadores `__DATA__` / `__ENGINE__`). Resultado: un solo archivo distribuible, sin fetch, sin servidor.

Para actualizar la visualización cuando cambia el catálogo: correr el reporte en Koha → exportar a Excel → ejecutar los dos scripts.

### Cifras actuales del grafo

**974 libros**, 1.379 autores, 548 palabras clave, 43 áreas geográficas y 232 colecciones → **3.176 nodos y 7.136 aristas**.

---

## 📦 Librerías y tecnologías

| Herramienta | Uso |
|---|---|
| [D3.js](https://d3js.org/) v7 | Grafo 2D: simulación de fuerzas, zoom/pan, transiciones (embebida: la versión 2D es offline). |
| [3d-force-graph](https://github.com/vasturiano/3d-force-graph) | Grafo 3D: layout de fuerzas en el espacio + render WebGL. |
| [Three.js](https://threejs.org/) | Escena 3D: sprites, campo de estrellas, niebla, geometría fusionada de aristas (vía import map). |
| [three-spritetext](https://github.com/vasturiano/three-spritetext) | Etiquetas de texto en el espacio 3D. |
| Python + [pandas](https://pandas.pydata.org/) | Pipeline de datos (Excel → JSON). |
| [Koha](https://koha-community.org/) | Sistema de gestión bibliotecaria; origen de los datos (reporte SQL sobre MARC XML). |
| EB Garamond (Google Fonts) | Tipografía. |

---

## 🎯 Decisiones de diseño

**Grafo bipartito de facetas.** En lugar de conectar libros entre sí, cada libro se conecta a sus facetas. Esto hace legible *por qué* dos libros se relacionan (comparten un autor, un tema…) y convierte a las facetas en centros naturales de exploración.

**2D y 3D como piezas distintas.** El 3D gana inmersión pero pierde precisión de lectura (oclusión, distancias engañosas). Por eso conviven: la 2D es la vista de análisis; la 3D, la experiencia exploratoria — apta, por ejemplo, para una pantalla en la biblioteca con el tour corriendo.

**Estética "universo".** Fondo oscuro con nebulosas y estrellas, nodos como discos luminosos con borde definido (se descartó el *bloom*/resplandor: en pantallas chicas todo colapsaba en manchas de luz) y libros como 📖 sobre disco oscuro para que contrasten.

**Densidad como control, no como recorte.** El filtro de densidad reduce lo *visible*, nunca los datos: todo nodo sigue existiendo para la búsqueda, el foco y los paneles.

### Rendimiento (la parte técnica interesante)

El primer 3D era lento en móvil. La causa no era "el 3D" sino los **draw calls**: ~7.000 objetos dibujados por cuadro (cada arista era un objeto `THREE.Line` independiente). Optimizaciones aplicadas:

- **Aristas fusionadas**: las ~5.500 líneas se convirtieron en **un único `THREE.LineSegments`** con un buffer compartido que se sobrescribe en cada tick de la simulación → de ~5.500 draw calls a 1. El resaltado de hover usa un segundo `LineSegments` mínimo solo con las aristas del vecindario.
- **Pausa de render inactivo**: con la simulación asentada y sin interacción, el loop de render se detiene (`pauseAnimation`) y despierta con cualquier gesto → consumo ~0 en reposo.
- **Resolución adaptada**: pixel ratio limitado (1.25 móvil / 1.5 escritorio) y antialiasing desactivado en móvil.
- **Etiquetas LOD con pool LRU**: las etiquetas se crean bajo demanda según distancia e importancia, con tope de visibles simultáneas y desalojo de texturas para acotar memoria GPU.
- **Interacción sin ambigüedad**: el arrastre de nodos está deshabilitado (`enableNodeDrag(false)`) — arrastrar siempre navega la cámara; el clic viaja al nodo.

---

## 🚀 Uso

No hay build ni dependencias que instalar para *ver* las visualizaciones: abrir el HTML en un navegador.

- `grafo_biblioteca_mampa.html` funciona sin conexión.
- `grafo_biblioteca_mampa_3d.html` necesita internet para las librerías (CDN) y un navegador con WebGL.

Para **regenerar los datos** hace falta Python 3 con `pandas` y `openpyxl`:

```bash
pip install pandas openpyxl
python scripts/build_graph.py      # Excel de Koha -> graph_data.json
python scripts/assemble.py         # -> grafo_biblioteca_mampa.html (2D)
python scripts/assemble3d.py       # -> grafo_biblioteca_mampa_3d.html (3D)
```

---

## 🗂 Estructura sugerida del repositorio

```
├── grafo_biblioteca_mampa.html        # visualización 2D (autocontenida)
├── grafo_biblioteca_mampa_3d.html     # visualización 3D (universo inmersivo)
├── scripts/
│   ├── koha_export_mampa.sql          # reporte SQL para Koha
│   ├── build_graph.py                 # Excel -> graph_data.json
│   ├── assemble.py                    # ensamblador 2D
│   └── assemble3d.py                  # ensamblador 3D
└── docs/                              # capturas, notas
```

---

## 🙌 Créditos

Proyecto de visualización del catálogo de la **Biblioteca Física Mampa** — Instituto Superior de Estudios Pedagógicos (ISEP), Córdoba, Argentina. Catálogo gestionado con [Koha](https://koha-community.org/).

El código se distribuye bajo licencia MIT. Los datos del catálogo (graph_data.json) se publican bajo CC BY 4.0