#!/usr/bin/env python3
"""Generate Buddy AI pin-connections PDF into docs/."""

from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parents[1] / "docs" / "Buddy_AI_Pin_Connections.pdf"


class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, "Buddy AI Finder Robot - Pin Connections", align="L")
        self.ln(4)
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(
            0,
            10,
            f"Page {self.page_no()}/{{nb}}  |  Pi 3 B+ + ESP32-CAM + ESP32-WROOM  |  v1",
            align="C",
        )

    def section(self, title: str):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(20, 20, 20)
        self.ln(2)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)

    def body(self, text: str):
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def table(self, headers, rows, col_widths=None):
        if col_widths is None:
            usable = 190
            col_widths = [usable / len(headers)] * len(headers)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(230, 230, 230)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9)
        for row in rows:
            line_h = 5
            max_lines = 1
            for i, cell in enumerate(row):
                lines = self.multi_cell(
                    col_widths[i], line_h, str(cell), dry_run=True, output="LINES"
                )
                max_lines = max(max_lines, len(lines))
            row_h = max(7, max_lines * line_h)
            if self.get_y() + row_h > self.page_break_trigger:
                self.add_page()
                self.set_font("Helvetica", "B", 9)
                self.set_fill_color(230, 230, 230)
                for i, h in enumerate(headers):
                    self.cell(col_widths[i], 7, h, border=1, fill=True)
                self.ln()
                self.set_font("Helvetica", "", 9)
            x0, y0 = self.get_x(), self.get_y()
            for i, cell in enumerate(row):
                self.set_xy(x0 + sum(col_widths[:i]), y0)
                self.multi_cell(
                    col_widths[i], line_h, str(cell), border=1, max_line_height=line_h
                )
            self.set_xy(x0, y0 + row_h)
        self.ln(3)


