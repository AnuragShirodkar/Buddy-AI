// ESP AI Finder Robot — differential-drive base
// Units: millimeters. Open in OpenSCAD → F6 → Export STL.

$fn = 48;

chassis_len = 180;
chassis_w = 140;
chassis_t = 3;
wall = 2.5;
motor_gap = 58;       // distance between motor mounting faces
wheel_clearance = 12;
motor_mount_spacing = 18; // TT motor screw spacing (approx)
axle_h = 18;

module rounded_rect(l, w, t, r=6) {
  linear_extrude(t)
    offset(r=r) offset(delta=-r)
      square([l, w], center=true);
}

module motor_mount_holes() {
  for (x = [-motor_mount_spacing/2, motor_mount_spacing/2])
    translate([x, 0, -1]) cylinder(h=chassis_t+2, d=3.2);
}

difference() {
  union() {
    rounded_rect(chassis_len, chassis_w, chassis_t);
    // side walls
    translate([0, chassis_w/2 - wall/2, chassis_t])
      cube([chassis_len - 20, wall, 25], center=true);
    translate([0, -(chassis_w/2 - wall/2), chassis_t])
      cube([chassis_len - 20, wall, 25], center=true);
    // front bumper lip
    translate([chassis_len/2 - 4, 0, chassis_t + 6])
      cube([3, chassis_w - 20, 12], center=true);
  }

  // motor cutouts left/right
  for (side = [-1, 1]) {
    translate([0, side * (chassis_w/2 - 8), -1])
      cube([70, 20, chassis_t + 4], center=true);
    translate([-10, side * (chassis_w/2 - 6), 0])
      motor_mount_holes();
  }

  // battery strap slots
  for (x = [-40, 40])
    translate([x, 0, -1]) cube([8, 50, chassis_t + 2], center=true);

  // cable pass-through
  translate([50, 0, -1]) cylinder(h=chassis_t + 2, d=12);

  // ESP32 standoff holes (approx 25x50 footprint)
  for (p = [[-20, -15], [-20, 15], [20, -15], [20, 15]])
    translate([p[0] - 30, p[1], -1]) cylinder(h=chassis_t + 2, d=2.8);

  // driver board holes
  for (p = [[20, -20], [20, 20], [50, -20], [50, 20]])
    translate([p[0], p[1], -1]) cylinder(h=chassis_t + 2, d=2.8);
}

// caster pad at rear
translate([-chassis_len/2 + 20, 0, 0])
  difference() {
    cylinder(h=axle_h, d=28);
    translate([0, 0, -1]) cylinder(h=axle_h + 2, d=3.2);
  }
