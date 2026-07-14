import adsk.core
import adsk.fusion
import json
import os
import re
import traceback


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CAD_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))
OUTPUT_DIR = os.path.join(CAD_DIR, "reference")


def _mm(value_cm):
    """Fusion stores API lengths in centimetres; reports are easier to use in mm."""
    return round(float(value_cm) * 10.0, 4)


def _point_mm(point):
    return {
        "x": _mm(point.x),
        "y": _mm(point.y),
        "z": _mm(point.z),
    }


def _bounding_box_mm(box):
    if not box:
        return None

    minimum = _point_mm(box.minPoint)
    maximum = _point_mm(box.maxPoint)
    return {
        "min_mm": minimum,
        "max_mm": maximum,
        "size_mm": {
            "x": round(maximum["x"] - minimum["x"], 4),
            "y": round(maximum["y"] - minimum["y"], 4),
            "z": round(maximum["z"] - minimum["z"], 4),
        },
    }


def _body_record(body, body_type):
    record = {
        "type": body_type,
        "name": body.name,
        "visible": bool(body.isVisible),
        "bounding_box": _bounding_box_mm(body.boundingBox),
    }

    if body_type == "brep":
        record["solid"] = bool(body.isSolid)
        record["faces"] = int(body.faces.count)
        record["edges"] = int(body.edges.count)
    return record


def _component_record(component, path):
    bodies = []
    for index in range(component.bRepBodies.count):
        bodies.append(_body_record(component.bRepBodies.item(index), "brep"))
    for index in range(component.meshBodies.count):
        bodies.append(_body_record(component.meshBodies.item(index), "mesh"))

    return {
        "path": path,
        "name": component.name,
        "bodies": bodies,
        "occurrence_count": int(component.occurrences.count),
    }


def _walk_component(component, path, component_records, occurrence_records):
    component_records.append(_component_record(component, path))

    for index in range(component.occurrences.count):
        occurrence = component.occurrences.item(index)
        occurrence_path = path + "/" + occurrence.name
        occurrence_records.append({
            "path": occurrence_path,
            "name": occurrence.name,
            "component_name": occurrence.component.name,
            "visible": bool(occurrence.isLightBulbOn),
            "bounding_box": _bounding_box_mm(occurrence.boundingBox),
        })
        _walk_component(
            occurrence.component,
            occurrence_path,
            component_records,
            occurrence_records,
        )


def _safe_filename(value):
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return clean or "fusion_design"


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design or not app.activeDocument:
            ui.messageBox("Apri prima un progetto Fusion Design da ispezionare.")
            return

        components = []
        occurrences = []
        _walk_component(design.rootComponent, design.rootComponent.name, components, occurrences)

        document_name = app.activeDocument.name
        report = {
            "document": document_name,
            "units": "mm",
            "read_only_inspection": True,
            "components": components,
            "occurrences": occurrences,
        }

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(
            OUTPUT_DIR,
            "inspection_" + _safe_filename(document_name) + ".json",
        )
        with open(output_path, "w", encoding="utf-8") as output_file:
            json.dump(report, output_file, ensure_ascii=False, indent=2)

        body_lines = []
        for component in components:
            for body in component["bodies"]:
                size = body.get("bounding_box", {}).get("size_mm", {})
                body_lines.append(
                    "- {0}: {1} x {2} x {3} mm ({4})".format(
                        body["name"],
                        size.get("x", "?"),
                        size.get("y", "?"),
                        size.get("z", "?"),
                        body["type"],
                    )
                )

        summary = "Ispezione completata senza modificare il modello.\n\n"
        summary += "Documento: " + document_name + "\n"
        summary += "File: " + output_path + "\n\n"
        summary += "\n".join(body_lines[:12]) if body_lines else "Nessun corpo trovato."
        ui.messageBox(summary)
    except Exception:
        ui.messageBox("Errore durante l'ispezione:\n" + traceback.format_exc())
