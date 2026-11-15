"""Importa un .glb y lo renderiza (Workbench, CPU) de frente y en primer plano de la cabeza: comprueba lo EXPORTADO, no lo de la web.
Uso: blender -b --python scripts/blender/ver_glb.py -- data/modelos/crew_VEGA.glb"""
import math, sys
from pathlib import Path
import bpy
ruta = Path(sys.argv[sys.argv.index("--") + 1])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ruta))
sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"
sc.display.shading.light = "FLAT"; sc.display.shading.color_type = "TEXTURE"
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.05, 0.045, 0.04)
cam = bpy.data.objects.new("c", bpy.data.cameras.new("c")); sc.collection.objects.link(cam); sc.camera = cam; cam.data.type = "ORTHO"
mallas = [o for o in bpy.data.objects if o.type == "MESH"]
top = max(max((o.matrix_world @ v.co).z for v in o.data.vertices) for o in mallas); print("ALTURA", round(top, 3))
for nombre, esc, z in (("cuerpo", 2.2, top / 2), ("cabeza", 0.5, top - 0.12)):
    cam.data.ortho_scale = esc; cam.location = (0, -5, z); cam.rotation_euler = (math.radians(90), 0, 0)
    sc.render.resolution_x, sc.render.resolution_y = 600, 800
    sc.render.filepath = str(ruta.with_name(f"glb_{ruta.stem}_{nombre}.png")); bpy.ops.render.render(write_still=True)
