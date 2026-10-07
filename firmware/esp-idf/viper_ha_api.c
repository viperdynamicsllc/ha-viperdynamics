#include "viper_ha_api.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "esp_mac.h"
#include "esp_wifi.h"
#include "mdns.h"

#define MAX_BODY  1024
#define OUT_CAP   4096

static const viper_ha_device_t *s_dev;
static const char *s_hostname;

/* Factory MAC: stable per unit, matches what the hostname is derived from. */
static void device_id(char out[13])
{
    uint8_t mac[6] = {0};
    esp_efuse_mac_get_default(mac);
    snprintf(out, 13, "%02x%02x%02x%02x%02x%02x",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

static esp_err_t send_json(httpd_req_t *req, const char *status, const char *json)
{
    httpd_resp_set_status(req, status);
    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-store");
    return httpd_resp_sendstr(req, json);
}

static esp_err_t send_error(httpd_req_t *req, const char *msg)
{
    char buf[128], esc[96];
    viper_ha_json_escape(esc, sizeof(esc), msg);
    snprintf(buf, sizeof(buf), "{\"error\":\"%s\"}", esc);
    return send_json(req, "400 Bad Request", buf);
}

static esp_err_t send_state(httpd_req_t *req)
{
    char *buf = malloc(OUT_CAP);
    if (!buf) return httpd_resp_send_500(req);
    buf[0] = '{';
    int n = 1 + s_dev->fill_state(buf + 1, OUT_CAP - 3);
    buf[n++] = '}';
    buf[n] = 0;
    esp_err_t r = send_json(req, "200 OK", buf);
    free(buf);
    return r;
}

static esp_err_t info_get(httpd_req_t *req)
{
    char *buf = malloc(OUT_CAP);
    if (!buf) return httpd_resp_send_500(req);
    char id[13], mac_s[18] = "";
    device_id(id);
    uint8_t mac[6] = {0};
    if (esp_wifi_get_mac(WIFI_IF_STA, mac) == ESP_OK)
        snprintf(mac_s, sizeof(mac_s), "%02x:%02x:%02x:%02x:%02x:%02x",
                 mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    int n = snprintf(buf, OUT_CAP,
                     "{\"manufacturer\":\"Viper Dynamics\",\"model\":\"%s\",\"model_name\":\"%s\","
                     "\"id\":\"%s\",\"name\":\"%s\",\"mac\":\"%s\",\"fw\":\"%s\",\"api\":%d",
                     s_dev->model, s_dev->model_name, id, s_hostname ? s_hostname : "",
                     mac_s, s_dev->fw, VIPER_HA_API_VERSION);
    n += s_dev->fill_info(buf + n, OUT_CAP - n - 2);
    buf[n++] = '}';
    buf[n] = 0;
    esp_err_t r = send_json(req, "200 OK", buf);
    free(buf);
    return r;
}

static esp_err_t state_get(httpd_req_t *req)
{
    return send_state(req);
}

static esp_err_t control_post(httpd_req_t *req)
{
    if (req->content_len == 0 || req->content_len > MAX_BODY)
        return send_error(req, "missing or oversized body");
    char *body = calloc(1, req->content_len + 1);
    if (!body) return httpd_resp_send_500(req);
    size_t got = 0;
    while (got < req->content_len) {
        int r = httpd_req_recv(req, body + got, req->content_len - got);
        if (r == HTTPD_SOCK_ERR_TIMEOUT) continue;
        if (r <= 0) { free(body); return ESP_FAIL; }
        got += r;
    }
    const char *err = s_dev->apply_control(body);
    free(body);
    if (err) return send_error(req, err);
    return send_state(req);
}

void viper_ha_register(httpd_handle_t httpd, const viper_ha_device_t *dev, const char *hostname)
{
    s_dev = dev;
    s_hostname = hostname;
    const httpd_uri_t uris[] = {
        {"/api/info",    HTTP_GET,  info_get,     NULL},
        {"/api/state",   HTTP_GET,  state_get,    NULL},
        {"/api/control", HTTP_POST, control_post, NULL},
    };
    for (size_t i = 0; i < sizeof(uris) / sizeof(uris[0]); i++)
        httpd_register_uri_handler(httpd, &uris[i]);
}

void viper_ha_advertise(const viper_ha_device_t *dev)
{
    char id[13], api[4];
    device_id(id);
    snprintf(api, sizeof(api), "%d", VIPER_HA_API_VERSION);
    mdns_txt_item_t txt[] = {
        {"id", id},
        {"model", dev->model},
        {"fw", dev->fw},
        {"api", api},
    };
    mdns_service_add(NULL, "_viperdyn", "_tcp", 80, txt, sizeof(txt) / sizeof(txt[0]));
}

/* Returns a pointer to the value after "key": or NULL. */
static const char *find_value(const char *body, const char *key)
{
    char pat[48];
    snprintf(pat, sizeof(pat), "\"%s\"", key);
    const char *p = strstr(body, pat);
    if (!p) return NULL;
    p = strchr(p + strlen(pat), ':');
    if (!p) return NULL;
    p++;
    while (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r') p++;
    return p;
}

bool viper_ha_json_int(const char *body, const char *key, int *out)
{
    const char *p = find_value(body, key);
    if (!p || !(*p == '-' || (*p >= '0' && *p <= '9'))) return false;
    *out = (int)strtol(p, NULL, 10);
    return true;
}

bool viper_ha_json_bool(const char *body, const char *key, bool *out)
{
    const char *p = find_value(body, key);
    if (!p) return false;
    if (!strncmp(p, "true", 4)) { *out = true; return true; }
    if (!strncmp(p, "false", 5)) { *out = false; return true; }
    return false;
}

bool viper_ha_json_str(const char *body, const char *key, char *out, size_t cap)
{
    const char *p = find_value(body, key);
    if (!p || *p != '"' || cap == 0) return false;
    p++;
    size_t n = 0;
    while (*p && *p != '"' && n + 1 < cap) {
        if (*p == '\\' && p[1]) p++;
        out[n++] = *p++;
    }
    out[n] = 0;
    return true;
}

void viper_ha_json_escape(char *dst, size_t cap, const char *src)
{
    size_t n = 0;
    for (; src && *src && n + 2 < cap; src++) {
        char c = *src;
        if (c == '"' || c == '\\') { dst[n++] = '\\'; dst[n++] = c; }
        else if ((unsigned char)c < 0x20) dst[n++] = ' ';
        else dst[n++] = c;
    }
    if (cap) dst[n] = 0;
}
