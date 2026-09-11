bl_info = {
    "name": "POW3R Pie Tools",
    "author": "Kenneth Cabacungan",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Pie Menu (Ctrl+W)",
    "description": "A collection of scene and object utilities in a pie menu.",
    "warning": "",
    "category": "Object",
}

import bpy
from bpy.props import BoolProperty

class VIEW3D_OT_frame_active_object(bpy.types.Operator):
    bl_idname = "view3d.frame_active_object"
    bl_label = "Frame Active Object"
    bl_description = "Frame only the active object, even if multiple objects are selected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.area.type != 'VIEW_3D':
            self.report({'WARNING'}, "This operator must run in a 3D View")
            return {'CANCELLED'}

        active = context.active_object
        if active is None:
            self.report({'WARNING'}, "No active object to frame")
            return {'CANCELLED'}

        view_layer = context.view_layer
        prev_selection = {obj: obj.select_get() for obj in view_layer.objects}

        try:
            for obj in view_layer.objects:
                obj.select_set(obj is active)
            bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
        finally:
            for obj, was_selected in prev_selection.items():
                obj.select_set(was_selected)

        return {'FINISHED'}


class ApplyAllShapeKeys(bpy.types.Operator):
    """Applies all shape keys of selected objects."""
    bl_idname = "mesh.apply_all_shape_keys"
    bl_label  = "Apply All Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        selected_count = 0
        if not selected:
            self.report({'WARNING'},"No objects selected.")
            return {'CANCELLED'}

        for obj in selected:
            if obj.type == 'MESH' and obj.data.shape_keys:
                context.view_layer.objects.active = obj
                try:
                    bpy.ops.object.shape_key_remove(all=True, apply_mix=True)
                except Exception:
                    # best-effort: continue on failure
                    pass
                selected_count += 1

        if selected_count > 1:
            self.report({'INFO'},f"Applied all shape keys of {selected_count} objects.")
        else:
            self.report({'INFO'},f"Applied all shape keys of {selected_count} object.")

        return {'FINISHED'}


class ClearAllSplitNormals(bpy.types.Operator):
    """Clears split normals of selected objects."""
    bl_idname = "mesh.clear_normals_all"
    bl_label  = "Clear All Split Normals"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        selected_count = 0
        if not selected:
            self.report({'WARNING'},"No objects selected.")
            return {'CANCELLED'}

        for obj in selected:
            context.view_layer.objects.active = obj
            try:
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
            except Exception:
                # operator may require edit mode; try a safer approach
                if obj.type == 'MESH' and obj.data.use_auto_smooth:
                    obj.data.use_auto_smooth = False
            selected_count += 1

        if selected_count > 1:
            self.report({'INFO'},f"Cleared split normals for {selected_count} objects.")
        else:
            self.report({'INFO'},f"Cleared split normals for {selected_count} object.")

        return {'FINISHED'}


class DuplicateToSelected(bpy.types.Operator):
    """Create duplicates of active object to selected objects."""
    bl_idname = "object.duplicate_to_selected"
    bl_label = "Duplicate To Selected"
    bl_options = {'REGISTER', 'UNDO'}

    linked: BoolProperty(
        name="Linked",
        description="Toggle linked duplicate",
        default=True,
    )
    
    def execute(self, context):
        active = context.active_object
        selected = context.selected_objects
        new_selected = []
        if len(selected) < 3:
            pass
        else:
            bpy.ops.object.select_all(action='DESELECT')
        active.select_set(1)
        
        n = 0
        for obj in selected:
            obj_location = (
                obj.location.x,
                obj.location.y,
                obj.location.z
            )
            
            if (obj.location == active.location) and (len(selected) < 3):
                self.report({'WARNING'}, "No duplicates created. Select at least 1 target object.")
                return {'CANCELLED'}
            elif (obj == active) or (obj.location == active.location):
                pass
            else:
                bpy.ops.object.duplicate(linked=self.linked) # Duplicate active
                copy = context.active_object
                copy.location = obj.location # Move duplicate to selected object
                new_selected.append(copy)                
                n += 1
        
        context.view_layer.objects.active = active
        active.select_set(1)
        for new_sel in new_selected:
            new_sel.select_set(1)
        
        duplicate_type = "linked " if self.linked else ""
        if n == 1:
            self.report({'INFO'}, f"Created {duplicate_type}duplicate for {n} object")
        elif n > 1:
            self.report({'INFO'}, f"Created {duplicate_type}duplicates for {n} objects")
        return {'FINISHED'}


class RemoveEmptyBooleanModifiers(bpy.types.Operator):
    """Removes empty boolean modifiers from selected objects."""
    bl_idname = "object.remove_empty_boolean_modifiers"
    bl_label = "Remove Empty Boolean Modifiers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        n = 0
        for obj in context.selected_objects:
            # use list() to avoid runtime changes during iteration
            for mod in list(obj.modifiers):
                if mod.type == 'BOOLEAN' and mod.object is None:
                    obj.modifiers.remove(mod)
                    n += 1

        if n:
            self.report({'INFO'}, f"Removed {n} empty boolean modifiers.")
        else:
            self.report({'INFO'}, "No empty boolean modifiers found.")

        return {'FINISHED'}


