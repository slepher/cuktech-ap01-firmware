/* SPDX-License-Identifier: Apache-2.0 */
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>
#ifdef __NuttX__
#include <sys/mount.h>
#endif
#ifndef AP01_SIM_STATE_PATH
#define AP01_SIM_STATE_PATH "/ap01/ap01-sim-state.bin"
#endif

static uint64_t g_ap01_sim_weather_due, g_ap01_sim_binding_due;
static uint64_t g_ap01_sim_protocol_due, g_ap01_sim_ota_due, g_ap01_sim_update_due;
static uint64_t g_ap01_sim_sample_due;
static unsigned int g_ap01_sim_update_fault;
static unsigned int g_ap01_sim_weather_fault, g_ap01_sim_binding_fault;
static unsigned int g_ap01_sim_protocol_fault, g_ap01_sim_ota_fault;
static unsigned int g_ap01_sim_protocol_bank, g_ap01_sim_protocol_port;
static bool g_ap01_sim_store_invalid;
static unsigned int g_ap01_sim_capacity_remainder[AP01_SIM_GROUPS][AP01_SIM_PORTS];

static ap01_sim_port_t *ap01_sim_get_port(unsigned int bank, unsigned int port)
{
  if (port >= AP01_SIM_PORTS || bank > AP01_SIM_LOCAL_BANK) return NULL;
  return bank == AP01_SIM_LOCAL_BANK ? &g_ap01_sim.ports[port] : &g_ap01_sim.banks[bank].ports[port];
}

