#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_app.py — pipeline reproducible: CSV Koha -> app HTML autónoma.

    python build_app.py

Pasos:
  1. Convierte el CSV con koha_to_json.py (genera biblioteca.json).
  2. Recorta a las claves cortas que usa el front y minifica (catalog.min.json).
  3. Inyecta el catálogo en app_template.html -> biblioteca-estanteria.html.

Para datos vivos en un servidor: en vez de embeber, serví biblioteca.json
y cambiá la línea DATA del template por un fetch (ver comentario en el HTML).
"""
import json, subprocess, sys
from pathlib import Path

import sys
# Ruta del CSV: 1er argumento, o el nombre por defecto en el directorio actual.
CSV = sys.argv[1] if len(sys.argv) > 1 else "16-test_export-reportresults.csv"

def trim(b):
    o = {"id": b["id"], "t": b["title"], "col": b["color"]}
    a = b.get("authorMain") or b.get("authorCorporate")
    for k, v in (("bn", b.get("biblionumber")), ("st", b.get("subtitle")), ("a", a),
                 ("aa", b.get("authorsAdditionalRaw")), ("y", b.get("year")),
                 ("p", b.get("pages")), ("i", b.get("isbn")),
                 ("c", b.get("callNumber")), ("sm", b.get("shelfmark")),
                 ("se", b.get("series")), ("u", b.get("resourceUrl")),
                 ("s", b.get("subjects"))):
        if v:
            o[k] = v
    return o

def main():
    subprocess.run([sys.executable, "koha_to_json.py", CSV, "biblioteca.json"], check=True)
    full = json.loads(Path("biblioteca.json").read_text(encoding="utf-8"))
    mini = {"sections": [{"section": s["section"], "count": s["count"],
                          "books": [trim(b) for b in s["books"]]} for s in full["sections"]]}
    blob = json.dumps(mini, ensure_ascii=False, separators=(",", ":"))
    if "</script>" in blob:
        raise SystemExit("El catálogo contiene '</script>' y rompería el embed.")
    tpl = Path("app_template.html").read_text(encoding="utf-8")
    Path("biblioteca-estanteria.html").write_text(
        tpl.replace("__CATALOG_JSON__", blob), encoding="utf-8")
    n = sum(s["count"] for s in mini["sections"])
    print(f"OK · {n} libros embebidos -> biblioteca-estanteria.html")

if __name__ == "__main__":
    main()
