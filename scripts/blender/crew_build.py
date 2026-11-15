"""Genera a un tripulante FICTICIO realista con MPFB (humano 100 % generado por script en Blender; assets CC0 de MakeHuman) y lo deja listo para la vitrina.
Uso:  BLENDER_USER_RESOURCES=data/blender_user blender -b --python scripts/blender/crew_build.py -- VEGA [--preview]
Salida: data/modelos/crew_<INDICATIVO>.blend (+ vista previa PNG con --preview). Nada de personas reales: son combinaciones de parámetros."""
import math
import re
import sys
from pathlib import Path

import bpy
from mathutils import Euler

RAIZ = Path(bpy.data.filepath).resolve().parent if bpy.data.filepath else Path.cwd()
SALIDA = Path.cwd() / "data" / "modelos"
COLOR_FRANJA = {"VEGA": "#d9a441", "LYRA": "#86a982", "ALTAIR": "#c8553d", "CASTOR": "#c98aa0", "RIGEL": "#8d86c9"}   # = src/libro/tripulacion.py
PERFIL_BRAZO = 0   # sin pose forzada: la A-pose de MakeHuman es limpia; girar los huesos sin repintar pesos rompe el hombro
SPECS = {   # macro: gender 0=mujer 1=hombre · age 0.5=25 años (≈ 0.75 → 45) · race: reparto asiático/caucásico/africano · assets: nombres de los packs CC0
    "VEGA":   dict(macro=dict(gender=1.0, age=0.72, muscle=0.58, weight=0.52, height=0.62, proportions=0.55, race=dict(asian=0.05, caucasian=0.85, african=0.10)), pelo="Short02", cejas="Eyebrow004", piel="middleage_caucasian_male", ojos=(0.50, 0.31, 0.16)),
    "LYRA":   dict(macro=dict(gender=0.0, age=0.58, muscle=0.45, weight=0.42, height=0.5, proportions=0.6, race=dict(asian=0.75, caucasian=0.2, african=0.05)), pelo="Ponytail01", cejas="Eyebrow007", piel="young_asian_female", ojos=(0.26, 0.16, 0.09)),
    "ALTAIR": dict(macro=dict(gender=1.0, age=0.62, muscle=0.7, weight=0.58, height=0.58, proportions=0.5, race=dict(asian=0.0, caucasian=0.05, african=0.95)), pelo="Short04", cejas="Eyebrow001", piel="young_african_male", ojos=(0.24, 0.14, 0.08)),
    "CASTOR": dict(macro=dict(gender=0.0, age=0.7, muscle=0.4, weight=0.48, height=0.52, proportions=0.55, race=dict(asian=0.05, caucasian=0.9, african=0.05)), pelo="Bob01", cejas="Eyebrow010", piel="middleage_caucasian_female", ojos=(0.30, 0.45, 0.30)),
    "RIGEL":  dict(macro=dict(gender=1.0, age=0.55, muscle=0.5, weight=0.45, height=0.55, proportions=0.52, race=dict(asian=0.2, caucasian=0.4, african=0.4)), pelo="Short03", cejas="Eyebrow005", piel="young_caucasian_male", ojos=(0.34, 0.34, 0.22)),
}


def hex_a_lineal(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c] + [1.0]


QUITAR = ("head", "jaw", "ears", "eye", "lips", "finger", "metacarpal", "foot", "toe", "fingernails", "oculi", "orbicularis")