static uint64_t ap01_sim_millis(void)
{
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return (uint64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static unsigned int ap01_sim_take_fault(void)
{
  unsigned int fault = g_ap01_sim.next_fault;
  if (g_ap01_sim.next_failure && fault == 0) fault = 1;
  g_ap01_sim.next_failure = false;
  g_ap01_sim.next_fault = 0;
  return fault;
}

static bool ap01_sim_reply(const char *operation, enum ap01_sim_status_e status,
                            const char *stage, const char *error)
{
  ++g_ap01_sim.reply.sequence;
  g_ap01_sim.reply.status = status;
  snprintf(g_ap01_sim.reply.operation, sizeof(g_ap01_sim.reply.operation), "%s", operation);
  snprintf(g_ap01_sim.reply.stage, sizeof(g_ap01_sim.reply.stage), "%s", stage);
  snprintf(g_ap01_sim.reply.error, sizeof(g_ap01_sim.reply.error), "%s", error);
  snprintf(g_ap01_sim.reply.action_hint, sizeof(g_ap01_sim.reply.action_hint), "%s",
           status == AP01_SIM_TIMEOUT ? "retry-or-cancel" :
           status == AP01_SIM_ERROR ? "inspect-state-and-retry" : "");
  ++g_ap01_sim.revision;
  printf("SERVICE sequence=%u operation=%s status=%u stage=%s error=%s\n",
    g_ap01_sim.reply.sequence, operation, status, stage, error[0] ? error : "none");
  return status == AP01_SIM_OK || status == AP01_SIM_PENDING;
}

static bool ap01_sim_command(const char *operation)
{
  unsigned int fault = ap01_sim_take_fault();
  if (fault) return ap01_sim_reply(operation, fault == 2 ? AP01_SIM_TIMEOUT : AP01_SIM_ERROR,
                                  "mock-transport", fault == 2 ? "timeout" : "injected-failure");
  return true;
}

static void ap01_sim_invalidate_protocol(unsigned bank, unsigned port)
{
  ap01_sim_port_t *p = ap01_sim_get_port(bank, port);
  if (p->protocol_status != AP01_SIM_ERROR) p->protocol_status = AP01_SIM_IDLE;
  p->protocol_mask = 0;
  if (g_ap01_sim_protocol_due && bank == g_ap01_sim_protocol_bank && port == g_ap01_sim_protocol_port)
    {
      g_ap01_sim_protocol_due = 0; p->protocol_status = AP01_SIM_ERROR;
      ap01_sim_reply("protocol-detect", AP01_SIM_ERROR, "device", "usb-device-changed");
    }
}

static uint32_t ap01_sim_crc(const uint8_t *data, size_t length)
{
  uint32_t crc = 0xffffffffU;
  for (size_t i = 0; i < length; ++i)
    {
      crc ^= data[i];
      for (unsigned bit = 0; bit < 8; ++bit)
        crc = (crc >> 1) ^ (0xedb88320U & (0U - (crc & 1U)));
    }
  return ~crc;
}

static void ap01_sim_put32(uint8_t **out, uint32_t value)
{
  for (unsigned i = 0; i < 4; ++i) *(*out)++ = (uint8_t)(value >> (8 * i));
}

static uint32_t ap01_sim_get32(const uint8_t **in)
{
  uint32_t value = 0;
  for (unsigned i = 0; i < 4; ++i) value |= (uint32_t)*(*in)++ << (8 * i);
  return value;
}

/* 13-byte explicit header + 12 physical-port configuration records + strings
 * and CRC fit within AP01_SIM_CONFIG_MAX bytes. Telemetry/history are intentionally not saved. */
static size_t ap01_sim_encode(uint8_t data[AP01_SIM_CONFIG_MAX])
{
  uint8_t *out = data;
  memcpy(out, "AP01SCF1", 8); out += 8;
  *out++ = 1; *out++ = AP01_SIM_GROUPS; *out++ = AP01_SIM_PORTS;
  out += 2;
  *out++ = g_ap01_sim.settings.enabled[0];
  *out++ = g_ap01_sim.settings.enabled[1];
  *out++ = g_ap01_sim.settings.brightness;
  *out++ = g_ap01_sim.settings.hour12;
  *out++ = g_ap01_sim.settings.output_mode;
  *out++ = g_ap01_sim.settings.pet;
  *out++ = g_ap01_sim.settings.guide_completed;
  ap01_sim_put32(&out, g_ap01_sim.settings.saver_seconds);
  ap01_sim_put32(&out, g_ap01_sim.settings.blank_seconds);
  *out++ = g_ap01_sim.settings.saver_mode;
  *out++ = g_ap01_sim.wifi_configured; *out++ = g_ap01_sim.bound;
  ap01_sim_put32(&out, g_ap01_sim.firmware_version);
  ap01_sim_put32(&out, g_ap01_sim.device_firmware_version);
  for (unsigned bank = 0; bank < AP01_SIM_GROUPS; ++bank)
    for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
      {
        const ap01_sim_port_t *p = ap01_sim_get_port(bank, port);
        *out++ = p->enabled; *out++ = p->safe_enabled;
        *out++ = p->safe_mode; *out++ = p->protocol;
        ap01_sim_put32(&out, p->safe_limit);
        ap01_sim_put32(&out, p->protocol_disabled_mask);
      }
  size_t ssid = strnlen(g_ap01_sim.ssid, sizeof(g_ap01_sim.ssid));
  size_t location = strnlen(g_ap01_sim.weather.location, sizeof(g_ap01_sim.weather.location));
  if (ssid == sizeof(g_ap01_sim.ssid) || location == sizeof(g_ap01_sim.weather.location)) return 0;
  *out++ = ssid; memcpy(out, g_ap01_sim.ssid, ssid); out += ssid;
  *out++ = location; memcpy(out, g_ap01_sim.weather.location, location); out += location;
  size_t payload = (size_t)(out - data) - 13;
  data[11] = payload & 255; data[12] = payload >> 8;
  uint32_t crc = ap01_sim_crc(data, out - data);
  ap01_sim_put32(&out, crc);
  return out - data;
}

static bool ap01_sim_decode(const uint8_t *data, size_t length)
{
  if (length < 128 || length > AP01_SIM_CONFIG_MAX || memcmp(data, "AP01SCF1", 8) ||
      data[8] != 1 || data[9] != AP01_SIM_GROUPS || data[10] != AP01_SIM_PORTS ||
      ((size_t)data[11] | (size_t)data[12] << 8) + 17 != length) return false;
  const uint8_t *checksum = data + length - 4;
  if (ap01_sim_get32(&checksum) != ap01_sim_crc(data, length - 4)) return false;
  const uint8_t *in = data + 13;
  ap01_sim_settings_t settings;
  memset(&settings, 0, sizeof(settings));
  for (unsigned i = 0; i < 2; ++i) { if (*in > 1) return false; settings.enabled[i] = *in++; }
  settings.brightness = *in++; if (settings.brightness > 11 || *in > 1) return false;
  settings.hour12 = *in++; settings.output_mode = *in++; settings.pet = *in++;
  if (settings.output_mode > 2 || settings.pet > 4 || *in > 1) return false;
  settings.guide_completed = *in++; settings.saver_seconds = ap01_sim_get32(&in);
  settings.blank_seconds = ap01_sim_get32(&in); settings.saver_mode = *in++;
  if (settings.saver_seconds > 3600 || settings.blank_seconds > 3600 ||
      settings.saver_mode < 1 || settings.saver_mode > 3 || in[0] > 1 || in[1] > 1) return false;
  bool configured = *in++, bound = *in++;
  unsigned firmware_version = ap01_sim_get32(&in), device_version = ap01_sim_get32(&in);
  if (!firmware_version || firmware_version > 99999999 || !device_version || device_version > 99999999) return false;
  struct { bool enabled, safe; unsigned mode, protocol, limit, disabled; } ports[AP01_SIM_GROUPS][AP01_SIM_PORTS];
  for (unsigned bank = 0; bank < AP01_SIM_GROUPS; ++bank)
    for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
      {
        if ((size_t)(data + length - 4 - in) < 12 || in[0] > 1 || in[1] > 1) return false;
        ports[bank][port].enabled = *in++; ports[bank][port].safe = *in++;
        ports[bank][port].mode = *in++; ports[bank][port].protocol = *in++;
        ports[bank][port].limit = ap01_sim_get32(&in);
        ports[bank][port].disabled = ap01_sim_get32(&in);
        if (ports[bank][port].mode > 3 || ports[bank][port].protocol > 2 ||
            ports[bank][port].disabled > 7 || ports[bank][port].limit > 86400) return false;
      }
  if (in >= data + length - 4) return false;
  unsigned ssid_length = *in++;
  if (ssid_length > 32 || (size_t)(data + length - 4 - in) < ssid_length + 1) return false;
  if (memchr(in, 0, ssid_length)) return false;
  char ssid[33]; memcpy(ssid, in, ssid_length); ssid[ssid_length] = 0; in += ssid_length;
  unsigned location_length = *in++;
  if (location_length > 47 || (size_t)(data + length - 4 - in) != location_length) return false;
  if (memchr(in, 0, location_length)) return false;
  char location[48]; memcpy(location, in, location_length); location[location_length] = 0;
  g_ap01_sim.settings = settings;
  g_ap01_sim.firmware_version = firmware_version; g_ap01_sim.device_firmware_version = device_version;
  g_ap01_sim.wifi_configured = configured; g_ap01_sim.bound = bound;
  snprintf(g_ap01_sim.ssid, sizeof(g_ap01_sim.ssid), "%s", ssid);
  snprintf(g_ap01_sim.weather.location, sizeof(g_ap01_sim.weather.location), "%s", location);
  for (unsigned bank = 0; bank < AP01_SIM_GROUPS; ++bank)
    for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
      {
        ap01_sim_port_t *p = ap01_sim_get_port(bank, port);
        p->enabled = ports[bank][port].enabled; p->safe_enabled = ports[bank][port].safe;
        p->safe_mode = ports[bank][port].mode; p->protocol = ports[bank][port].protocol;
        p->safe_limit = ports[bank][port].limit; p->protocol_disabled_mask = ports[bank][port].disabled;
      }
  return true;
}

static bool ap01_sim_persist(void)
{
  if (g_ap01_sim_store_invalid)
    return ap01_sim_reply("config-save", AP01_SIM_ERROR, "validation", "restore-defaults-to-repair-config");
  uint8_t data[AP01_SIM_CONFIG_MAX]; size_t length = ap01_sim_encode(data);
  if (!length) return ap01_sim_reply("config-save", AP01_SIM_ERROR, "validation", "invalid-configuration-string");
  char temporary[256]; snprintf(temporary, sizeof(temporary), "%s.new", AP01_SIM_STATE_PATH);
  FILE *file = fopen(temporary, "wb");
  if (!file) return ap01_sim_reply("config-save", AP01_SIM_ERROR, "storage", "open-failed");
  bool ok = fwrite(data, 1, length, file) == length;
  if (fflush(file) || fsync(fileno(file))) ok = false;
  if (fclose(file)) ok = false;
  if (!ok) return ap01_sim_reply("config-save", AP01_SIM_ERROR, "storage", "write-failed");
  file = fopen(temporary, "rb"); uint8_t check[AP01_SIM_CONFIG_MAX];
  ok = file && fread(check, 1, sizeof(check), file) == length && !memcmp(data, check, length);
  if (file) fclose(file);
  if (!ok) return ap01_sim_reply("config-save", AP01_SIM_ERROR, "storage", "readback-failed");
  if (rename(temporary, AP01_SIM_STATE_PATH))
    return ap01_sim_reply("config-save", AP01_SIM_ERROR, "storage", "atomic-rename-failed");
  return true;
}

static void ap01_sim_defaults(void)
{
  g_ap01_sim.settings = (ap01_sim_settings_t){.enabled={true,true}, .brightness=10,
    .hour12=false, .output_mode=0, .pet=0, .guide_completed=false,
    .saver_seconds=180, .blank_seconds=60, .saver_mode=2};
  g_ap01_sim.wifi_configured = false; g_ap01_sim.bound = false;
  g_ap01_sim.ssid[0] = 0;
  snprintf(g_ap01_sim.weather.location, sizeof(g_ap01_sim.weather.location), "SIM 北京");
  for (unsigned bank = 0; bank < AP01_SIM_GROUPS; ++bank)
    for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
      {
        ap01_sim_port_t *p = ap01_sim_get_port(bank, port);
        p->enabled = true; p->safe_enabled = false; p->safe_mode = 0;
        p->safe_limit = 120; p->protocol = 0; p->protocol_disabled_mask = 0;
      }
}

static void ap01_sim_init(void)
{
  memset(&g_ap01_sim, 0, sizeof(g_ap01_sim)); ap01_sim_defaults();
  for (unsigned bank = 0; bank < AP01_SIM_GROUPS; ++bank)
    for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
      ap01_sim_get_port(bank, port)->supported_protocol_mask = 7;
  memset(g_ap01_sim_capacity_remainder, 0, sizeof(g_ap01_sim_capacity_remainder));
  g_ap01_sim_sample_due = 0;
  g_ap01_sim.firmware_version = 41; g_ap01_sim.offered_version = 42;
  g_ap01_sim.device_firmware_version = 10; g_ap01_sim.device_offered_version = 11;
  g_ap01_sim.ota_crc_valid = true; g_ap01_sim.ota_signed = false;
  g_ap01_sim_store_invalid = false;
  g_ap01_sim_weather_due = g_ap01_sim_binding_due = g_ap01_sim_protocol_due = g_ap01_sim_ota_due = g_ap01_sim_update_due = 0;
#ifdef __NuttX__
  if (mount(NULL, "/ap01", "hostfs", 0, "fs=/home/slepher/nuttx-ap01-sim") < 0 && errno != EEXIST)
    ap01_sim_reply("config-load", AP01_SIM_ERROR, "mount", "hostfs-mount-failed");
#endif
  FILE *file = fopen(AP01_SIM_STATE_PATH, "rb");
  if (file)
    {
      uint8_t data[AP01_SIM_CONFIG_MAX + 1]; size_t length = fread(data, 1, sizeof(data), file); fclose(file);
      if (!ap01_sim_decode(data, length))
        {
          g_ap01_sim_store_invalid = true;
          ap01_sim_reply("config-load", AP01_SIM_ERROR, "validation", "config-corrupt-or-unsupported");
        }
      else ap01_sim_reply("config-load", AP01_SIM_OK, "readback", "");
    }
  else if (errno != ENOENT) ap01_sim_reply("config-load", AP01_SIM_ERROR, "storage", "read-failed");
  ap01_wifi_init();
  ap01_wifi_offline();
  g_ap01_sim.wifi_connected = g_ap01_sim.wifi_configured;
  if (g_ap01_sim.wifi_connected) ap01_sim_weather_refresh();
}

static bool ap01_sim_save(void)
{
  return ap01_sim_command("settings-save") && ap01_sim_persist() &&
    ap01_sim_reply("settings-save", AP01_SIM_OK, "committed", "");
}

static bool ap01_sim_apply_settings(const ap01_sim_settings_t *settings)
{
  if (!settings || settings->brightness > 11 || settings->output_mode > 2 ||
      settings->pet > 4 || settings->saver_seconds > 3600 ||
      settings->blank_seconds > 3600 || settings->saver_mode < 1 || settings->saver_mode > 3)
    return ap01_sim_reply("settings-save", AP01_SIM_ERROR, "validation", "invalid-settings");
  if (!ap01_sim_command("settings-save")) return false;
  ap01_sim_settings_t previous = g_ap01_sim.settings; g_ap01_sim.settings = *settings;
  if (!ap01_sim_persist()) { g_ap01_sim.settings = previous; return false; }
  return ap01_sim_reply("settings-save", AP01_SIM_OK, "committed", "");
}

static bool ap01_sim_factory_reset(void)
{
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK)
    return ap01_sim_reply("factory-reset", AP01_SIM_ERROR, "busy", "update-in-progress-or-awaiting-restart");
  if (!ap01_sim_command("factory-reset")) return false;
  uint8_t previous[AP01_SIM_CONFIG_MAX]; size_t length = ap01_sim_encode(previous);
  bool invalid = g_ap01_sim_store_invalid; g_ap01_sim_store_invalid = false;
  ap01_sim_defaults();
  if (!ap01_sim_persist())
    { ap01_sim_decode(previous, length); g_ap01_sim_store_invalid = invalid; return false; }
  if (!ap01_wifi_reset()) return false;
  g_ap01_sim.wifi_connected = false; g_ap01_sim.binding = AP01_SIM_IDLE;
  g_ap01_sim.weather.status = AP01_SIM_IDLE; g_ap01_sim.ota = AP01_SIM_IDLE;
  g_ap01_sim_weather_due = g_ap01_sim_binding_due = g_ap01_sim_protocol_due = g_ap01_sim_ota_due = g_ap01_sim_update_due = 0;
  g_ap01_sim.update_check = AP01_SIM_IDLE;
  for (unsigned bank = 0; bank < AP01_SIM_GROUPS; ++bank)
    for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
      { ap01_sim_get_port(bank, port)->protocol_status = AP01_SIM_IDLE; ap01_sim_get_port(bank, port)->protocol_mask = 0; }
  return ap01_sim_reply("factory-reset", AP01_SIM_OK, "committed", "");
}

static void ap01_sim_connect(unsigned int bank, bool connected)
{
  if (bank >= AP01_SIM_BANKS) { ap01_sim_reply("device-connect", AP01_SIM_ERROR, "validation", "invalid-bank"); return; }
  ap01_sim_bank_t *b = &g_ap01_sim.banks[bank]; b->connected = connected;
  if (connected)
    {
      g_ap01_sim.charger_connected = true; g_ap01_sim.charger_temperature = 34;
      for (unsigned i = 0; i < AP01_SIM_PORTS; ++i)
        {
          g_ap01_sim.ports[i].capabilities = AP01_SIM_CAP_SAFE | AP01_SIM_CAP_PROTOCOL;
          g_ap01_sim.ports[i].max_watts = i == 0 ? 100 : i == 1 ? 65 : 22;
        }
    }
  b->battery = bank ? 43 : 78; b->temperature = bank ? 37 : 32;
  b->remaining_minutes = bank ? 96 : 124;
  for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
    {
      ap01_sim_port_t *p = &b->ports[port];
      p->capabilities = connected ? AP01_SIM_CAP_SAFE | AP01_SIM_CAP_PROTOCOL : 0;
      p->connected = connected && port < 2; p->input = false;
      p->bms_online = p->connected && port == 0; p->battery = port ? 83 : 67;
      p->cable_amps = port == 0 ? 5 : 3; p->max_watts = port == 0 ? 100 : port == 1 ? 65 : 22;
      p->voltage_mv = p->connected ? (port ? 20000 : 9000) : 0;
      p->current_ma = p->connected && p->enabled ? (port ? 2500 : 2200) : 0;
      snprintf(p->device_name, sizeof(p->device_name), "%s", port ? "SIM Laptop" : "SIM Phone");
      ap01_sim_invalidate_protocol(bank, port);
    }
  ap01_sim_port_t *local = &g_ap01_sim.ports[bank];
  local->connected = connected; local->bms_online = connected;
  local->battery = b->battery; local->cable_amps = 5;
  local->max_watts = 100; local->voltage_mv = connected ? 20000 : 0;
  local->current_ma = connected && local->enabled ? 3500 : 0;
  snprintf(local->device_name, sizeof(local->device_name), "SIM Power Bank C%u", bank + 1);
  ap01_sim_invalidate_protocol(AP01_SIM_LOCAL_BANK, bank);
  ap01_sim_reply("device-connect", AP01_SIM_OK, connected ? "connected" : "disconnected", "");
}

static bool ap01_sim_device_connect(unsigned int bank, unsigned int port, bool connected)
{
  ap01_sim_port_t *p = ap01_sim_get_port(bank, port);
  if (!p) return ap01_sim_reply("usb-connect", AP01_SIM_ERROR, "validation", "invalid-port");
  /* A USB device is distinct from a CUKTECH power bank. Only the explicit
   * bank-connect event creates the corresponding C1/C2 overview. */
  if (bank == AP01_SIM_LOCAL_BANK && port < AP01_SIM_BANKS && g_ap01_sim.banks[port].connected)
    ap01_sim_connect(port, false);
  if (bank == AP01_SIM_LOCAL_BANK && connected) g_ap01_sim.charger_connected = true;
  p->connected = connected; p->voltage_mv = connected ? 9000 : 0;
  p->bms_online = false; p->battery = 0; p->input = false;
  p->current_ma = connected && p->enabled ? 1800 : 0;
  p->capabilities = AP01_SIM_CAP_SAFE | AP01_SIM_CAP_PROTOCOL;
  p->cable_amps = 3; p->max_watts = 22;
  snprintf(p->device_name, sizeof(p->device_name), "SIM USB Device");
  ap01_sim_invalidate_protocol(bank, port);
  return ap01_sim_reply("usb-connect", AP01_SIM_OK, connected ? "connected" : "disconnected", "");
}

static bool ap01_sim_port_available(unsigned int bank, unsigned int port, unsigned capability)
{
  if (bank > AP01_SIM_LOCAL_BANK || port >= AP01_SIM_PORTS)
    return ap01_sim_reply("port-command", AP01_SIM_ERROR, "validation", "invalid-port");
  if (!g_ap01_sim.charger_connected)
    return ap01_sim_reply("port-command", AP01_SIM_ERROR, "device", "charger-disconnected");
  if (!(bank == AP01_SIM_LOCAL_BANK ? g_ap01_sim.charger_connected : g_ap01_sim.banks[bank].connected))
    return ap01_sim_reply("port-command", AP01_SIM_ERROR, "device", "device-disconnected");
  if (capability && !(ap01_sim_get_port(bank, port)->capabilities & capability))
    return ap01_sim_reply("port-command", AP01_SIM_ERROR, "capability", "capability-not-supported");
  return true;
}

static bool ap01_sim_set_mode(unsigned int mode)
{
  if (mode > 2) return ap01_sim_reply("output-mode", AP01_SIM_ERROR, "validation", "invalid-mode");
  if (!ap01_sim_command("output-mode")) return false;
  unsigned old = g_ap01_sim.settings.output_mode; g_ap01_sim.settings.output_mode = mode;
  if (!ap01_sim_persist()) { g_ap01_sim.settings.output_mode = old; return false; }
  return ap01_sim_reply("output-mode", AP01_SIM_OK, "committed", "");
}

static bool ap01_sim_set_port(unsigned int bank, unsigned int port, bool enabled)
{
  if (!ap01_sim_port_available(bank, port, 0) || !ap01_sim_command("port-switch")) return false;
  ap01_sim_port_t *p = ap01_sim_get_port(bank, port); bool old = p->enabled;
  p->enabled = enabled;
  if (!ap01_sim_persist()) { p->enabled = old; return false; }
  p->current_ma = enabled && p->connected ? (port ? 2500 : 2200) : 0;
  return ap01_sim_reply("port-switch", AP01_SIM_OK, "committed", "");
}

static bool ap01_sim_set_safe(unsigned int bank, unsigned int port, bool enabled,
                              unsigned int mode, unsigned int limit)
{
  if (mode > 3 || limit > 86400) return ap01_sim_reply("safe-charge", AP01_SIM_ERROR, "validation", "invalid-setting");
  if (!ap01_sim_port_available(bank, port, AP01_SIM_CAP_SAFE) || !ap01_sim_command("safe-charge")) return false;
  ap01_sim_port_t *p = ap01_sim_get_port(bank, port);
  bool old = p->safe_enabled; unsigned old_mode = p->safe_mode, old_limit = p->safe_limit;
  p->safe_enabled = enabled; p->safe_mode = mode; p->safe_limit = limit;
  if (!ap01_sim_persist()) { p->safe_enabled = old; p->safe_mode = old_mode; p->safe_limit = old_limit; return false; }
  return ap01_sim_reply("safe-charge", AP01_SIM_OK, "committed", "");
}

static bool ap01_sim_protocol_confirm(unsigned int bank, unsigned int port, unsigned int disabled_mask)
{
  if (disabled_mask > 7) return ap01_sim_reply("protocol-confirm", AP01_SIM_ERROR, "validation", "invalid-mask");
  if (!ap01_sim_port_available(bank, port, AP01_SIM_CAP_PROTOCOL)) return false;
  ap01_sim_port_t *result = ap01_sim_get_port(bank, port);
  if (!result->connected || result->protocol_status != AP01_SIM_OK || bank != g_ap01_sim_protocol_bank || port != g_ap01_sim_protocol_port)
    return ap01_sim_reply("protocol-confirm", AP01_SIM_ERROR, "transaction", "no-current-successful-detection");
  if (!ap01_sim_command("protocol-confirm")) return false;
  ap01_sim_port_t *p = ap01_sim_get_port(bank, port); unsigned old = p->protocol_disabled_mask;
  p->protocol_disabled_mask = disabled_mask;
  if (!ap01_sim_persist()) { p->protocol_disabled_mask = old; return false; }
  p->protocol_status = AP01_SIM_IDLE;
  return ap01_sim_reply("protocol-confirm", AP01_SIM_OK, "committed", "");
}

static bool ap01_sim_protocol_start(unsigned int bank, unsigned int port)
{
  if (!ap01_sim_port_available(bank, port, AP01_SIM_CAP_PROTOCOL)) return false;
  if (!ap01_sim_get_port(bank, port)->connected)
    return ap01_sim_reply("protocol-detect", AP01_SIM_ERROR, "device", "usb-device-disconnected");
  if (g_ap01_sim_protocol_due) return ap01_sim_reply("protocol-detect", AP01_SIM_ERROR, "busy", "detection-in-progress");
  g_ap01_sim_protocol_bank = bank; g_ap01_sim_protocol_port = port;
  g_ap01_sim_protocol_fault = ap01_sim_take_fault();
  ap01_sim_get_port(bank, port)->protocol_status = AP01_SIM_PENDING;
  g_ap01_sim_protocol_due = ap01_sim_millis() + 2000;
  return ap01_sim_reply("protocol-detect", AP01_SIM_PENDING, "detecting", "");
}

static bool ap01_sim_protocol_cancel(void)
{
  g_ap01_sim_protocol_due = 0;
  ap01_sim_get_port(g_ap01_sim_protocol_bank, g_ap01_sim_protocol_port)->protocol_status = AP01_SIM_IDLE;
  return ap01_sim_reply("protocol-cancel", AP01_SIM_OK, "cancelled", "");
}

static bool ap01_sim_wifi_configure(const char *ssid)
{
  if (!ssid || !ssid[0] || strlen(ssid) > 32)
    return ap01_sim_reply("wifi-configure", AP01_SIM_ERROR, "validation", "invalid-ssid");
  if (!ap01_sim_command("wifi-configure")) return false;
  char old[33]; memcpy(old, g_ap01_sim.ssid, sizeof(old)); bool configured = g_ap01_sim.wifi_configured;
  snprintf(g_ap01_sim.ssid, sizeof(g_ap01_sim.ssid), "%s", ssid); g_ap01_sim.wifi_configured = true;
  if (!ap01_sim_persist()) { memcpy(g_ap01_sim.ssid, old, sizeof(old)); g_ap01_sim.wifi_configured = configured; return false; }
  g_ap01_sim.wifi_connected = true;
  return ap01_sim_reply("wifi-configure", AP01_SIM_OK, "connected", "");
}

static void ap01_sim_wifi_disconnect(void)
{
  g_ap01_sim.wifi_connected = false;
  if (g_ap01_sim_weather_due) g_ap01_sim_weather_fault = 1;
  if (g_ap01_sim_binding_due) g_ap01_sim_binding_fault = 1;
  if (g_ap01_sim_update_due) g_ap01_sim_update_fault = 1;
  if (g_ap01_sim_ota_due) g_ap01_sim_ota_fault = 1;
  ap01_sim_reply("wifi", AP01_SIM_OK, "disconnected", "");
}

static void ap01_sim_charger_connect(bool connected)
{
  g_ap01_sim.charger_connected = connected;
  if (connected)
    {
      g_ap01_sim.charger_temperature = 34;
      for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
        {
          g_ap01_sim.ports[port].capabilities = AP01_SIM_CAP_SAFE | AP01_SIM_CAP_PROTOCOL;
          g_ap01_sim.ports[port].max_watts = port == 0 ? 100 : port == 1 ? 65 : 22;
        }
    }
  else
    {
      g_ap01_sim.device_recovery_required = false;
      if (g_ap01_sim_update_due && g_ap01_sim.update_target == 1) g_ap01_sim_update_fault = 1;
      if (g_ap01_sim_ota_due && g_ap01_sim.ota_target == 1) g_ap01_sim_ota_fault = 1;
      for (unsigned bank = 0; bank < AP01_SIM_BANKS; ++bank) ap01_sim_connect(bank, false);
      for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
        {
          ap01_sim_port_t *p = &g_ap01_sim.ports[port];
          p->connected = false; p->bms_online = false; p->input = false;
          p->voltage_mv = p->current_ma = p->capabilities = 0;
          ap01_sim_invalidate_protocol(AP01_SIM_LOCAL_BANK, port);
        }
    }
  ap01_sim_reply("charger", AP01_SIM_OK, connected ? "connected" : "disconnected", "");
}

static bool ap01_sim_weather_refresh(void)
{
  if (g_ap01_sim_weather_due) return ap01_sim_reply("weather-refresh", AP01_SIM_ERROR, "busy", "request-in-progress");
  if (!g_ap01_sim.wifi_connected) return ap01_sim_reply("weather-refresh", AP01_SIM_ERROR, "network", "wifi-disconnected");
  g_ap01_sim_weather_fault = ap01_sim_take_fault();
  g_ap01_sim.weather.status = AP01_SIM_PENDING; g_ap01_sim_weather_due = ap01_sim_millis() + 1000;
  return ap01_sim_reply("weather-refresh", AP01_SIM_PENDING, "requesting", "");
}

static bool ap01_sim_binding_start(void)
{
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK)
    return ap01_sim_reply("binding-start", AP01_SIM_ERROR, "busy", "update-in-progress-or-awaiting-restart");
  if (g_ap01_sim_binding_due) return ap01_sim_reply("binding-start", AP01_SIM_ERROR, "busy", "binding-in-progress");
  if (!g_ap01_sim.wifi_connected) return ap01_sim_reply("binding-start", AP01_SIM_ERROR, "network", "wifi-disconnected");
  g_ap01_sim_binding_fault = ap01_sim_take_fault();
  g_ap01_sim.binding = AP01_SIM_PENDING; g_ap01_sim_binding_due = ap01_sim_millis() + 1500;
  return ap01_sim_reply("binding-start", AP01_SIM_PENDING, "pairing", "");
}

