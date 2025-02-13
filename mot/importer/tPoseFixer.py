import bpy, math
from mathutils import Vector

FIXED_FLAG = "FIXED_T-POSE"
def fixTPose(armObj: bpy.types.Object):
    if FIXED_FLAG in armObj and armObj[FIXED_FLAG]:
        return
    print("Applying T-Pose")
    
    # change all the bone rotations (technically more accurate but less nice to work with)
    bpy.ops.object.mode_set(mode="EDIT")
    for bone in armObj.data.edit_bones:
        #length = math.dist(bone.head, bone.tail)
        bone.tail = Vector(bone.head) + Vector((0, 0.1, 0))
    
    # apply armature modifiers on all armature children
    child: bpy.types.Object
    for child in armObj.children:
        if child.type != "MESH":
            continue
        for mod in child.modifiers:
            if mod.type != "ARMATURE":
                continue
            bpy.context.view_layer.objects.active = child
            bpy.ops.object.modifier_apply(modifier=mod.name)
    
    # apply armature as rest pose
    bpy.context.view_layer.objects.active = armObj
    armObj.select_set(True)
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.armature_apply()
    bpy.ops.object.mode_set(mode="OBJECT")
    
    # add armature modifier back
    for child in armObj.children:
        if child.type != "MESH":
            continue
        mod: bpy.types.ArmatureModifier
        mod = child.modifiers.new(name="Armature", type="ARMATURE")
        mod.object = armObj

    armObj[FIXED_FLAG] = True
