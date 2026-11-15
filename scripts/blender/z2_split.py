"""Parte el traje NASA Z-2 (NASA 3D Resources) en dos mallas, traje y casco, para poder quitar el casco en la web.
Criterio geométrico (el modelo es una sola malla): caras cuyo centroide cae dentro de una esfera alrededor del casco, por encima del cuello.
Uso: blender -b --python scripts/blender/z2_split.py   → web/public/models/z2_suit.glb y z2_helmet.glb (el z2.glb original no se toca)"""
import bmesh, bpy
from mathutils import Vector
ORIGEN, SALIDA = "web/public/models/z2.glb", "web/public/models"
CENTRO, RADIO, Z_MIN = Vector((0.0, -0.115, 1.72)), 0.34, 1.60     # medido sobre el modelo (Z arriba en Blender)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=ORIGEN)
o = [x for x in bpy.data.objects if x.type == "MESH"][0]
mw = o.matrix_world
bm = bmesh.new(); bm.from_mesh(o.data)
Y_MAX = 0.10   # lo que queda detrás (mochila) se queda en el traje
casco = [f for f in bm.faces if (mw @ f.calc_center_median()).z > Z_MIN and (mw @ f.calc_center_median()).y < Y_MAX and ((mw @ f.calc_center_median()) - CENTRO).length < RADIO]
print("CARAS casco", len(casco), "de", len(bm.faces))
def guardar(nombre, caras_borrar):
    b = bm.copy(); idx = {f.index for f in caras_borrar}; b.faces.ensure_lookup_table()
    bmesh.ops.delete(b, geom=[b.faces[i] for i in idx], context="FACES")
    me = bpy.data.meshes.new(nombre); b.to_mesh(me); b.free()
    ob = bpy.data.objects.new(nombre, me); bpy.context.scene.collection.objects.link(ob)
    for m in o.data.materials: me.materials.append(m)
    for x in bpy.data.objects: x.select_set(x is ob)
    bpy.ops.export_scene.gltf(filepath=f"{SALIDA}/{nombre}.glb", export_format="GLB", use_selection=True, export_draco_mesh_compression_enable=True)
    bpy.data.objects.remove(ob)
idc = {f.index for f in casco}
bm.transform(mw)                                                     # las mallas nuevas nacen sin la rotación que el importador puso al objeto: se hornea en los vértices
guardar("z2_suit", casco)                                            # traje = todo menos el casco
guardar("z2_helmet", [f for f in bm.faces if f.index not in idc])    # casco = solo esas caras