def crear_uniforme(nombre, base, rig):
    """Mono de vuelo a medida: la superficie evaluada del cuerpo (sin ayudantes), sin cabeza/manos/pies, desplazada 1 cm hacia fuera y pintada con la franja del tripulante."""
    import bmesh
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(base.evaluated_get(dg))
    ob = bpy.data.objects.new(f"{nombre}_uniform", me)
    bpy.context.scene.collection.objects.link(ob)
    for g in base.vertex_groups:
        ob.vertex_groups.new(name=g.name)
    nombres = {g.index: g.name for g in base.vertex_groups}
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    dvert = bm.verts.layers.deform.verify()
    cabeza_z = min(v.co.z for v in bm.verts if sum(w for gi, w in v[dvert].items() if nombres[gi] == "head") > 0.5)
    corte = cabeza_z - 0.075                                  # todo lo que está por encima del cuello se va, sin depender de pesos (evita restos en mejillas)
    borrar = [v for v in bm.verts if sum(w for gi, w in v[dvert].items() if any(nombres[gi].startswith(q) for q in QUITAR)) > 0.45]
    bmesh.ops.delete(bm, geom=borrar, context="VERTS")
    # bordes limpios: cuello, muñecas y tobillos se cortan con PLANOS (no con pesos de vértice, que dejan dientes de sierra)
    from mathutils import Vector
    def corta(co, no, quitar_fuera=True):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no, clear_outer=quitar_fuera, clear_inner=not quitar_fuera)
    corta(Vector((0, 0, corte)), Vector((0, 0, 1)))
    for lado in ("L", "R"):
        try:
            mu, an = rig.pose.bones[f"wrist.{lado}"], rig.pose.bones[f"foot.{lado}"]
            ant = rig.pose.bones[f"lowerarm02.{lado}"]
            eje = (mu.head - ant.head).normalized()
            corta(mu.head.copy(), eje)                                   # la mano queda fuera
            corta(Vector((0, 0, an.head.z + 0.03)), Vector((0, 0, 1)), quitar_fuera=False)   # el pie queda fuera
        except KeyError:
            print("AVISO: hueso no encontrado para el corte limpio", lado)
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * 0.011                                # la prenda queda 1,1 cm por fuera de la piel
    bm.verts.ensure_lookup_table()
    # franja de color en el brazo (35–52 % entre hombro y codo) y en el cuello de la prenda
    col = bm.loops.layers.color.new("Col")
    base_c, franja = hex_a_lineal("#d9d3c1"), hex_a_lineal(COLOR_FRANJA[nombre])
    # franjas con BORDE NÍTIDO: se insertan cortes (planos) en los límites de la banda y se colorea por cara, no por vértice (la interpolación dibujaba dientes de sierra)
    def centro(lado, prefijos):                                # centroide de los vértices con peso en esos huesos (la geometría real del brazo, no una suposición)
        grupos = {gi for gi, n in nombres.items() if any(n == f"{q}.{lado}" for q in prefijos)}
        pts = [v.co.copy() for v in bm.verts if sum(w for gi, w in v[dvert].items() if gi in grupos) > 0.5]
        return sum(pts, Vector((0, 0, 0))) / len(pts) if pts else None
    brazos = []
    for lado in ("L", "R"):
        cu, cl = centro(lado, ("upperarm01", "upperarm02")), centro(lado, ("lowerarm01", "lowerarm02"))
        if cu is not None and cl is not None:
            u = (cl - cu).normalized()
            brazos.append((cu, u))                             # franja = 7 cm a cada lado del centro del brazo superior
    def corte_sin_borrar(co, no):
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no)
    z_collar = corte - 0.025
    corte_sin_borrar(Vector((0, 0, z_collar)), Vector((0, 0, 1)))
    for cu, u in brazos:
        for t in (-0.07, 0.07):
            corte_sin_borrar(cu + u * t, u)
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        c = f.calc_center_median()
        en_banda = c.z > z_collar - 1e-4 and abs(c.x) < 0.13
        for cu, u in brazos:
            t = (c - cu).dot(u)
            if abs(t) <= 0.07 + 1e-4 and ((c - cu) - u * t).length < 0.09:
                en_banda = True
        for l in f.loops:
            l[col] = franja if en_banda else base_c
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    mat = bpy.data.materials.new(f"{nombre}_uniform_mat"); mat.use_nodes = True
    nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
    nodo = nt.nodes.new("ShaderNodeVertexColor"); nodo.layer_name = "Col"
    nt.links.new(nodo.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.88
    me.materials.clear(); me.materials.append(mat)
    for pol in me.polygons:
        pol.material_index = 0
    return ob


def material_plano(nombre, rgb, rugosidad=0.4):
    m = bpy.data.materials.new(nombre); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Base Color"].default_value = (*rgb, 1.0); b.inputs["Roughness"].default_value = rugosidad
    return m


def ojos(me, nombre):
    """Ojo = esfera: casquete frontal (≈38°) = iris del color del tripulante; casquete central (≈14°) = pupila; resto = esclerótica. Sustituye a la textura, que no se tiñe bien."""
    me.materials.clear()
    for m in (material_plano(f"{nombre}_sclera", (0.88, 0.85, 0.80), 0.35), material_plano(f"{nombre}_iris", COLOR_OJOS, 0.25), material_plano(f"{nombre}_pupil", (0.01, 0.01, 0.012), 0.1)):
        me.materials.append(m)
    c38, c14 = math.cos(math.radians(38)), math.cos(math.radians(14))
    for p in me.polygons:
        d = -p.normal.y
        p.material_index = 2 if d > c14 else 1 if d > c38 else 0


def crear_ropa_interior(nombre, base, rig, mujer):
    """Short (y top deportivo en las mujeres) a medida desde la superficie del cuerpo: la capa Body deja de ser un cuerpo desnudo."""
    import bmesh
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(base.evaluated_get(dg))
    zs = [v.co.z for v in me.vertices]
    alto = max(zs) - min(zs)
    zmin = min(zs)
    bandas = [(0.455, 0.545, 0.125)] + ([(0.705, 0.775, 0.098)] if mujer else [])     # (z0, z1, |x|máx) como fracción de la altura
    from mathutils import Vector
    piezas = []
    for z0, z1, xl in bandas:
        bm = bmesh.new(); bm.from_mesh(me)
        for co, no, clear_inner in ((Vector((0, 0, zmin + z0 * alto)), Vector((0, 0, 1)), True), (Vector((0, 0, zmin + z1 * alto)), Vector((0, 0, 1)), False),
                                    (Vector((-xl * alto, 0, 0)), Vector((1, 0, 0)), True), (Vector((xl * alto, 0, 0)), Vector((1, 0, 0)), False)):
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no, clear_inner=clear_inner, clear_outer=not clear_inner)
        piezas.append(bm)
    bm = piezas[0]
    for extra in piezas[1:]:
        tmp = bpy.data.meshes.new("tmp"); extra.to_mesh(tmp); extra.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    bm.normal_update()
    for v in bm.verts:
        v.co += v.normal * 0.004
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(f"{nombre}_underwear", me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.clear(); me.materials.append(material_plano(f"{nombre}_underwear_mat", (0.10, 0.10, 0.11), 0.7))
    for p in me.polygons:
        p.material_index = 0
    return ob


def exportar(nombre, base, rig):
    """Hornea todo a mallas estáticas (sin rig), simplifica los materiales a Principled con su textura y exporta un .glb con una malla por capa."""
    dg = bpy.context.evaluated_depsgraph_get()
    estaticos = []
    for ob in [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith(("_uniform", "_underwear"))]:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        nuevo = bpy.data.objects.new(ob.name.replace(f"{nombre}_body.", f"{nombre}_").replace(f"{nombre}_body", f"{nombre}_skin"), me)
        bpy.context.scene.collection.objects.link(nuevo)
        for slot in ob.material_slots:
            me.materials.append(simple_material(slot.material))
        if "high-poly" in ob.name.lower():
            ojos(me, nombre)
        for p in me.polygons:
            p.use_smooth = True
        estaticos.append(nuevo)
        ob.hide_viewport = True; ob.hide_render = True
    rig.hide_viewport = True
    for o in bpy.data.objects:
        o.select_set(o in estaticos or o.name.endswith(("_uniform", "_underwear")))
    destino = SALIDA / f"crew_{nombre}.glb"
    bpy.ops.export_scene.gltf(filepath=str(destino), export_format="GLB", use_selection=True, export_image_format="WEBP", export_materials="EXPORT",
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6, export_yup=True, export_apply=False)
    print("GLB", destino, round(destino.stat().st_size / 1e6, 2), "MB", [o.name for o in estaticos])


def imagenes(arbol, vistos=None):
    """Todas las imágenes de un árbol de nodos, entrando en los grupos (el material de piel de MPFB las guarda dentro)."""
    vistos = vistos or set()
    out = []
    for nd in arbol.nodes:
        if nd.type == "TEX_IMAGE" and nd.image and nd.image.name not in vistos:
            vistos.add(nd.image.name); out.append(nd.image)
        elif nd.type == "GROUP" and nd.node_tree:
            out += imagenes(nd.node_tree, vistos)
    return out


def teñir(img, rgb, nombre):
    """Copia de la imagen con su color multiplicado (iris): MakeHuman tiñe el iris con el color del material; glTF no lo hace solo."""
    import numpy as np
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, 4)
    luma = px[:, :3].mean(axis=1, keepdims=True)
    f = np.clip((0.78 - luma) / 0.25, 0, 1)                      # solo el iris (oscuro) se tiñe; la esclera blanca queda blanca
    px[:, :3] = px[:, :3] * (1 - f) + px[:, :3] * np.array(rgb, dtype=np.float32) * 2.2 * f
    px[:, :3] = np.clip(px[:, :3], 0, 1)
    nueva = bpy.data.images.new(nombre, w, h, alpha=True)
    nueva.pixels.foreach_set(px.ravel()); nueva.pack()
    return nueva


