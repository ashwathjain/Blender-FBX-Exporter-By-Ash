# How to Use:
#   1. Install: Edit → Preferences → Add-ons → Install → select this .py file.
#   2. Enable the add-on from the Import-Export category.
#   3. Access it via: File → Export → Ash Export FBX (.fbx)
#   4. Choose whether to export only selected objects or all meshes.
#   5. Press “Export” — each object will be exported as its own FBX file.


bl_info = {
    "name": "Ash Export FBX",
    "author": "Ashwath Jain",
    "version": (2, 5),
    "blender": (3, 0, 0),
    "location": "File > Export > Ash Export FBX (.fbx)",
    "description": "Exports each object (or selected) as a separate FBX file at world origin, "
    "then restores transforms."
    " Can open export folder automatically.",
    "category": "Import-Export"
}

import bpy
import os
import platform
import subprocess


class ASH_OT_batch_export_fbx(bpy.types.Operator):
    "Export objects "

    bl_idname = "export_scene.ash_batch_fbx"
    bl_label = "Ash Export FBX"
    bl_options = {'REGISTER', 'UNDO'}

    only_selected: bpy.props.BoolProperty(
        name="Export Selected Only",
        description="Export only selected objects (if none selected, exports all meshes)",
        default=True
    )

    open_folder: bpy.props.BoolProperty(
        name="Open Folder After Export",
        description="Automatically open the export folder when export finishes",
        default=True
    )

    def execute(self, context):
        export_path = bpy.path.abspath("//exports/")
        os.makedirs(export_path, exist_ok=True)

        # Get objects to export
        if self.only_selected and context.selected_objects:
            objects_to_export = context.selected_objects
        else:
            objects_to_export = [obj for obj in bpy.data.objects if obj.type == 'MESH']

        if not objects_to_export:
            self.report({'WARNING'}, "No mesh objects found to export.")
            return {'CANCELLED'}

        exported_count = 0
        self.report({'INFO'}, f"🚀 Starting export... saving files to {export_path}")

        for obj in objects_to_export:
            if obj.type != 'MESH':
                continue

            # Save original transform
            original_loc = obj.location.copy()
            original_rot = obj.rotation_euler.copy()
            original_scale = obj.scale.copy()

            # Move to world origin
            obj.location = (0.0, 0.0, 0.0)
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Export FBX
            fbx_path = os.path.join(export_path, f"{obj.name}.fbx")
            bpy.ops.export_scene.fbx(
                filepath=fbx_path,
                use_selection=True,
                apply_unit_scale=True,
                bake_space_transform=True,
                object_types={'MESH', 'ARMATURE'},
                mesh_smooth_type='FACE',
                use_mesh_modifiers=True,
                path_mode='AUTO'
            )

            # Restore original transform
            obj.location = original_loc
            obj.rotation_euler = original_rot
            obj.scale = original_scale
            obj.select_set(False)

            print(f"✅ Exported {obj.name} → {fbx_path}")
            exported_count += 1

        # Summary message
        summary = f"✨ Export complete! {exported_count} FBX file(s) saved to:\n{export_path}"
        self.report({'INFO'}, summary)
        print(summary)

        # Auto-open export folder
        if self.open_folder:
            try:
                if platform.system() == "Windows":
                    os.startfile(export_path)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", export_path])
            except Exception as e:
                self.report({'WARNING'}, f"Couldn't open folder: {e}")

        return {'FINISHED'}


# --- Add menu entry under File > Export ---
def menu_func_export(self, context):
    self.layout.operator(ASH_OT_batch_export_fbx.bl_idname, text="Ash Export FBX (.fbx)")


def register():
    bpy.utils.register_class(ASH_OT_batch_export_fbx)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ASH_OT_batch_export_fbx)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
