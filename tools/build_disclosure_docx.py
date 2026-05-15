#!/usr/bin/env python3
"""
One-step builder: render editable-source drawings, fill the DOCX template, and
optionally bundle drawing source files.

Usage:
  python3 tools/build_disclosure_docx.py \
    --template 专利交底书模板.docx \
    --payload payload.json \
    --output 案件名称-专利交底书.docx \
    --drawings-dir drawings \
    --zip-drawing-sources 案件名称-附图源文件.zip
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fill_disclosure_template import fill_document
from render_disclosure_drawings import ensure_drawings, zip_drawing_sources


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", required=True, help="Path to 专利交底书模板.docx")
    parser.add_argument("--payload", required=True, help="Input payload JSON")
    parser.add_argument("--output", required=True, help="Output DOCX path")
    parser.add_argument("--drawings-dir", default="drawings", help="Directory for generated DOT/SVG/PNG drawings")
    parser.add_argument("--updated-payload", help="Optional path for payload updated with generated drawing paths")
    parser.add_argument("--zip-drawing-sources", help="Optional ZIP path for DOT/SVG/PNG drawing source bundle")
    parser.add_argument("--dpi", type=int, default=260, help="PNG rendering DPI, default 260")
    args = parser.parse_args()

    template_path = Path(args.template).expanduser().resolve()
    payload_path = Path(args.payload).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    drawings_dir = Path(args.drawings_dir).expanduser().resolve()

    with payload_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    payload.setdefault("_base_dir", str(payload_path.parent))

    payload = ensure_drawings(payload, drawings_dir, dpi=args.dpi)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fill_document(template_path, payload, output_path)
    print(f"Wrote DOCX: {output_path}")

    if args.updated_payload:
        updated_payload_path = Path(args.updated_payload).expanduser().resolve()
        updated_payload_path.parent.mkdir(parents=True, exist_ok=True)
        with updated_payload_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"Wrote updated payload: {updated_payload_path}")

    if args.zip_drawing_sources:
        zip_path = Path(args.zip_drawing_sources).expanduser().resolve()
        zip_drawing_sources(payload, zip_path)
        if zip_path.exists():
            print(f"Wrote drawing sources: {zip_path}")


if __name__ == "__main__":
    main()