PIEL_IMG: dict = {}
PELO = re.compile(r"short0|bob0|long0|ponytail|afro|braid|eyebrow|eyelash")


def simple_material(m):
    """Principled con la imagen de color del material original (el material MPFB usa grupos de nodos que glTF no entiende); pelo/cejas/pestañas con su transparencia."""
    nombre = (m.name if m else "m")
    n = bpy.data.materials.new(nombre + "_glb"); n.use_nodes = True
    bsdf = n.node_tree.nodes["Principled BSDF"]; bsdf.inputs["Roughness"].default_value = 0.6
    imgs = imagenes(m.node_tree) if (m and m.node_tree) else []
    print("MAT", nombre, [i.name for i in imgs])
    malos = ("normal", "bump", "spec", "rough", "ao", "sss", "displace", "mask")
    candidatas = [i for i in imgs if not any(k in i.name.lower() for k in malos)] or imgs
    if "high-poly" in nombre.lower() or "low-poly" in nombre.lower():
        candidatas = [i for i in candidatas if "eye" in i.name.lower()] or candidatas
    img = candidatas[0] if candidatas else None
    if img and nombre.lower().endswith(".body"):
        PIEL_IMG["img"] = img
    if img is None and nombre.lower().rsplit(".", 1)[-1] in ("nipple", "lips", "fingernails", "toenails", "ears", "genitals"):
        img = PIEL_IMG.get("img")                                   # estas piezas comparten el UV de la piel: se usa su misma textura
    if img and ("high-poly" in nombre.lower() or "low-poly" in nombre.lower()):
        img = teñir(img, COLOR_OJOS, nombre + "_iris")
    if img:
        t = n.node_tree.nodes.new("ShaderNodeTexImage"); t.image = img
        n.node_tree.links.new(t.outputs["Color"], bsdf.inputs["Base Color"])
        if PELO.search(nombre.lower()):
            n.node_tree.links.new(t.outputs["Alpha"], bsdf.inputs["Alpha"])
    return n


