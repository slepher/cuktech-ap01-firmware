/* SPDX-License-Identifier: Apache-2.0 */
/* Local HOSTFS test transport. Requests are atomic, bounded, and identified.
 * It models external service events; navigation still uses the keyboard. */
#ifndef TOOLS_AP01_SIM_CONTROL_H
#define TOOLS_AP01_SIM_CONTROL_H
#define AP01_SIM_REQUEST "/ap01/sim-request.txt"
#define AP01_SIM_RESPONSE "/ap01/sim-response.json"
static unsigned long g_ap01_sim_request;
static unsigned long g_ap01_sim_request_high_water;
static unsigned int g_ap01_sim_published_revision;
static bool g_ap01_sim_request_retired;
static bool g_ap01_sim_request_ok;
static uint64_t g_ap01_sim_control_session;
static uint64_t g_ap01_sim_last_request_session;
static char g_ap01_sim_last_request_line[160];
static bool ap01_ui_sim_control_ui(const char *operation, unsigned value);

static void ap01_sim_control_init(void)
{
  /* A leftover request is never replayed across a process restart. A caller
   * that was waiting for it receives an explicit unknown result instead. */
  struct timespec now;
  clock_gettime(CLOCK_REALTIME, &now);
  g_ap01_sim_control_session = (uint64_t)now.tv_sec * UINT64_C(1000000000) + now.tv_nsec;
  FILE *in = fopen(AP01_SIM_REQUEST, "r");
  if (in)
    {
      unsigned long long old_session;
      if (fscanf(in, "%llu %lu", &old_session, &g_ap01_sim_request) == 2 && g_ap01_sim_request)
        { g_ap01_sim_request_retired = true; g_ap01_sim_last_request_session = old_session; }
      fclose(in);
    }
}

static void ap01_sim_json_string(FILE *out, const char *text)
{
  fputc('"', out);
  for (const unsigned char *p = (const unsigned char *)text; *p; ++p)
    {
      if (*p == '"' || *p == '\\') fputc('\\', out);
      fputc(*p, out);
    }
  fputc('"', out);
}

