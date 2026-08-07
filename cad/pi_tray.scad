// Raspberry Pi 3 B+ tray with power-bank pocket
// Mounts on top of chassis with M2.5/M3 screws.

$fn = 48;

pi_l = 90;
pi_w = 60;
tray_t = 2.5;
standoff_h = 6;
pocket_l = 105;
pocket_w = 55;
pocket_h = 28;

module pi_holes() {
  // Pi 3 mounting holes (approximate)
  holes = [[3.5, 3.5], [3.5, 49.5], [61.5, 3.5], [61.5, 49.5]];
  for (h = holes)
    translate([h[0], h[1], -1]) cylinder(h=tray_t + standoff_h + 2, d=2.7);
}

difference() {
  union() {
    cube([pi_l, pi_w, tray_t]);
    // standoffs
    holes = [[3.5, 3.5], [3.5, 49.5], [61.5, 3.5], [61.5, 49.5]];
    for (h = holes)
      translate([h[0], h[1], 0]) cylinder(h=tray_t + standoff_h, d=6);
    // power bank pocket behind Pi
    translate([pi_l + 2, (pi_w - pocket_w)/2, 0])
      difference() {
        cube([pocket_l, pocket_w, pocket_h]);
        translate([2, 2, 2]) cube([pocket_l - 4, pocket_w - 4, pocket_h]);
      }
  }
  pi_holes();
  // ventilation slots
  for (y = [12, 24, 36, 48])
    translate([15, y, -1]) cube([40, 3, tray_t + 2]);
  // chassis mount holes
  for (p = [[10, 10], [10, 50], [80, 10], [80, 50]])
    translate([p[0], p[1], -1]) cylinder(h=tray_t + 2, d=3.2);
}
