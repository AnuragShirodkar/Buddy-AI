// ESP32-CAM mast — forward-facing, ~120 mm lens height
// Optional servo horns: set use_pan_tilt = true for bracket clearance.

$fn = 48;

use_pan_tilt = false;
base = 36;
mast_h = use_pan_tilt ? 70 : 110;
mast_t = 3;
cam_w = 42;
cam_h = 42;

module cam_mount_plate() {
  difference() {
    cube([cam_w, 3, cam_h]);
    for (p = [[6, 6], [6, cam_h - 6], [cam_w - 6, 6], [cam_w - 6, cam_h - 6]])
      translate([p[0], -1, p[1]]) rotate([-90, 0, 0]) cylinder(h=10, d=2.5);
    translate([cam_w/2, -1, cam_h/2 + 4]) rotate([-90, 0, 0]) cylinder(h=10, d=14);
  }
}

difference() {
  union() {
    translate([-base/2, -base/2, 0]) cube([base, base, mast_t]);
    translate([-mast_t/2, -mast_t/2, 0]) cube([mast_t, mast_t, mast_h]);
    translate([-cam_w/2, mast_t/2, mast_h - 10]) cam_mount_plate();
  }
  for (p = [[-12, -12], [-12, 12], [12, -12], [12, 12]])
    translate([p[0], p[1], -1]) cylinder(h=mast_t + 2, d=3.2);
}

if (use_pan_tilt) {
  translate([40, 0, 0]) {
    difference() {
      cube([30, 30, 4]);
      translate([15, 15, -1]) cylinder(h=6, d=6);
      for (a = [0:90:270])
        rotate([0, 0, a]) translate([10, 0, -1]) cylinder(h=6, d=2.2);
    }
  }
}