static void ap01_sim_status_publish(void)
{
  FILE *out = fopen(AP01_SIM_RESPONSE ".new", "w");
  if (!out) return;
  fprintf(out, "{\"session\":%llu,\"request_session\":%llu,\"request_retired\":%u,\"request_ok\":%u,\"request_high_water\":%lu,", (unsigned long long)g_ap01_sim_control_session, (unsigned long long)g_ap01_sim_last_request_session, g_ap01_sim_request_retired, g_ap01_sim_request_ok, g_ap01_sim_request_high_water);
  fprintf(out, "\"request\":%lu,\"revision\":%u,\"reply\":{\"sequence\":%u,\"status\":%u,\"operation\":\"%s\",\"stage\":\"%s\",\"error\":\"%s\",\"action\":\"%s\"},",
    g_ap01_sim_request, g_ap01_sim.revision, g_ap01_sim.reply.sequence,
    g_ap01_sim.reply.status, g_ap01_sim.reply.operation, g_ap01_sim.reply.stage,
    g_ap01_sim.reply.error, g_ap01_sim.reply.action_hint);
  fprintf(out, "\"page\":\"%s\",\"mode\":%u,\"selection\":%u,\"wifi\":%u,\"configured\":%u,\"bound\":%u,\"binding\":%u,\"weather\":%u,\"charger\":%u,\"ota\":%u,\"progress\":%u,\"update_check\":%u,\"firmware\":[%u,%u],",
    ap01_ui_page_name(g_ap01_ui_page), g_ap01_ui_mode, g_ap01_ui_selection,
    g_ap01_sim.wifi_connected, g_ap01_sim.wifi_configured, g_ap01_sim.bound,
    g_ap01_sim.binding, g_ap01_sim.weather.status, g_ap01_sim.charger_connected,
    g_ap01_sim.ota, g_ap01_sim.ota_progress, g_ap01_sim.update_check,
    g_ap01_sim.firmware_version, g_ap01_sim.device_firmware_version);
  fprintf(out, "\"wifi_active\":%d,\"wifi_profiles\":[", g_ap01_wifi_active);
  bool first_wifi = true;
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
    if (g_ap01_wifi[i].length)
      {
        fprintf(out, "%s{\"slot\":%u,\"ssid\":", first_wifi ? "" : ",", i);
        ap01_sim_json_string(out, g_ap01_wifi[i].ssid);
        fputc('}', out); first_wifi = false;
      }
  fputs("],", out);
  fprintf(out, "\"ui\":{\"charge_view\":%u,\"charge_item\":%u,\"charge_popup\":%u,\"guide_active\":%u,\"guide_stage\":%u,\"guide_option\":%u,\"system\":%u,\"saver\":%u,\"boot\":%u},",
    g_ap01_ui_charge_view, g_ap01_ui_charge_index, g_ap01_ui_charge_popup,
    g_ap01_ui_guide_active, g_ap01_ui_guide_stage, g_ap01_ui_option,
    g_ap01_ui_system_view, g_ap01_ui_saver_kind, g_ap01_ui_boot_running);
  fprintf(out, "\"device_recovery\":%u,\"ota_target\":%u,", g_ap01_sim.device_recovery_required, g_ap01_sim.ota_target);
  fprintf(out, "\"packages\":[{\"valid\":%u,\"version\":%u,\"signed\":%u},{\"valid\":%u,\"version\":%u,\"signed\":%u}],",
    g_ap01_sim.packages[0].validated, g_ap01_sim.packages[0].version, g_ap01_sim.packages[0].is_signed,
    g_ap01_sim.packages[1].validated, g_ap01_sim.packages[1].version, g_ap01_sim.packages[1].is_signed);
  fprintf(out, "\"settings\":{\"mode\":%u,\"brightness\":%u,\"hour12\":%u,\"pet\":%u,\"guide\":%u,\"always_on\":%u,\"saver\":%u},\"banks\":[%u,%u],\"ports\":[",
    g_ap01_sim.settings.output_mode, g_ap01_sim.settings.brightness,
    g_ap01_sim.settings.hour12, g_ap01_sim.settings.pet, g_ap01_sim.settings.guide_completed,
    g_ap01_sim.settings.enabled[0], g_ap01_sim.settings.enabled[1],
    g_ap01_sim.banks[0].connected, g_ap01_sim.banks[1].connected);
  for (unsigned bank = 0; bank < AP01_SIM_GROUPS; ++bank)
    for (unsigned port = 0; port < AP01_SIM_PORTS; ++port)
      {
        ap01_sim_port_t *p = ap01_sim_get_port(bank, port);
        fprintf(out, "%s{\"bank\":%u,\"port\":%u,\"connected\":%u,\"enabled\":%u,\"mv\":%u,\"ma\":%u,\"safe\":%u,\"protocol\":%u,\"disabled\":%u,\"history\":%u}",
          bank || port ? "," : "", bank, port, p->connected, p->enabled,
          p->voltage_mv, p->current_ma, p->safe_enabled, p->protocol_status,
          p->protocol_disabled_mask, p->history_count);
      }
  fputs("]}\n", out);
  bool ok = !ferror(out) && fflush(out) == 0;
  if (fclose(out)) ok = false;
  if (ok && rename(AP01_SIM_RESPONSE ".new", AP01_SIM_RESPONSE) == 0)
    g_ap01_sim_published_revision = g_ap01_sim.revision;
}

