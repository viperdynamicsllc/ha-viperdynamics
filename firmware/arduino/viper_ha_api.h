// Viper HA API v1 — Home Assistant discovery and control for Viper Dynamics devices.
// Spec: https://github.com/viperdynamicsllc/ha-viperdynamics/blob/main/docs/api.md
//
// Copy this file into an Arduino/ESPAsyncWebServer firmware, then:
//   1. Fill a ViperHaDevice with the model, version and three callbacks.
//   2. Call viperHaBegin(server, device, hostname) where the other routes are registered.
//   3. Call viperHaAdvertise() right after MDNS.begin() / MDNS.addService("http", ...).
// Callbacks run on the async_tcp task, like any other route handler.
#pragma once

#include <ArduinoJson.h>
#include <ESPAsyncWebServer.h>
#include <ESPmDNS.h>
#include <WiFi.h>
#include <esp_mac.h>

#define VIPER_HA_API_VERSION 1
#define VIPER_HA_MAX_BODY    1024

struct ViperHaDevice {
  const char *model;      // slug, e.g. "stargate_p4x"
  const char *modelName;  // e.g. "Stargate P4X"
  const char *fw;         // firmware version
  // Add capabilities, modes and ranges. Identity fields are filled in already.
  void (*fillInfo)(JsonObject info);
  // Add current state keys for this device's capabilities.
  void (*fillState)(JsonObject state);
  // Apply a control request. Return nullptr on success or a short error message.
  const char *(*applyControl)(JsonObjectConst body);
};

static const ViperHaDevice *s_viperHa = nullptr;
static String s_viperHaName;

// Full factory MAC, the same one hostnames are derived from: stable per unit.
static String viperHaId() {
  uint8_t mac[6];
  esp_efuse_mac_get_default(mac);
  char id[13];
  snprintf(id, sizeof(id), "%02x%02x%02x%02x%02x%02x",
           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  return String(id);
}

static void viperHaSendJson(AsyncWebServerRequest *req, int code, JsonDocument &doc) {
  String out;
  serializeJson(doc, out);
  AsyncWebServerResponse *res = req->beginResponse(code, "application/json", out);
  res->addHeader("Cache-Control", "no-store");
  req->send(res);
}

static void viperHaSendState(AsyncWebServerRequest *req) {
  JsonDocument doc;
  s_viperHa->fillState(doc.to<JsonObject>());
  viperHaSendJson(req, 200, doc);
}

static void viperHaSendError(AsyncWebServerRequest *req, int code, const char *msg) {
  JsonDocument doc;
  doc["error"] = msg;
  viperHaSendJson(req, code, doc);
}

static void viperHaBegin(AsyncWebServer &server, const ViperHaDevice &dev, const String &hostname) {
  s_viperHa = &dev;
  s_viperHaName = hostname;

  server.on("/api/info", HTTP_GET, [](AsyncWebServerRequest *req) {
    JsonDocument doc;
    JsonObject info = doc.to<JsonObject>();
    info["manufacturer"] = "Viper Dynamics";
    info["model"] = s_viperHa->model;
    info["model_name"] = s_viperHa->modelName;
    info["id"] = viperHaId();
    info["name"] = s_viperHaName;
    String mac = WiFi.macAddress();  // radio MAC, as the router sees it
    mac.toLowerCase();
    info["mac"] = mac;
    info["fw"] = s_viperHa->fw;
    info["api"] = VIPER_HA_API_VERSION;
    s_viperHa->fillInfo(info);
    viperHaSendJson(req, 200, doc);
  });

  server.on("/api/state", HTTP_GET, [](AsyncWebServerRequest *req) {
    viperHaSendState(req);
  });

  // The body arrives in chunks before the request handler runs; collect it in
  // _tempObject, which the request frees with free() when it is destroyed.
  server.on(
    "/api/control", HTTP_POST,
    [](AsyncWebServerRequest *req) {
      const char *body = (const char *)req->_tempObject;
      if (!body) {
        viperHaSendError(req, 400, "missing or oversized body");
        return;
      }
      JsonDocument doc;
      if (deserializeJson(doc, body) || !doc.is<JsonObject>()) {
        viperHaSendError(req, 400, "invalid json");
        return;
      }
      const char *err = s_viperHa->applyControl(doc.as<JsonObjectConst>());
      if (err) {
        viperHaSendError(req, 400, err);
        return;
      }
      viperHaSendState(req);
    },
    nullptr,
    [](AsyncWebServerRequest *req, uint8_t *data, size_t len, size_t index, size_t total) {
      if (total > VIPER_HA_MAX_BODY) return;
      if (index == 0) req->_tempObject = calloc(total + 1, 1);
      if (req->_tempObject && index + len <= total)
        memcpy((uint8_t *)req->_tempObject + index, data, len);
    });
}

// Advertise _viperdyn._tcp so Home Assistant discovers the device.
static void viperHaAdvertise() {
  if (!s_viperHa) return;
  MDNS.addService("viperdyn", "tcp", 80);
  MDNS.addServiceTxt("viperdyn", "tcp", "id", viperHaId().c_str());
  MDNS.addServiceTxt("viperdyn", "tcp", "model", s_viperHa->model);
  MDNS.addServiceTxt("viperdyn", "tcp", "fw", s_viperHa->fw);
  MDNS.addServiceTxt("viperdyn", "tcp", "api", String(VIPER_HA_API_VERSION).c_str());
}