static bool ap01_sim_binding_cancel(void)
{
  g_ap01_sim_binding_due = 0; g_ap01_sim.binding = AP01_SIM_IDLE;
  return ap01_sim_reply("binding-cancel", AP01_SIM_OK, "cancelled", "");
}

static bool ap01_sim_update_check(unsigned int target)
{
  if (g_ap01_sim.binding == AP01_SIM_PENDING)
    return ap01_sim_reply("update-check", AP01_SIM_ERROR, "busy", "binding-in-progress");
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK)
    return ap01_sim_reply("update-check", AP01_SIM_ERROR, "busy", "update-in-progress-or-awaiting-restart");
  if (g_ap01_sim_update_due) return ap01_sim_reply("update-check", AP01_SIM_ERROR, "busy", "check-in-progress");
  if (target > 1) return ap01_sim_reply("update-check", AP01_SIM_ERROR, "validation", "invalid-target");
  if (!g_ap01_sim.wifi_connected) return ap01_sim_reply("update-check", AP01_SIM_ERROR, "network", "wifi-disconnected");
  if (target && !g_ap01_sim.charger_connected) return ap01_sim_reply("update-check", AP01_SIM_ERROR, "device", "charger-disconnected");
  g_ap01_sim.update_target = target; g_ap01_sim_update_fault = ap01_sim_take_fault();
  g_ap01_sim.update_check = AP01_SIM_PENDING; g_ap01_sim_update_due = ap01_sim_millis() + 1000;
  return ap01_sim_reply("update-check", AP01_SIM_PENDING, "requesting", "");
}

