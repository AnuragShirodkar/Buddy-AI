/*********
  ESP32-WROOM — Finder Robot drive base
  HTTP:
    GET  /                         status
    GET  /cmd?dir=forward&speed=180&ms=300
    POST /cmd  JSON {"dir":"left","speed":160,"ms":250}
  UDP (port 4210): plain text "forward 180 300" or "stop"
*********/

#include <WiFi.h>
#include <WebServer.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include "config.h"

WebServer server(HTTP_PORT);
WiFiUDP udp;

enum Dir { DIR_STOP, DIR_FORWARD, DIR_BACK, DIR_LEFT, DIR_RIGHT };

#if MOTOR_HAS_PWM
static const int CH_A = 0;
static const int CH_B = 1;
#endif

static uint32_t last_cmd_ms = 0;
static uint32_t move_until_ms = 0;
static Dir current_dir = DIR_STOP;
static int current_speed = DEFAULT_SPEED;

static void write_pwm(bool left, int speed) {
#if MOTOR_HAS_PWM
  ledcWrite(left ? CH_A : CH_B, constrain(speed, 0, 255));
#else
  (void)left;
  (void)speed;
#endif
}

static void apply_side(bool left, int speed, bool forward) {
  if (left ? MOTOR_INVERT_LEFT : MOTOR_INVERT_RIGHT) {
    forward = !forward;
  }
  int in1 = left ? PIN_AIN1 : PIN_BIN1;
  int in2 = left ? PIN_AIN2 : PIN_BIN2;

  if (speed <= 0) {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    write_pwm(left, 0);
    return;
  }

  digitalWrite(in1, forward ? HIGH : LOW);
  digitalWrite(in2, forward ? LOW : HIGH);
  write_pwm(left, speed);
}

static void drive(Dir d, int speed) {
  current_dir = d;
  current_speed = speed;
  last_cmd_ms = millis();

  switch (d) {
    case DIR_FORWARD:
      apply_side(true, speed, true);
      apply_side(false, speed, true);
      break;
    case DIR_BACK:
      apply_side(true, speed, false);
      apply_side(false, speed, false);
      break;
    case DIR_LEFT:
      apply_side(true, speed, false);
      apply_side(false, speed, true);
      break;
    case DIR_RIGHT:
      apply_side(true, speed, true);
      apply_side(false, speed, false);
      break;
    case DIR_STOP:
    default:
      apply_side(true, 0, true);
      apply_side(false, 0, true);
      move_until_ms = 0;
      break;
  }
}

static Dir parse_dir(const String &s) {
  String d = s;
  d.toLowerCase();
  if (d == "forward" || d == "fwd" || d == "f") return DIR_FORWARD;
  if (d == "back" || d == "backward" || d == "reverse" || d == "b") return DIR_BACK;
  if (d == "left" || d == "l" || d == "turn_left") return DIR_LEFT;
  if (d == "right" || d == "r" || d == "turn_right") return DIR_RIGHT;
  return DIR_STOP;
}

static const char *dir_name(Dir d) {
  switch (d) {
    case DIR_FORWARD: return "forward";
    case DIR_BACK: return "back";
    case DIR_LEFT: return "left";
    case DIR_RIGHT: return "right";
    default: return "stop";
  }
}

static void apply_command(Dir d, int speed, int ms) {
  if (speed < 0) speed = DEFAULT_SPEED;
  if (speed > 255) speed = 255;
  if (d == DIR_STOP || ms == 0) {
    drive(DIR_STOP, 0);
    return;
  }
  if (ms < 0) {
    // continuous until watchdog or stop
    move_until_ms = 0;
    drive(d, speed);
    return;
  }
  move_until_ms = millis() + (uint32_t)ms;
  drive(d, speed);
}

static void handle_status() {
  char buf[192];
  snprintf(buf, sizeof(buf),
           "{\"device\":\"esp32-motor\",\"ip\":\"%s\",\"dir\":\"%s\",\"speed\":%d,\"watchdog_ms\":%d}",
           WiFi.localIP().toString().c_str(), dir_name(current_dir), current_speed, WATCHDOG_MS);
  server.send(200, "application/json", buf);
}

