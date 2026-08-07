#ifndef FINDER_MOTOR_CONFIG_H
#define FINDER_MOTOR_CONFIG_H

#include "secrets.h"

#ifndef WIFI_SSID
#error "Create esp32-motor/secrets.h from secrets.h.example"
#endif

#define HTTP_PORT 80
#define UDP_PORT 4210

// Dual H-bridge pinout (change to match your wiring — see docs/wiring.md)
#define PIN_AIN1 26
#define PIN_AIN2 27
#define PIN_PWMA 25
#define PIN_BIN1 33
#define PIN_BIN2 32
#define PIN_PWMB 14

// 1 = driver has ENA/ENB PWM pins; 0 = direction-only (L9110-style)
#define MOTOR_HAS_PWM 1

// Flip if a side runs backward
#define MOTOR_INVERT_LEFT 0
#define MOTOR_INVERT_RIGHT 0

#define PWM_FREQ_HZ 20000
#define PWM_RES_BITS 8
#define DEFAULT_SPEED 180   // 0-255
#define WATCHDOG_MS 800     // stop if no command within this window

#endif
