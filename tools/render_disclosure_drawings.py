#!/usr/bin/env python3
"""
Render patent disclosure drawings from payload JSON.

The tool keeps drawings editable by saving source files next to rendered images:
- Graphviz DOT source: .dot
- Vector output: .svg
- Word-compatible high-resolution output: .png

Typical usage:
  python3 tools/render_disclosure_drawings.py \
    --payload payload.json \
    --out-dir drawings \
    --update-payload payload.with_drawings.json

Supported drawing items in payload["drawings"]:
  1) {"no":"图1", "title":"...", "dot":"digraph G {...}"}
  2) {"no":"图1", "title":"...", "nodes":[...], "edges":[...]}
  3) {"no":"图1", "title":"...", "path":"existing.png"}

For maximum Word compatibility, the DOCX filler inserts PNG. The SVG and DOT
files are delivered together as editable/vector source files.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

DEFAULT_FONT = "Noto Sans CJK SC"


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()


def sanitize_filename(name: str, fallback: str) -> str:
    name = clean_text(name) or fallback
    name = re.sub(r"[\\/:*?\"<>|\s]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("._")
    return name or fallback


def q(s: str) -> str:
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


def edge_tuple(edge: Any) -> Tuple[str, str, str]:
    if isinstance(edge, dict):
        return clean_text(edge.get("from")), clean_text(edge.get("to")), clean_text(edge.get("label"))
    if isinstance(edge, (list, tuple)) and len(edge) >= 2:
        label = clean_text(edge[2]) if len(edge) > 2 else ""
        return clean_text(edge[0]), clean_text(edge[1]), label
    raise ValueError(f"Invalid edge spec: {edge!r}")


def dot_from_nodes_edges(drawing: Dict[str, Any]) -> str:
    title = clean_text(drawing.get("title")) or "附图"
    graph_name = sanitize_filename(clean_text(drawing.get("no")) or "G", "G")
    nodes = list(drawing.get("nodes") or [])
    edges = list(drawing.get("edges") or [])
    lines: List[str] = [
        f"digraph {graph_name} {{",
        "  graph [rankdir=TB, splines=ortho, nodesep=0.55, ranksep=0.65, dpi=220, labelloc=t, label=" + q(title) + "];",
        f"  node [shape=box, style=\"rounded,filled\", fillcolor=\"#FFFFFF\", color=\"#444444\", penwidth=1.2, fontname={q(DEFAULT_FONT)}, fontsize=16, margin=\"0.12,0.08\"];",
        f"  edge [color=\"#444444\", arrowsize=0.8, fontname={q(DEFAULT_FONT)}, fontsize=12];",
    ]
    if nodes:
        for node in nodes:
            if isinstance(node, dict):
                node_id = sanitize_filename(clean_text(node.get("id")), f"N{len(lines)}")
                label = clean_text(node.get("label")) or node_id
            else:
                node_id = sanitize_filename(clean_text(node), f"N{len(lines)}")
                label = clean_text(node)
            lines.append(f"  {node_id} [label={q(label)}];")
    for edge in edges:
        src, dst, label = edge_tuple(edge)
        src = sanitize_filename(src, "N1")
        dst = sanitize_filename(dst, "N2")
        attrs = f" [label={q(label)}]" if label else ""
        lines.append(f"  {src} -> {dst}{attrs};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def normalize_dot(dot: str) -> str:
    dot = clean_text(dot)
    # Do not attempt full parsing; just return user DOT. The prompt should include
    # graph/node/edge font settings for Chinese rendering.
    return dot + ("\n" if dot and not dot.endswith("\n") else "")


def render_dot(dot_path: Path, svg_path: Path, png_path: Path, dpi: int = 260) -> None:
    dot_bin = shutil.which("dot")
    if not dot_bin:
        raise RuntimeError("Graphviz 'dot' was not found. DOT source was written, but SVG/PNG could not be rendered.")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([dot_bin, "-Tsvg", str(dot_path), "-o", str(svg_path)], check=True)
    # png:cairo generally renders CJK text and antialiasing better than legacy png.
    subprocess.run([dot_bin, f"-Gdpi={dpi}", "-Tpng:cairo", str(dot_path), "-o", str(png_path)], check=True)


def ensure_drawings(payload: Dict[str, Any], out_dir: Path, dpi: int = 260) -> Dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    base_dir = Path(payload.get("_base_dir") or Path.cwd())
    drawings = list(payload.get("drawings") or [])
    updated: List[Dict[str, Any]] = []

    for i, drawing in enumerate(drawings, start=1):
        d = dict(drawing or {})
        no = clean_text(d.get("no")) or f"图{i}"
        title = clean_text(d.get("title")) or "附图"
        stem = sanitize_filename(f"{no}_{title}", f"图{i}")
        existing_path = clean_text(d.get("path"))
        if existing_path:
            p = Path(existing_path)
            if not p.is_absolute():
                p = base_dir / p
            if p.exists():
                d["path"] = str(p.resolve())
                updated.append(d)
                continue

        dot_text = clean_text(d.get("dot"))
        if not dot_text and (d.get("nodes") or d.get("edges")):
            dot_text = dot_from_nodes_edges(d)
        elif dot_text:
            dot_text = normalize_dot(dot_text)

        if dot_text:
            dot_path = out_dir / f"{stem}.dot"
            svg_path = out_dir / f"{stem}.svg"
            png_path = out_dir / f"{stem}.png"
            dot_path.write_text(dot_text, encoding="utf-8")
            try:
                render_dot(dot_path, svg_path, png_path, dpi=dpi)
                d["path"] = str(png_path.resolve())
                d["png_path"] = str(png_path.resolve())
                d["svg_path"] = str(svg_path.resolve())
                d["source_path"] = str(dot_path.resolve())
            except Exception as exc:
                d["source_path"] = str(dot_path.resolve())
                d["render_error"] = str(exc)
            updated.append(d)
            continue

        # No source and no valid image path. Keep the item; the filler will insert the caption text only.
        updated.append(d)

    payload["drawings"] = updated
    if not clean_text(payload.get("representative_figure")):
        for d in updated:
            if clean_text(d.get("path")):
                payload["representative_figure"] = clean_text(d.get("path"))
                break
    return payload


def zip_drawing_sources(payload: Dict[str, Any], zip_path: Path) -> None:
    candidates: List[Path] = []
    for d in payload.get("drawings") or []:
        for key in ("source_path", "svg_path", "png_path", "path"):
            value = clean_text(d.get(key))
            if value:
                p = Path(value)
                if p.exists() and p not in candidates:
                    candidates.append(p)
    if not candidates:
        return
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in candidates:
            zf.write(p, arcname=p.name)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", required=True, help="Input payload JSON")
    parser.add_argument("--out-dir", required=True, help="Directory for generated DOT/SVG/PNG drawings")
    parser.add_argument("--update-payload", help="Write payload JSON updated with generated image/source paths")
    parser.add_argument("--dpi", type=int, default=260, help="PNG rendering DPI, default 260")
    parser.add_argument("--zip-sources", help="Optional ZIP path for DOT/SVG/PNG drawing sources")
    args = parser.parse_args()

    payload_path = Path(args.payload).expanduser().resolve()
    with payload_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    payload.setdefault("_base_dir", str(payload_path.parent))

    updated = ensure_drawings(payload, Path(args.out_dir).expanduser().resolve(), dpi=args.dpi)

    if args.update_payload:
        out_payload = Path(args.update_payload).expanduser().resolve()
        out_payload.parent.mkdir(parents=True, exist_ok=True)
        with out_payload.open("w", encoding="utf-8") as f:
            json.dump(updated, f, ensure_ascii=False, indent=2)
        print(f"Wrote updated payload: {out_payload}")

    if args.zip_sources:
        zip_path = Path(args.zip_sources).expanduser().resolve()
        zip_drawing_sources(updated, zip_path)
        if zip_path.exists():
            print(f"Wrote drawing sources: {zip_path}")


if __name__ == "__main__":
    main()
