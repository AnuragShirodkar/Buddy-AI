// Cable clip — print 4–6, screw or glue to chassis rails

$fn = 32;

difference() {
  union() {
    cube([16, 10, 8]);
    translate([0, 3, 8]) cube([16, 4, 6]);
  }
  translate([8, -1, 5]) rotate([-90, 0, 0]) cylinder(h=12, d=6);
  translate([8, 5, -1]) cylinder(h=20, d=3.2);
}
