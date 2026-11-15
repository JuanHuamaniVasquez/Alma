import bpy, sys, addon_utils
print("MOD", [m for m in sys.modules if m.startswith("bl_ext") and m.count(".") <= 2][:5])
try:
    bpy.ops.preferences.addon_enable(module="bl_ext.blender_org.mpfb")
except Exception as e:
    print("ENABLE-ERR", e)
from bl_ext.blender_org.mpfb.services.humanservice import HumanService
print("OK import", HumanService)
base = HumanService.create_human(mask_helpers=True, detailed_helpers=False, extra_vertex_groups=False, feet_on_ground=True, scale=0.1)
print("OBJ", base.name, len(base.data.vertices), "verts", tuple(round(x,2) for x in base.dimensions))
