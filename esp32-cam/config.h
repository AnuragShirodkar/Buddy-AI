#ifndef FINDER_CAM_CONFIG_H
#define FINDER_CAM_CONFIG_H

// Copy secrets from secrets.h.example → secrets.h (gitignored pattern: edit locally)
#include "secrets.h"

#ifndef WIFI_SSID
#error "Create esp32-cam/secrets.h from secrets.h.example"
#endif

// AI-Thinker ESP32-CAM
#define CAMERA_MODEL_AI_THINKER

#define HTTP_PORT 80
#define FRAME_SIZE FRAMESIZE_VGA   // 640x480 — good balance for Wi-Fi + vision
#define JPEG_QUALITY 12            // lower = better quality, larger files
#define XCLK_FREQ_HZ 20000000

#endif