def vista_previa(nombre, base):
    """Render rápido con Workbench (CPU, texturas) de frente y de tres cuartos, para revisar sin salir de Blender."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "TEXTURE"; sc.display.shading.show_specular_highlight = False
    sc.render.resolution_x, sc.render.resolution_y = 700, 1000
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.05, 0.045, 0.04)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = "ORTHO"; cam.data.ortho_scale = 2.2
    for i, ang in enumerate((0, 35)):
        a = math.radians(ang)
        cam.location = (math.sin(a) * 5, -math.cos(a) * 5, 0.95); cam.rotation_euler = (math.radians(90), 0, a)
        sc.render.filepath = str(SALIDA / f"preview_{nombre}_{i}.png")
        SALIDA.mkdir(parents=True, exist_ok=True)
        bpy.ops.render.render(write_still=True)
    print("PREVIEW", nombre)


COLOR_OJOS = (0.50, 0.31, 0.16)   # se fija por tripulante en main()


def main():
    nombre = sys.argv[sys.argv.index("--") + 1].upper()
    spec = SPECS[nombre]
    global COLOR_OJOS
    COLOR_OJOS = spec.get("ojos", COLOR_OJOS)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.preferences.addon_enable(module="bl_ext.blender_org.mpfb")
    from bl_ext.blender_org.mpfb.services.assetservice import AssetService
    from bl_ext.blender_org.mpfb.services.humanservice import HumanService
    from bl_ext.blender_org.mpfb.services.targetservice import TargetService

    macro = TargetService.get_default_macro_info_dict()
    macro.update({k: v for k, v in spec["macro"].items()})
    base = HumanService.create_human(mask_helpers=True, detailed_helpers=False, extra_vertex_groups=True, feet_on_ground=True, scale=0.1, macro_detail_dict=macro)
    base.name = f"{nombre}_body"
    print("MACRO-ANTES", TargetService.get_macro_info_dict_from_basemesh(base))
    for k in ("gender", "age", "muscle", "weight", "proportions", "height"):        # se fijan explícitamente: create_human no siempre aplica el dict
        TargetService.set_target_value(base, k, spec["macro"][k])
    for r, v in spec["macro"]["race"].items():
        TargetService.set_target_value(base, r, v)
    TargetService.reapply_macro_details(base)
    print("MACRO-DESPUES", TargetService.get_macro_info_dict_from_basemesh(base), "alto", round(base.dimensions.z, 3))

    def asset(kind, name, sub, tipo):
        norm = lambda t: re.sub(r"[^a-z0-9]", "", str(t).lower())  # noqa: E731
        p = next((q for q in AssetService.list_mhclo_assets(sub) if norm(name) in norm(Path(str(q)).name)), None)
        if p is None:
            print("FALTA ASSET", sub, name, "de", [str(q).split("/")[-1] for q in AssetService.list_mhclo_assets(sub)][:12])
            return None
        return HumanService.add_mhclo_asset(str(p), base, asset_type=tipo, material_type="MAKESKIN")

    asset("eyes", "high-poly", "eyes", "Eyes")
    asset("eyebrows", spec["cejas"], "eyebrows", "Eyebrows")
    asset("eyelashes", "Eyelashes01", "eyelashes", "Eyelashes")
    asset("teeth", "Teeth base", "teeth", "Teeth")
    asset("tongue", "Tongue01", "tongue", "Tongue")
    asset("hair", spec["pelo"], "hair", "Hair")
    mh = next((p for p in AssetService.list_mhmat_assets("skins") if spec["piel"] in str(p)), None)
    if mh:
        HumanService.set_character_skin(str(mh), base, skin_type="ENHANCED_SSS")
    else:
        print("FALTA PIEL", spec["piel"])
    # --- pose: brazos caídos (A-pose suave) con el rig por defecto de MPFB, y se hornea la pose a mallas estáticas
    rig = HumanService.add_builtin_rig(base, "default", import_weights=True)
    print("BONES", [b.name for b in rig.pose.bones if "arm" in b.name.lower() or "clavicle" in b.name.lower()][:16])
    from mathutils import Matrix
    bpy.context.view_layer.update()
    for lado, signo in ((("L", -1), ("R", 1)) if PERFIL_BRAZO else ()):                   # bajar los brazos: giro en el eje Y del mundo (frente-atrás) alrededor del hombro
        pb = rig.pose.bones.get(f"upperarm01.{lado}")
        if pb:
            cabeza = pb.head.copy()
            T = Matrix.Translation(cabeza)
            pb.matrix = T @ Matrix.Rotation(signo * math.radians(PERFIL_BRAZO), 4, "Y") @ T.inverted() @ pb.matrix
            bpy.context.view_layer.update()
    bpy.context.view_layer.update()
    print("GRUPOS", sorted({g.name for g in base.vertex_groups})[:80], len(base.data.vertices), [m.type for m in base.modifiers])
    print("LISTO", nombre, [o.name for o in bpy.data.objects][:20], "alto", round(base.dimensions.z, 3))
    uni = crear_uniforme(nombre, base, rig)
    crear_ropa_interior(nombre, base, rig, spec["macro"]["gender"] < 0.5)
    if "--glb" in sys.argv:
        exportar(nombre, base, rig)
    if "--preview" in sys.argv:
        vista_previa(nombre, base)
    SALIDA.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(SALIDA / f"crew_{nombre}.blend"))


main()
