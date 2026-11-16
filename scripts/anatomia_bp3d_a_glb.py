"""M9 · Anatomía REAL: convierte un subconjunto de BodyParts3D 4.0 (DBCLS; CC BY 4.0; cuerpo masculino adulto segmentado) a UN glTF con Draco para la capa Anatomy.
Fuente S-37. Reconocimiento obligatorio: «BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International».
Uso:  blender -b -P scripts/anatomia_bp3d_a_glb.py -- data/externos/bodyparts3d web/public/models/anatomy_bp3d.glb
Cada objeto se llama `FJxxxx|nombre FMA|categoria` (hueso|cartilago|organo-<grupo>) para que la web asigne cada pieza a su cadena de ajuste.
Ejes: BodyParts3D es z-arriba, frente = −y, izquierda = +x, en mm; se importa con esos ejes y se escala a metros (el exportador glTF deja y-arriba, frente = +z)."""
import collections
import re
import sys
from pathlib import Path

import bpy

carpeta, salida = Path(sys.argv[sys.argv.index("--") + 1]), sys.argv[sys.argv.index("--") + 2]
OBJ = carpeta / "obj" / "partof_BP3D_4.0_obj_99"
el = collections.defaultdict(set)
for linea in (carpeta / "partof_element_parts.txt").read_text(encoding="utf-8").splitlines()[1:]:
    _, n, e = linea.split("\t")
    el[e].add(n)

ORD = "(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)"
LR = "(left |right )?"
HUESO = [
    rf"^{LR}(clavicle|scapula|humerus|radius|ulna|hip bone|femur|patella|tibia|fibula|talus|calcaneus|cuboid bone|cuneiform bone|medial cuneiform bone|intermediate cuneiform bone|lateral cuneiform bone|scaphoid|lunate|triquetral|pisiform|trapezium|trapezoid|capitate|hamate|maxilla)$",
    r"^(sacrum|coccyx|mandible|hyoid bone|body of sternum|manubrium of sternum|xiphoid process|neurocranium|atlas|axis|navicular bone of (left|right) foot)$",
    rf"^{LR}{ORD} (rib|metacarpal bone|metatarsal bone)$", r"^" + ORD + r" (thoracic|cervical|lumbar) vertebra$",
    rf"^(proximal|middle|distal) phalanx of {LR}(thumb|index finger|middle finger|ring finger|little finger|big toe|second toe|third toe|fourth toe|little toe)$",
]
CARTILAGO = [rf"^{LR}{ORD} costal cartilage$"]
ORGANOS = [("corazon", {"heart"}), ("aorta", {"aorta"}), ("vena_cava", {"superior vena cava", "inferior vena cava"}), ("pulmon_izq", {"left lung"}), ("pulmon_der", {"right lung"}),
           ("traquea", {"trachea"}), ("esofago", {"esophagus"}), ("diafragma", {"diaphragm"}), ("higado", {"liver"}), ("vesicula", {"gallbladder"}), ("estomago", {"stomach"}),
           ("pancreas", {"pancreas"}), ("rinon_izq", {"left kidney"}), ("rinon_der", {"right kidney"}), ("vejiga", {"urinary bladder"}), ("intestino_delgado", {"small intestine"}),
           ("intestino_grueso", {"large intestine"}), ("frontal", {"cortex of left frontal lobe", "cortex of right frontal lobe"}),
           ("corteza", {"cortex of left cerebral hemisphere", "cortex of right cerebral hemisphere"}), ("cerebelo", {"cerebellum"}), ("tronco_encefalico", {"brainstem"}),
           ("pineal", {"pineal body"}), ("hipotalamo", {"hypothalamus"})]
elegidos: dict[str, tuple[str, str]] = {}
for e, ns in el.items():
    for n in sorted(ns):
        if any(re.match(p, n) for p in HUESO):
            elegidos.setdefault(e, (n, "hueso"))
        elif any(re.match(p, n) for p in CARTILAGO):
            elegidos.setdefault(e, (n, "cartilago"))
for e, ns in el.items():
    if e in elegidos:
        continue
    for grupo, nombres in ORGANOS:
        hit = sorted(nombres & ns)
        if hit:
            elegidos[e] = (hit[0], f"organo-{grupo}")
            break
print("piezas:", len(elegidos), collections.Counter(c.split(":")[0] for _, c in elegidos.values()))

bpy.ops.wm.read_factory_settings(use_empty=True)
for e, (nombre, cat) in sorted(elegidos.items()):
    bpy.ops.wm.obj_import(filepath=str(OBJ / f"{e}.obj"), forward_axis="NEGATIVE_Y", up_axis="Z", global_scale=0.001)
    for o in bpy.context.selected_objects:
        o.name = f"{e}|{nombre}|{cat}"
        o.data.name = o.name
bpy.ops.export_scene.gltf(filepath=salida, export_format="GLB", export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=7,
                          export_draco_position_quantization=14, export_normals=False, export_texcoords=False, export_materials="NONE", export_apply=False)
print("OK", salida, Path(salida).stat().st_size)