static void handle_cmd_get() {
  String dir = server.hasArg("dir") ? server.arg("dir") : "stop";
  int speed = server.hasArg("speed") ? server.arg("speed").toInt() : DEFAULT_SPEED;
  int ms = server.hasArg("ms") ? server.arg("ms").toInt() : 300;
  apply_command(parse_dir(dir), speed, ms);
  server.send(200, "application/json",
              String("{\"ok\":true,\"dir\":\"") + dir_name(current_dir) + "\"}");
}

static void handle_cmd_post() {
  StaticJsonDocument<256> doc;
  DeserializationError err = deserializeJson(doc, server.arg("plain"));
  if (err) {
    server.send(400, "application/json", "{\"ok\":false,\"error\":\"bad_json\"}");
    return;
  }
  const char *dir = doc["dir"] | "stop";
  int speed = doc["speed"] | DEFAULT_SPEED;
  int ms = doc.containsKey("ms") ? (int)doc["ms"] : 300;
  apply_command(parse_dir(String(dir)), speed, ms);
  server.send(200, "application/json",
              String("{\"ok\":true,\"dir\":\"") + dir_name(current_dir) + "\"}");
}

static void handle_udp() {
  int packetSize = udp.parsePacket();
  if (packetSize <= 0) return;
  char packet[128];
  int n = udp.read(packet, sizeof(packet) - 1);
  if (n <= 0) return;
  packet[n] = 0;
  String line = String(packet);
  line.trim();
  // formats: "stop" | "forward" | "forward 180" | "forward 180 300"
  int sp1 = line.indexOf(' ');
  String dstr = (sp1 < 0) ? line : line.substring(0, sp1);
  int speed = DEFAULT_SPEED;
  int ms = 300;
  if (sp1 >= 0) {
    String rest = line.substring(sp1 + 1);
    rest.trim();
    int sp2 = rest.indexOf(' ');
    if (sp2 < 0) {
      speed = rest.toInt();
    } else {
      speed = rest.substring(0, sp2).toInt();
      ms = rest.substring(sp2 + 1).toInt();
    }
  }
  if (dstr.equalsIgnoreCase("stop")) ms = 0;
  apply_command(parse_dir(dstr), speed, ms);
}

void setup() {
  Serial.begin(115200);

  pinMode(PIN_AIN1, OUTPUT);
  pinMode(PIN_AIN2, OUTPUT);
  pinMode(PIN_BIN1, OUTPUT);
  pinMode(PIN_BIN2, OUTPUT);
#if MOTOR_HAS_PWM
  ledcSetup(CH_A, PWM_FREQ_HZ, PWM_RES_BITS);
  ledcSetup(CH_B, PWM_FREQ_HZ, PWM_RES_BITS);
  ledcAttachPin(PIN_PWMA, CH_A);
  ledcAttachPin(PIN_PWMB, CH_B);
#endif
  drive(DIR_STOP, 0);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.printf("WiFi connecting to %s", WIFI_SSID);
  for (int i = 0; i < 40 && WiFi.status() != WL_CONNECTED; i++) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi failed — check secrets.h");
    return;
  }
  Serial.print("MOTOR IP: ");
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, handle_status);
  server.on("/cmd", HTTP_GET, handle_cmd_get);
  server.on("/cmd", HTTP_POST, handle_cmd_post);
  server.begin();

  udp.begin(UDP_PORT);
  Serial.printf("HTTP cmd: http://%s/cmd?dir=stop\n", WiFi.localIP().toString().c_str());
  Serial.printf("UDP port: %d\n", UDP_PORT);
}

void loop() {
  server.handleClient();
  handle_udp();

  uint32_t now = millis();
  if (move_until_ms != 0 && (int32_t)(now - move_until_ms) >= 0) {
    drive(DIR_STOP, 0);
  }
  if (current_dir != DIR_STOP && (now - last_cmd_ms) > WATCHDOG_MS) {
    Serial.println("Watchdog stop");
    drive(DIR_STOP, 0);
  }
}
