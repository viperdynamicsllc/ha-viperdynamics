// Viper HA API v1 for ESP-IDF firmware (esp_http_server + mdns component).
// Spec: https://github.com/viperdynamicsllc/ha-viperdynamics/blob/main/docs/api.md
//
// Copy viper_ha_api.{c,h} into the firmware's main component, then:
//   1. Fill a viper_ha_device_t with the model, version and three callbacks.
//   2. Call viper_ha_register(httpd, &device, hostname) after httpd_start().
//   3. Call viper_ha_advertise(&device) after mdns_init() / mdns_service_add("_http", ...).
// Callbacks run on the httpd task; hand anything owned by another task over
// through flags rather than touching it directly.
#pragma once

#include <stdbool.h>
#include <stddef.h>
#include "esp_http_server.h"

#define VIPER_HA_API_VERSION 1

typedef struct {
    const char *model;       /* slug, e.g. "nether_portal_7_pro" */
    const char *model_name;  /* e.g. "Nether Portal 7 Pro" */
    const char *fw;          /* firmware version */
    /* Append JSON members to /api/info, each starting with ',' (identity fields
     * are written already). Return the number of chars written. */
    int (*fill_info)(char *buf, size_t cap);
    /* Write the /api/state members without braces, e.g. "\"mode\":1,...". */
    int (*fill_state)(char *buf, size_t cap);
    /* Apply a control request body. Return NULL on success or a short error. */
    const char *(*apply_control)(const char *body);
} viper_ha_device_t;

void viper_ha_register(httpd_handle_t httpd, const viper_ha_device_t *dev, const char *hostname);
void viper_ha_advertise(const viper_ha_device_t *dev);

/* Tiny readers for the flat JSON bodies Home Assistant sends. */
bool viper_ha_json_int(const char *body, const char *key, int *out);
bool viper_ha_json_bool(const char *body, const char *key, bool *out);
bool viper_ha_json_str(const char *body, const char *key, char *out, size_t cap);

/* Copy src into dst as JSON string content (no surrounding quotes). */
void viper_ha_json_escape(char *dst, size_t cap, const char *src);