class RemoveParticlesSystems(bpy.types.Operator):
    """Removes particle system modifiers from selected objects."""
    bl_idname = "object.remove_particles_systems"
    bl_label  = "Remove Particles Systems From Selected"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected = context.selected_objects
        selected_count = 0
        if not selected:
            self.report({'WARNING'},"No objects selected.")
            return {'CANCELLED'}

        for obj in selected:
            for mod in reversed(list(obj.modifiers)):
                if mod.type == 'PARTICLE_SYSTEM':
                    obj.modifiers.remove(mod)
            selected_count += 1

        if selected_count > 1:
            self.report({'INFO'},f"Removed particles systems from {selected_count} objects.")
        else:
            self.report({'INFO'},f"Removed particles systems from {selected_count} object.")

        return {'FINISHED'}


class ShapesparkValidateMaterials(bpy.types.Operator):
    bl_idname = "object.shapespark_validate_materials"
    bl_label = "Shapespark Validate Materials"
    bl_description = "Validate all objects in scene for Shapespark compatible materials"
    bl_options = {'REGISTER', 'UNDO'}

    objects = {}

    def PrintObjects(self):

        report_lines = [
            "/-----------------Shapespark Validator v1.0-----------------/",
            "/-------------------Start of objects list-------------------/",
        ]
        for line in report_lines:
            self.report({"INFO"}, line)

        for key in self.objects.keys():
            obj_info = key + " : "

            materials = []
            for mat in self.objects[key]:
                mat = "\"" + mat + "\""
                print(mat)
                materials.append(mat)
            mat_info = ", ".join(materials)

            full_info = obj_info + mat_info
            report_lines.append(full_info)
            # print(full_info)
            self.report({"INFO"}, full_info)

        report_lines.extend([
            "/--------------------End of objects list--------------------/",
            "Objects listed above need checking for complex materials."
        ])

        for line in report_lines[2 + len(self.objects):]:
            self.report({"INFO"}, line)

        # Print validation report to text file in Blender
        end_report = [
            "For persistent validation report, see \"Shapespark Validator Report\" in the text editor.",
            "Finished scene validation. Click to view full details."
            ]
        for line in end_report:
            self.report({"INFO"}, line)
        report_text = bpy.data.texts.new("Shapespark Validator Report")
        report_text.write("\n".join(report_lines))
        return {'FINISHED'}

    def execute(self, context):
        self.objects = {} # key: object name, value: material index list []
        for obj in bpy.data.objects:
            try:
                for mat in obj.data.materials.values():
                    surface_input = next(
                        (
                            output.inputs.get("Surface")
                            for output in mat.node_tree.nodes
                            if output.type == "OUTPUT_MATERIAL"
                        ),
                        None,
                    )if mat and mat.use_nodes else None
                    has_direct_principled_connection = bool(
                        surface_input
                        and any(
                            link.from_node.type == "BSDF_PRINCIPLED"
                            for link in surface_input.links
                        )
                    )
                    principled_node = next(
                        (
                            link.from_node
                            for link in surface_input.links
                            if link.from_node.type == "BSDF_PRINCIPLED"
                        ),
                        None,
                    ) if surface_input else None
                    has_simple_principled_inputs = bool(
                        principled_node
                        and all(
                            link.from_node.type == "TEX_IMAGE"
                            or (
                                input_socket.name == "Normal"
                                and link.from_node.type in {"NORMAL_MAP", "BUMP"}
                            )
                            for input_socket in principled_node.inputs
                            for link in input_socket.links
                        )
                    )

                    # Tag material as complex material
                    if not has_direct_principled_connection or not has_simple_principled_inputs:
                        if obj.name not in self.objects:
                            self.objects.update({obj.name:[]})
                            # print(f"Added object {obj.name}")
                        self.objects[obj.name].append(mat.name)
            except AttributeError:
                pass

        self.PrintObjects()
        return {'FINISHED'}


class POW3R_PIE_TOOLS_Menu(bpy.types.Menu):
    bl_idname = "POW3R_MT_pie_tools"
    bl_label = "POW3R Pie Tools"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.separator()
        pie.separator()
        pie.operator("view3d.frame_active_object", text="Frame Active Object")
        pie.operator("mesh.apply_all_shape_keys", text="Apply Shape Keys")
        pie.operator("object.remove_empty_boolean_modifiers", text="Remove Empty Booleans")
        pie.operator("object.remove_particles_systems", text="Remove Particles")
        pie.operator("object.duplicate_to_selected", text="Duplicate To Selected")
        pie.operator("mesh.clear_normals_all", text="Clear Split Normals")
        pie.operator("object.shapespark_validate_materials", text="Shapespark Validate Materials")


classes = (
    ApplyAllShapeKeys,
    VIEW3D_OT_frame_active_object,
    ClearAllSplitNormals,
    DuplicateToSelected,
    RemoveEmptyBooleanModifiers,
    RemoveParticlesSystems,
    POW3R_PIE_TOOLS_Menu,
    ShapesparkValidateMaterials
)

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # keymap: Ctrl+W to open pie
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Window', space_type='EMPTY')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS', ctrl=True)
        kmi.properties.name = POW3R_PIE_TOOLS_Menu.bl_idname
        addon_keymaps.append((km, kmi))


def unregister():
    # remove keymaps
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