static bool ap01_sim_control_poll(void)
{
  unsigned revision = g_ap01_sim.revision;
  FILE *in = fopen(AP01_SIM_REQUEST, "r");
  if (in)
    {
      char line[160] = {0}, operation[32], extra;
      unsigned long id = 0;
      unsigned long long request_session = 0;
      unsigned a, b, c, d;
      bool valid = fgets(line, sizeof(line), in) &&
        sscanf(line, "%llu %lu %31s %u %u %u %u %c", &request_session, &id, operation, &a, &b, &c, &d, &extra) == 7 &&
        feof(in) == 0; /* exactly one newline-terminated request */
      if (valid) { int tail = fgetc(in); valid = tail == EOF; }
      fclose(in);
      if (id && (id != g_ap01_sim_request || request_session != g_ap01_sim_last_request_session || strcmp(line, g_ap01_sim_last_request_line)))
        {
          g_ap01_sim_request = id;
          g_ap01_sim_last_request_session = request_session;
          snprintf(g_ap01_sim_last_request_line, sizeof(g_ap01_sim_last_request_line), "%s", line);
          g_ap01_sim_request_retired = false;
          g_ap01_sim_request_ok = false;
          if (!valid) ap01_sim_reply("control", AP01_SIM_ERROR, "parse", "invalid-request");
          else if (request_session != g_ap01_sim_control_session)
            {
              g_ap01_sim_request_retired = true;
              ap01_sim_reply("control", AP01_SIM_ERROR, "session", "previous-session-result-unknown");
            }
          else if (id <= g_ap01_sim_request_high_water)
            ap01_sim_reply("control", AP01_SIM_ERROR, "replay", "request-id-already-retired");
          else
            {
          g_ap01_sim_request_high_water = id;
          if (!strcmp(operation, "status")) { /* observational */ }
          else if (!strcmp(operation, "bank")) ap01_sim_connect(a, b != 0);
          else if (!strcmp(operation, "device")) ap01_sim_device_connect(a, b, c != 0);
          else if (!strcmp(operation, "charger"))
            ap01_sim_charger_connect(a != 0);
          else if (!strcmp(operation, "recovery") && a <= 1)
            {
              g_ap01_sim.device_recovery_required = a != 0;
              if (a) g_ap01_sim.charger_connected = true;
              ap01_sim_reply(operation, AP01_SIM_OK, "device-event", "");
            }
          else if (!strcmp(operation, "wifi-put")) ap01_wifi_import_file(a, ".wifi-input");
          else if (!strcmp(operation, "wifi-delete"))
            { ap01_sim_wifi_profile empty = {0}; ap01_wifi_put(a, &empty); }
          else if (!strcmp(operation, "wifi-release")) ap01_wifi_release();
          else if (!strcmp(operation, "wifi-select")) ap01_wifi_select(a);
          else if (!strcmp(operation, "wifi"))
            {
              if (a && g_ap01_wifi_active >= 0) ap01_wifi_select((unsigned)g_ap01_wifi_active);
              else if (a) ap01_sim_wifi_configure("AP01-Test");
              else ap01_sim_wifi_disconnect();
            }
          else if (!strcmp(operation, "fault") && a <= 2)
            { g_ap01_sim.next_fault = a; ap01_sim_reply(operation, AP01_SIM_OK, "armed", ""); }
          else if (!strcmp(operation, "weather")) ap01_sim_weather_refresh();
          else if (!strcmp(operation, "weather-data") && a <= 999 && b <= 100 && c <= 500 && d <= 20)
            {
              g_ap01_sim.weather.native_code = a; g_ap01_sim.weather.humidity = b;
              g_ap01_sim.weather.aqi = c; g_ap01_sim.weather.uvi = d;
              g_ap01_sim.weather.status = AP01_SIM_OK;
              for (unsigned i = 0; i < 7; ++i) g_ap01_sim.weather.forecast[i].native_code = a;
              ap01_sim_reply(operation, AP01_SIM_OK, "event", "");
            }
          else if (!strcmp(operation, "climate") && a <= 200 && b <= 200 && c <= 200 && d <= 200)
            {
              g_ap01_sim.weather.temperature = (int)a - 100;
              g_ap01_sim.weather.high = (int)b - 100;
              g_ap01_sim.weather.low = (int)c - 100;
              g_ap01_sim.weather.feels_like = (int)d - 100;
              ap01_sim_reply(operation, AP01_SIM_OK, "event", "");
            }
          else if (!strcmp(operation, "sun") && a < 1440 && b < 1440)
            {
              g_ap01_sim.weather.sunrise_minutes = a; g_ap01_sim.weather.sunset_minutes = b;
              ap01_sim_reply(operation, AP01_SIM_OK, "event", "");
            }
          else if (!strcmp(operation, "bind")) ap01_sim_binding_start();
          else if (!strcmp(operation, "bind-cancel")) ap01_sim_binding_cancel();
          else if (!strcmp(operation, "check")) ap01_sim_update_check(a);
          else if (!strcmp(operation, "check-cancel")) ap01_sim_update_cancel();
          else if (!strcmp(operation, "mode")) ap01_sim_set_mode(a);
          else if (!strcmp(operation, "port")) ap01_sim_set_port(a, b, c != 0);
          else if (!strcmp(operation, "telemetry") && a < AP01_SIM_GROUPS && b < AP01_SIM_PORTS && c <= 28000 && d <= 5000)
            {
              ap01_sim_port_t *p = ap01_sim_get_port(a, b);
              p->voltage_mv = c; p->current_ma = d;
              ap01_sim_reply(operation, AP01_SIM_OK, "event", "");
            }
          else if (!strcmp(operation, "capabilities") && a < AP01_SIM_GROUPS && b < AP01_SIM_PORTS && c <= 3 && d <= 5)
            {
              ap01_sim_port_t *p = ap01_sim_get_port(a, b);
              bool changed = p->capabilities != c;
              p->capabilities = c; p->cable_amps = d;
              if (changed) ap01_sim_invalidate_protocol(a, b);
              ap01_sim_reply(operation, AP01_SIM_OK, "event", "");
            }
          else if (!strcmp(operation, "port-state") && a < AP01_SIM_GROUPS && b < AP01_SIM_PORTS && c < 8 && d <= 100)
            {
              ap01_sim_port_t *p = ap01_sim_get_port(a, b);
              bool was_connected = p->connected;
              p->input = (c & 1) != 0; p->bms_online = (c & 2) != 0;
              p->connected = (c & 4) != 0; p->battery = d;
              if (was_connected != p->connected) ap01_sim_invalidate_protocol(a, b);
              ap01_sim_reply(operation, AP01_SIM_OK, "event", "");
            }
          else if (!strcmp(operation, "safe")) ap01_sim_set_safe(a, b, c != 0, 0, d);
          else if (!strcmp(operation, "protocol")) ap01_sim_protocol_start(a, b);
          else if (!strcmp(operation, "protocol-mask") && a < AP01_SIM_GROUPS && b < AP01_SIM_PORTS && c <= 7)
            {
              ap01_sim_get_port(a, b)->supported_protocol_mask = c;
              ap01_sim_reply(operation, AP01_SIM_OK, "event", "");
            }
          else if (!strcmp(operation, "protocol-cancel")) ap01_sim_protocol_cancel();
          else if (!strcmp(operation, "protocol-confirm")) ap01_sim_protocol_confirm(a, b, c);
          else if (!strcmp(operation, "package"))
            {
              const uint8_t data[] = {0x41, 0x50, 0x30, 0x31};
              ap01_sim_ota_prepare(a == 0 ? "AP01" : a == 1 ? "TA1208" : "INVALID", b,
                data, sizeof(data), ap01_sim_crc(data, sizeof(data)) ^ c, d != 0);
            }
          else if (!strcmp(operation, "ota")) ap01_sim_ota_start(a != 0, b != 0);
          else if (!strcmp(operation, "ota-cancel")) ap01_sim_ota_cancel();
          else if (!strcmp(operation, "reset")) ap01_sim_factory_reset();
          else if (!strcmp(operation, "timers"))
            {
              ap01_sim_settings_t settings = g_ap01_sim.settings;
              settings.saver_seconds = a; settings.blank_seconds = b; settings.saver_mode = c;
              ap01_sim_apply_settings(&settings);
            }
          else
            {
              unsigned sequence = g_ap01_sim.reply.sequence;
              if (ap01_ui_sim_control_ui(operation, a))
                ap01_sim_reply(operation, AP01_SIM_OK, "ui-event", "");
              else if (sequence == g_ap01_sim.reply.sequence)
                ap01_sim_reply("control", AP01_SIM_ERROR, "dispatch", "unknown-command-or-invalid-value");
            }
          g_ap01_sim_request_ok = !strcmp(operation, "status") || g_ap01_sim.reply.status == AP01_SIM_OK || g_ap01_sim.reply.status == AP01_SIM_PENDING;
            }
          ap01_sim_status_publish();
        }
    }
  /* Publish input-only transitions too. The fixed local endpoint never sends
   * ROM bytes, credentials, or requests outside this host. */
  static uint64_t published_at;
  uint64_t now = ap01_sim_millis();
  if (g_ap01_sim_published_revision != g_ap01_sim.revision || now - published_at >= 200)
    { ap01_sim_status_publish(); published_at = now; }
  return revision != g_ap01_sim.revision;
}
#endif
