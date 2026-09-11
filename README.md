# POW3R Pie Tools

A Blender add-on that packages a set of useful object and scene utility tools into a single pie menu for quick access.

## Installation
- Copy `POW3R Pie Tools Add-On.py` into Blender's add-ons folder, or install it through Blender > Edit > Preferences > Add-ons > Install...
- Enable the add-on in Preferences > Add-ons.

## Usage
- Open the 3D Viewport.
- Press Ctrl + W to open the pie menu.
- Use the tools in the menu for faster object cleanup and workflow tasks.

## Features
- **Frame Active Object:** Quickly center the viewport on the current active object without losing the rest of the selection state.
- **Apply All Shape Keys:** Apply all shape keys for selected mesh objects in one action.
- **Clear Split Normals:** Reset split normals across selected objects to clean up smoothing and shading issues.
- **Duplicate To Selected:** Duplicate the active object to multiple selected targets, with optional linked duplication.
- **Remove Empty Boolean Modifiers:** Clean out boolean modifiers that are left empty or unassigned.
- **Remove Particles Systems From Selected:** Strip particle system modifiers from selected objects in one step.
- **Shapespark Validate Materials:** Scan the scene for materials that may not be compatible with Shapespark and report them for review.

## Notes
This add-on is designed to keep commonly used Blender utilities grouped in one place for faster production workflows. In the future, each operator may be split into its own source file for better modularity and organization.