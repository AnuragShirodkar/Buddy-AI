# 3D-printable parts

Open these in [OpenSCAD](https://openscad.org/), press **F6** (Render), then **File → Export → Export as STL**.

| File | Part |
|------|------|
| [`chassis.scad`](chassis.scad) | Differential-drive base, motor cutouts, battery straps, ESP/driver holes |
| [`pi_tray.scad`](pi_tray.scad) | Pi 3 B+ standoffs + power-bank pocket + vents |
| [`camera_mast.scad`](camera_mast.scad) | Forward CAM mount (~110 mm mast). Set `use_pan_tilt = true` for servo spacer |
| [`cable_clip.scad`](cable_clip.scad) | Wire clips |

## Print settings (starting point)

- Material: PLA or PETG  
- Layer: 0.2 mm  
- Infill: 25–40% for chassis; 15% for clips  
- Supports: usually none (mast may need supports under cam plate depending on orientation)

## Assembly order

1. Press-fit / screw motors into chassis sides  
2. Mount motor driver + ESP32-WROOM  
3. Bolt Pi tray above (keep Pi vents clear)  
4. Mount camera mast at front; aim slightly downward for floor objects  
5. Route wires through cable clips; keep clear of wheels  

Lens height target: **10–15 cm** above floor for v1 find-on-floor tasks.