def main() -> None:
    pdf = PDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Buddy AI - Hardware Pin Map", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.body(
        "Locked stack: Raspberry Pi 3 B+ (brain), ESP32-CAM (eyes over Wi-Fi), "
        "ESP32-WROOM (motors, pan-tilt servos, distance sensor), Bluetooth speaker "
        "(voice out), phone/laptop mic for v1. No Raspberry Pi Camera Module."
    )

    pdf.section("1. Power")
    pdf.table(
        ["From", "To", "Notes"],
        [
            ["Pi 5V PSU / power bank", "Pi 3 B+ power input", "Do not power motors from the Pi"],
            ["5V supply (>=500mA)", "ESP32-CAM 5V + GND", "Prefer solid 5V; weak USB can brown out"],
            ["Motor battery (+)", "Motor driver VS / VCC motor", "Match motor voltage (often 6-12V)"],
            ["Motor battery (-)", "Motor driver GND", ""],
            ["Regulated 5V", "ESP32-WROOM VIN / 5V", "Buck from motor pack if needed"],
            ["ESP32-WROOM GND", "Driver GND", "Must share ground with driver"],
            ["Servo 5V supply", "Servo red wires", "Do NOT use ESP32 3.3V for servos"],
            ["Servo GND", "ESP32-WROOM GND", "Common ground"],
            ["Ultrasonic VCC", "5V", "HC-SR04 prefers 5V"],
            ["Ultrasonic GND", "ESP32-WROOM GND", "Common ground"],
        ],
        [55, 60, 75],
    )

    pdf.section("2. ESP32-CAM (eyes) - AI-Thinker style")
    pdf.body(
        "Camera pins are fixed on the module (firmware uses CAMERA_MODEL_AI_THINKER). "
        "You only wire power + Wi-Fi credentials. Pi fetches JPEG from http://CAM_IP/capture."
    )
    pdf.table(
        ["ESP32-CAM", "Connect to"],
        [
            ["5V", "5V supply (>=500mA)"],
            ["GND", "Power GND"],
            ["Wi-Fi", "Same network as Pi 3 B+ and ESP32-WROOM"],
            ["FTDI RX/TX/GPIO0", "Only when flashing firmware"],
        ],
        [50, 140],
    )
    pdf.body(
        "Do not attach motors to the CAM board. Mount CAM on pan-tilt mast; "
        "servos are driven by ESP32-WROOM, not the CAM."
    )
    pdf.body(
        "After boot, serial monitor @ 115200 prints CAM IP. Set pi-brain .env CAM_URL "
        "to http://THAT_IP (capture path is /capture, stream on port 81 /stream)."
    )

    pdf.section("3. ESP32-WROOM -> Motor driver (firmware defaults)")
    pdf.body("Left motor = A, Right motor = B. Pins match esp32-motor/config.h.")
    pdf.table(
        ["ESP32 GPIO", "L298N", "L9110", "Function"],
        [
            ["GPIO 26", "IN1", "A-IA", "Left / Motor A dir 1"],
            ["GPIO 27", "IN2", "A-IB", "Left / Motor A dir 2"],
            ["GPIO 25", "ENA (PWM)", "(unused*)", "Left speed PWM"],
            ["GPIO 33", "IN3", "B-IA", "Right / Motor B dir 1"],
            ["GPIO 32", "IN4", "B-IB", "Right / Motor B dir 2"],
            ["GPIO 14", "ENB (PWM)", "(unused*)", "Right speed PWM"],
            ["GND", "GND", "GND", "Common ground"],
        ],
        [35, 40, 40, 75],
    )
    pdf.body(
        "* For L9110 / drivers without ENA/ENB: set MOTOR_HAS_PWM to 0 in config.h. "
        "Driver OUT1/OUT2 -> left motor; OUT3/OUT4 -> right motor. "
        "If a side runs backward, swap that motor's two wires or set MOTOR_INVERT_LEFT/RIGHT."
    )

    pdf.section("4. Pan-tilt servos -> ESP32-WROOM")
    pdf.table(
        ["Servo wire", "Connect to"],
        [
            ["Brown / Black (GND)", "ESP32-WROOM GND"],
            ["Red (VCC)", "External 5V"],
            ["Orange / Yellow signal - Pan", "GPIO 18"],
            ["Orange / Yellow signal - Tilt", "GPIO 19"],
        ],
        [95, 95],
    )

    pdf.section("5. Distance sensor -> ESP32-WROOM")
    pdf.body("HC-SR04 ultrasonic (recommended defaults):")
    pdf.table(
        ["HC-SR04", "ESP32-WROOM"],
        [
            ["VCC", "5V"],
            ["GND", "GND"],
            ["TRIG", "GPIO 12"],
            ["ECHO", "GPIO 13 (use resistor divider 5V->3.3V if possible)"],
        ],
        [50, 140],
    )
    pdf.body("If using VL53L0X ToF instead:")
    pdf.table(
        ["VL53L0X", "ESP32-WROOM"],
        [
            ["VCC", "3.3V"],
            ["GND", "GND"],
            ["SDA", "GPIO 21"],
            ["SCL", "GPIO 22"],
        ],
        [50, 140],
    )

    pdf.add_page()
    pdf.section("6. Audio / network (no GPIO)")
    pdf.table(
        ["Device", "Connection"],
        [
            ["Bluetooth speaker", "Pair in Raspberry Pi OS (voice out)"],
            ["Phone / laptop mic (v1)", "Wi-Fi to Pi web UI / POST /command"],
            ["ReSpeaker 2-Mic HAT (next version)", "Onboard voice-in - not wired in v1"],
            ["Pi Camera Module", "Not used - you do not have one"],
        ],
        [80, 110],
    )

    pdf.section("7. Network map")
    pdf.table(
        ["Device", "Role", "Example"],
        [
            ["Pi 3 B+", "Brain", "Runs pi-brain; opens :8080"],
            ["ESP32-CAM", "Eyes", "http://192.168.x.y/capture"],
            ["ESP32-WROOM", "Motors/servos/sensor", "http://192.168.x.z/cmd"],
        ],
        [45, 55, 90],
    )
    pdf.body(
        "All three must be on the same Wi-Fi. Put CAM_URL and MOTOR_URL in pi-brain/.env."
    )

    pdf.section("8. ESP32-WROOM pin summary")
    pdf.table(
        ["GPIO", "Function"],
        [
            ["26", "Motor A IN1"],
            ["27", "Motor A IN2"],
            ["25", "Motor A ENA (PWM)"],
            ["33", "Motor B IN1"],
            ["32", "Motor B IN2"],
            ["14", "Motor B ENB (PWM)"],
            ["18", "Pan servo signal"],
            ["19", "Tilt servo signal"],
            ["12", "Ultrasonic TRIG"],
            ["13", "Ultrasonic ECHO"],
            ["21 / 22", "ToF SDA / SCL (if VL53 instead of HC-SR04)"],
            ["GND", "Common with driver, servos, sensor"],
        ],
        [40, 150],
    )

    pdf.section("9. Safety notes")
    pdf.body(
        "- Never feed motor current through the Pi 5V rail.\n"
        "- Give ESP32-CAM a solid 5V supply (brownouts cause Wi-Fi drops / bad images).\n"
        "- Share GND between ESP32-WROOM, motor driver logic, servos, and sensors.\n"
        "- Level-shift HC-SR04 ECHO (5V) down to 3.3V for ESP32 safety when possible.\n"
        "- Servos need a solid 5V supply; brownouts cause random resets.\n"
        "- Put Pi 3 B+, ESP32-CAM, and ESP32-WROOM on the same Wi-Fi network."
    )

    pdf.section("10. Firmware / config references")
    pdf.body(
        "Camera firmware: esp32-cam/\n"
        "Motor pins: esp32-motor/config.h\n"
        "Wiring notes: docs/wiring.md\n"
        "Repo: https://github.com/AnuragShirodkar/Buddy-AI"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
