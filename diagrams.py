# Generated inline SVG diagrams. Edit diagrams.json to maintain the figures.
import json
from pathlib import Path

DIAGRAMS = json.loads(Path(__file__).with_name("diagrams.json").read_text(encoding="utf-8"))

def diagram_for(slug, section):
    return DIAGRAMS.get(f"{slug}:{section}", "")