static bool ap01_sim_update_cancel(void)
{
  g_ap01_sim_update_due = 0; g_ap01_sim.update_check = AP01_SIM_IDLE;
  return ap01_sim_reply("update-cancel", AP01_SIM_OK, "cancelled", "");
}

static bool ap01_sim_ota_prepare(const char *model, unsigned int version, const uint8_t *data,
                                  size_t length, uint32_t crc, bool is_signed)
{
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK)
    return ap01_sim_reply("ota-package", AP01_SIM_ERROR, "busy", "update-in-progress-or-awaiting-restart");
  unsigned target;
  if (model && !strcmp(model, "AP01")) target = 0;
  else if (model && !strcmp(model, "TA1208")) target = 1;
  else return ap01_sim_reply("ota-package", AP01_SIM_ERROR, "compatibility", "model-mismatch");
  unsigned current = target ? g_ap01_sim.device_firmware_version : g_ap01_sim.firmware_version;
  if (!data || !length || length > 1024 * 1024 || version > 99999999 || version < current ||
      (version == current && !(target && g_ap01_sim.device_recovery_required)))
    return ap01_sim_reply("ota-package", AP01_SIM_ERROR, "validation", "invalid-length-or-version");
  if (ap01_sim_crc(data, length) != crc)
    return ap01_sim_reply("ota-package", AP01_SIM_ERROR, "integrity", "crc-mismatch");
  if (target) { g_ap01_sim.device_offered_version = version; g_ap01_sim.device_update_available = true; }
  else { g_ap01_sim.offered_version = version; g_ap01_sim.update_available = true; }
  g_ap01_sim.ota_target = target; g_ap01_sim.ota_crc_valid = true; g_ap01_sim.ota_signed = is_signed;
  g_ap01_sim.packages[target].validated = true; g_ap01_sim.packages[target].version = version;
  g_ap01_sim.packages[target].is_signed = is_signed;
  return ap01_sim_reply("ota-package", AP01_SIM_OK, "validated", "");
}

static bool ap01_sim_restart_complete(void)
{
  if (!ap01_sim_command("restart")) return false;
  if (g_ap01_sim.ota == AP01_SIM_OK)
    {
      unsigned *version = g_ap01_sim.ota_target ? &g_ap01_sim.device_firmware_version : &g_ap01_sim.firmware_version;
      unsigned old = *version;
      *version = g_ap01_sim.ota_target ? g_ap01_sim.device_offered_version : g_ap01_sim.offered_version;
      if (!ap01_sim_persist()) { *version = old; return false; }
      if (g_ap01_sim.ota_target) { g_ap01_sim.device_update_available = false; g_ap01_sim.device_recovery_required = false; }
      else g_ap01_sim.update_available = false;
      g_ap01_sim.ota = AP01_SIM_IDLE;
    }
  return ap01_sim_reply("restart", AP01_SIM_OK, "simulated-reboot", "");
}

static bool ap01_sim_ota_start(bool crc_valid, bool is_signed)
{
  (void)is_signed; /* Signature metadata belongs to the validated package. */
  if (g_ap01_sim.binding == AP01_SIM_PENDING)
    return ap01_sim_reply("ota-start", AP01_SIM_ERROR, "busy", "binding-in-progress");
  if (g_ap01_sim.ota_target > 1) return ap01_sim_reply("ota-start", AP01_SIM_ERROR, "validation", "invalid-target");
  unsigned version = g_ap01_sim.ota_target ? g_ap01_sim.device_offered_version : g_ap01_sim.offered_version;
  if (!g_ap01_sim.packages[g_ap01_sim.ota_target].validated || g_ap01_sim.packages[g_ap01_sim.ota_target].version != version)
    return ap01_sim_reply("ota-start", AP01_SIM_ERROR, "package", "validated-package-required-for-target");
  if (g_ap01_sim.ota_target && !g_ap01_sim.charger_connected) return ap01_sim_reply("ota-start", AP01_SIM_ERROR, "device", "charger-disconnected");
  if (g_ap01_sim.ota_target ?
      (g_ap01_sim.device_recovery_required ? g_ap01_sim.device_offered_version < g_ap01_sim.device_firmware_version : (!g_ap01_sim.device_update_available || g_ap01_sim.device_offered_version <= g_ap01_sim.device_firmware_version)) :
      (!g_ap01_sim.update_available || g_ap01_sim.offered_version <= g_ap01_sim.firmware_version))
    return ap01_sim_reply("ota-start", AP01_SIM_ERROR, "validation", "no-new-version");
  if (!g_ap01_sim.wifi_connected) return ap01_sim_reply("ota-start", AP01_SIM_ERROR, "network", "wifi-disconnected");
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK) return ap01_sim_reply("ota-start", AP01_SIM_ERROR, "busy", "update-in-progress-or-awaiting-restart");
  g_ap01_sim.ota_crc_valid = crc_valid; g_ap01_sim.ota_signed = g_ap01_sim.packages[g_ap01_sim.ota_target].is_signed;
  g_ap01_sim_ota_fault = ap01_sim_take_fault(); g_ap01_sim.ota = AP01_SIM_PENDING;
  g_ap01_sim.ota_progress = 0; g_ap01_sim_ota_due = ap01_sim_millis() + 200;
  return ap01_sim_reply("ota-start", AP01_SIM_PENDING, "downloading", "");
}

static bool ap01_sim_ota_cancel(void)
{
  g_ap01_sim_ota_due = 0; g_ap01_sim.ota = AP01_SIM_IDLE;
  return ap01_sim_reply("ota-cancel", AP01_SIM_OK, "cancelled", "");
}

static void ap01_sim_tick(void)
{
  uint64_t now = ap01_sim_millis();
  if (g_ap01_sim_update_due && now >= g_ap01_sim_update_due)
    {
      if (!g_ap01_sim.wifi_connected || (g_ap01_sim.update_target && !g_ap01_sim.charger_connected)) g_ap01_sim_update_fault = 1;
      g_ap01_sim_update_due = 0;
      g_ap01_sim.update_check = g_ap01_sim_update_fault == 2 ? AP01_SIM_TIMEOUT : g_ap01_sim_update_fault ? AP01_SIM_ERROR : AP01_SIM_OK;
      bool available = g_ap01_sim.update_target ? g_ap01_sim.device_offered_version > g_ap01_sim.device_firmware_version : g_ap01_sim.offered_version > g_ap01_sim.firmware_version;
      if (g_ap01_sim.update_target) g_ap01_sim.device_update_available = available && g_ap01_sim.update_check == AP01_SIM_OK;
      else g_ap01_sim.update_available = available && g_ap01_sim.update_check == AP01_SIM_OK;
      ap01_sim_reply("update-check", g_ap01_sim.update_check,
        !g_ap01_sim.wifi_connected ? "network" : g_ap01_sim.update_target && !g_ap01_sim.charger_connected ? "device" : g_ap01_sim.update_check == AP01_SIM_OK ? (available ? "offer" : "up-to-date") : "response",
        g_ap01_sim.update_check == AP01_SIM_OK ? "" : !g_ap01_sim.wifi_connected ? "wifi-disconnected" : g_ap01_sim.update_target && !g_ap01_sim.charger_connected ? "charger-disconnected" : "update-check-failed");
    }
  if (g_ap01_sim_protocol_due && now >= g_ap01_sim_protocol_due)
    {
      g_ap01_sim_protocol_due = 0;
      ap01_sim_port_t *p = ap01_sim_get_port(g_ap01_sim_protocol_bank, g_ap01_sim_protocol_port);
      if (!p->connected || !(p->capabilities & AP01_SIM_CAP_PROTOCOL) || !(g_ap01_sim_protocol_bank == AP01_SIM_LOCAL_BANK ? g_ap01_sim.charger_connected : g_ap01_sim.banks[g_ap01_sim_protocol_bank].connected)) g_ap01_sim_protocol_fault = 1;
      p->protocol_status = g_ap01_sim_protocol_fault == 2 ? AP01_SIM_TIMEOUT : g_ap01_sim_protocol_fault ? AP01_SIM_ERROR : AP01_SIM_OK;
      p->protocol_mask = p->protocol_status == AP01_SIM_OK ? p->supported_protocol_mask : 0;
      ap01_sim_reply("protocol-detect", p->protocol_status, p->connected ? "completed" : "device", p->protocol_status == AP01_SIM_OK ? "" : !p->connected ? "usb-device-disconnected" : "detection-failed");
    }
  if (g_ap01_sim_weather_due && now >= g_ap01_sim_weather_due)
    {
      g_ap01_sim_weather_due = 0;
      ap01_sim_weather_t *w = &g_ap01_sim.weather;
      if (!g_ap01_sim.wifi_connected) g_ap01_sim_weather_fault = 1;
      w->status = g_ap01_sim_weather_fault == 2 ? AP01_SIM_TIMEOUT : g_ap01_sim_weather_fault ? AP01_SIM_ERROR : AP01_SIM_OK;
      if (w->status == AP01_SIM_OK)
        {
          w->condition = 0; w->native_code = 0; w->temperature = 24; w->high = 27; w->low = 18; w->feels_like = 25;
          w->humidity = 58; w->aqi = 36; w->uvi = 4; w->sunrise_minutes = 6 * 60 + 18; w->sunset_minutes = 18 * 60 + 4;
          for (unsigned i = 0; i < 7; ++i) { w->forecast[i].condition = i % 3; w->forecast[i].native_code = 0; w->forecast[i].high = 27 - i % 4; w->forecast[i].low = 18 + i % 3; }
        }
      ap01_sim_reply("weather-refresh", w->status, g_ap01_sim.wifi_connected ? "response" : "network", w->status == AP01_SIM_OK ? "" : !g_ap01_sim.wifi_connected ? "wifi-disconnected" : "weather-request-failed");
    }
  if (g_ap01_sim_binding_due && now >= g_ap01_sim_binding_due)
    {
      g_ap01_sim_binding_due = 0;
      if (!g_ap01_sim.wifi_connected) g_ap01_sim_binding_fault = 1;
      g_ap01_sim.binding = g_ap01_sim_binding_fault == 2 ? AP01_SIM_TIMEOUT : g_ap01_sim_binding_fault ? AP01_SIM_ERROR : AP01_SIM_OK;
      bool persistence_failed = false;
      if (g_ap01_sim.binding == AP01_SIM_OK)
        { g_ap01_sim.bound = true; if (!ap01_sim_persist()) { g_ap01_sim.bound = false; g_ap01_sim.binding = AP01_SIM_ERROR; persistence_failed = true; } }
      if (!persistence_failed)
        ap01_sim_reply("binding-start", g_ap01_sim.binding, g_ap01_sim.wifi_connected ? "response" : "network", g_ap01_sim.binding == AP01_SIM_OK ? "" : !g_ap01_sim.wifi_connected ? "wifi-disconnected" : "binding-failed");
    }
  if (g_ap01_sim_ota_due && now >= g_ap01_sim_ota_due)
    {
      if (!g_ap01_sim.wifi_connected || (g_ap01_sim.ota_target && !g_ap01_sim.charger_connected)) g_ap01_sim_ota_fault = 1;
      if (g_ap01_sim_ota_fault || (!g_ap01_sim.ota_crc_valid && g_ap01_sim.ota_progress >= 80))
        {
          g_ap01_sim_ota_due = 0;
          g_ap01_sim.ota = g_ap01_sim_ota_fault == 2 ? AP01_SIM_TIMEOUT : AP01_SIM_ERROR;
          ap01_sim_reply("ota-start", g_ap01_sim.ota,
            !g_ap01_sim.wifi_connected ? "network" : g_ap01_sim.ota_target && !g_ap01_sim.charger_connected ? "device" : g_ap01_sim.ota_crc_valid ? "download" : "integrity",
            !g_ap01_sim.wifi_connected ? "wifi-disconnected" : g_ap01_sim.ota_target && !g_ap01_sim.charger_connected ? "charger-disconnected" : g_ap01_sim.ota_crc_valid ? "update-transfer-failed" : "crc-mismatch");
        }
      else if (g_ap01_sim.ota_progress == 100)
        {
          g_ap01_sim_ota_due = 0; g_ap01_sim.ota = AP01_SIM_OK;
          /* The user's 0041 requirement removes the added signature gate;
           * integrity still applies. No real flash or server is involved. */
          ap01_sim_reply("ota-start", AP01_SIM_OK, "simulated-install", "");
        }
      else { g_ap01_sim.ota_progress += 10; g_ap01_sim_ota_due = now + 200; ++g_ap01_sim.revision; }
    }
  if (now >= g_ap01_sim_sample_due)
    {
      g_ap01_sim_sample_due = now + 1000;
      for (unsigned bank = 0; bank < AP01_SIM_GROUPS; ++bank)
        {
          bool local = bank == AP01_SIM_LOCAL_BANK;
          if (!(local ? g_ap01_sim.charger_connected : g_ap01_sim.banks[bank].connected)) continue;
          unsigned total = 0;
          for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
            {
              ap01_sim_port_t *p = ap01_sim_get_port(bank, port);
              unsigned mw = p->enabled && p->connected ? p->voltage_mv * p->current_ma / 1000 : 0;
              if (mw)
                {
                  unsigned *remainder = &g_ap01_sim_capacity_remainder[bank][port];
                  *remainder += p->current_ma;
                  p->delivered_mah += *remainder / 3600; *remainder %= 3600;
                }
              if (!p->input) total += mw;
              p->history[p->history_head] = mw;
              p->history_head = (p->history_head + 1) % AP01_SIM_HISTORY;
              if (p->history_count < AP01_SIM_HISTORY) ++p->history_count;
            }
          unsigned *history = local ? g_ap01_sim.history : g_ap01_sim.banks[bank].history;
          unsigned *head = local ? &g_ap01_sim.history_head : &g_ap01_sim.banks[bank].history_head;
          unsigned *count = local ? &g_ap01_sim.history_count : &g_ap01_sim.banks[bank].history_count;
          history[*head] = total; *head = (*head + 1) % AP01_SIM_HISTORY;
          if (*count < AP01_SIM_HISTORY) ++*count;
          ++g_ap01_sim.revision;
        }
    }
}

#include "ap01-sim-wifi.h"
