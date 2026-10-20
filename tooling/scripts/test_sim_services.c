/* SPDX-License-Identifier: Apache-2.0 */
#include <assert.h>
#include <stdio.h>
#include <unistd.h>
static char service_test_path[160];
#define AP01_SIM_STATE_PATH service_test_path
#include "ap01-sim-service.h"

static unsigned checks;
#define CHECK(condition) do { assert(condition); ++checks; } while (0)

static void complete_async(void)
{
  if (g_ap01_sim_weather_due) g_ap01_sim_weather_due = 1;
  if (g_ap01_sim_binding_due) g_ap01_sim_binding_due = 1;
  if (g_ap01_sim_protocol_due) g_ap01_sim_protocol_due = 1;
  if (g_ap01_sim_update_due) g_ap01_sim_update_due = 1;
  if (g_ap01_sim_ota_due) g_ap01_sim_ota_due = 1;
  ap01_sim_tick();
}

int main(void)
{
  snprintf(service_test_path, sizeof(service_test_path), "/tmp/ap01-service-check-%ld.bin", (long)getpid());
  CHECK(access(service_test_path, F_OK) != 0);
  ap01_sim_init();
  CHECK(g_ap01_sim.settings.brightness == 10 && !g_ap01_sim.bound);
  CHECK(ap01_sim_crc((const uint8_t *)"123456789", 9) == 0xcbf43926);
  CHECK(!ap01_sim_set_mode(3));
  CHECK(ap01_sim_set_mode(2));
  g_ap01_sim.next_failure = true;
  CHECK(!ap01_sim_set_mode(1) && g_ap01_sim.settings.output_mode == 2);
  g_ap01_sim.next_fault = 2;
  CHECK(!ap01_sim_set_mode(1) && g_ap01_sim.reply.status == AP01_SIM_TIMEOUT);
  CHECK(!ap01_sim_set_port(0, 0, false));
  ap01_sim_connect(0, true); ap01_sim_connect(1, true);
  CHECK(g_ap01_sim.banks[0].connected && g_ap01_sim.ports[0].connected);
  CHECK(ap01_sim_get_port(AP01_SIM_LOCAL_BANK, 0) != ap01_sim_get_port(0, 0));
  CHECK(ap01_sim_set_port(AP01_SIM_LOCAL_BANK, 0, false));
  CHECK(!g_ap01_sim.ports[0].enabled && g_ap01_sim.banks[0].ports[0].enabled);
  CHECK(ap01_sim_set_port(0, 0, false));
  CHECK(!g_ap01_sim.banks[0].ports[0].enabled && g_ap01_sim.banks[1].ports[0].enabled);
  CHECK(ap01_sim_set_safe(AP01_SIM_LOCAL_BANK, 1, true, 0, 120));
  CHECK(g_ap01_sim.ports[1].safe_enabled && !g_ap01_sim.banks[0].ports[1].safe_enabled);
  CHECK(!ap01_sim_set_safe(0, 0, true, 9, 120));
  CHECK(!ap01_sim_protocol_confirm(AP01_SIM_LOCAL_BANK, 1, 5));
  CHECK(ap01_sim_protocol_start(AP01_SIM_LOCAL_BANK, 1));
  CHECK(!ap01_sim_protocol_confirm(AP01_SIM_LOCAL_BANK, 1, 5));
  CHECK(g_ap01_sim.ports[1].protocol_status == AP01_SIM_PENDING);
  CHECK(!ap01_sim_protocol_start(0, 1));
  complete_async();
  CHECK(g_ap01_sim.ports[1].protocol_status == AP01_SIM_OK && g_ap01_sim.ports[1].protocol_mask == 7);
  CHECK(ap01_sim_protocol_confirm(AP01_SIM_LOCAL_BANK, 1, 5));
  CHECK(g_ap01_sim.ports[1].protocol_disabled_mask == 5);
  CHECK(!ap01_sim_protocol_confirm(AP01_SIM_LOCAL_BANK, 1, 5));
  g_ap01_sim.next_fault = 2;
  CHECK(ap01_sim_protocol_start(1, 0)); complete_async();
  CHECK(g_ap01_sim.banks[1].ports[0].protocol_status == AP01_SIM_TIMEOUT);
  CHECK(ap01_sim_protocol_start(1, 0));
  CHECK(ap01_sim_protocol_cancel()); complete_async();
  CHECK(g_ap01_sim.banks[1].ports[0].protocol_status == AP01_SIM_IDLE);
  CHECK(!ap01_sim_weather_refresh());
  CHECK(!ap01_sim_wifi_configure(""));
  CHECK(ap01_sim_wifi_configure("AP01-SIM"));
  CHECK(ap01_sim_weather_refresh());
  uint64_t weather_deadline = g_ap01_sim_weather_due;
  CHECK(!ap01_sim_weather_refresh() && g_ap01_sim_weather_due == weather_deadline);
  complete_async();
  CHECK(g_ap01_sim.weather.status == AP01_SIM_OK && g_ap01_sim.weather.temperature == 24);
  g_ap01_sim.next_failure = true;
  CHECK(ap01_sim_weather_refresh()); complete_async();
  CHECK(g_ap01_sim.weather.status == AP01_SIM_ERROR);
  CHECK(ap01_sim_weather_refresh()); ap01_sim_wifi_disconnect();
  CHECK(ap01_sim_wifi_configure("AP01-SIM")); complete_async();
  CHECK(g_ap01_sim.weather.status == AP01_SIM_ERROR);
  g_ap01_sim.next_fault = 2;
  CHECK(ap01_sim_weather_refresh()); complete_async();
  CHECK(g_ap01_sim.weather.status == AP01_SIM_TIMEOUT);
  CHECK(ap01_sim_weather_refresh()); g_ap01_sim.wifi_connected = false; complete_async();
  CHECK(g_ap01_sim.weather.status == AP01_SIM_ERROR);
  g_ap01_sim.wifi_connected = true;
  CHECK(ap01_sim_protocol_start(1, 0));
  CHECK(ap01_sim_device_connect(1, 0, false)); complete_async();
  CHECK(g_ap01_sim.banks[1].ports[0].protocol_status == AP01_SIM_ERROR);
  CHECK(ap01_sim_device_connect(1, 0, true));
  CHECK(ap01_sim_binding_start());
  CHECK(!ap01_sim_binding_start());
  CHECK(!ap01_sim_update_check(0));
  CHECK(!ap01_sim_ota_start(true, false));
  CHECK(ap01_sim_binding_cancel()); complete_async();
  CHECK(!g_ap01_sim.bound && g_ap01_sim.binding == AP01_SIM_IDLE);
  g_ap01_sim.next_fault = 2;
  CHECK(ap01_sim_binding_start()); complete_async();
  CHECK(!g_ap01_sim.bound && g_ap01_sim.binding == AP01_SIM_TIMEOUT);
  CHECK(ap01_sim_binding_start()); complete_async();
  CHECK(g_ap01_sim.bound && g_ap01_sim.binding == AP01_SIM_OK);
  CHECK(!ap01_sim_update_check(2));
  CHECK(ap01_sim_update_check(0)); CHECK(!ap01_sim_update_check(1));
  CHECK(ap01_sim_update_cancel()); complete_async();
  CHECK(g_ap01_sim.update_check == AP01_SIM_IDLE);
  g_ap01_sim.next_fault = 2;
  CHECK(ap01_sim_update_check(1)); complete_async();
  CHECK(g_ap01_sim.update_check == AP01_SIM_TIMEOUT);
  CHECK(ap01_sim_update_check(0)); complete_async();
  CHECK(g_ap01_sim.update_available);
  const uint8_t package[] = "AP01 controlled local package payload";
  uint32_t crc = ap01_sim_crc(package, sizeof(package));
  CHECK(!ap01_sim_ota_prepare("OTHER", 42, package, sizeof(package), crc, false));
  CHECK(!ap01_sim_ota_prepare("AP01", 41, package, sizeof(package), crc, false));
  CHECK(!ap01_sim_ota_prepare("AP01", 100000000, package, sizeof(package), crc, false));
  CHECK(!ap01_sim_ota_prepare("AP01", 42, package, sizeof(package), crc ^ 1, false));
  CHECK(ap01_sim_ota_prepare("AP01", 42, package, sizeof(package), crc, false));
  CHECK(ap01_sim_ota_start(true, false));
  CHECK(!ap01_sim_ota_prepare("TA1208", 11, package, sizeof(package), crc, true));
  CHECK(!ap01_sim_update_check(1));
  CHECK(!ap01_sim_binding_start());
  CHECK(!ap01_sim_factory_reset());
  CHECK(g_ap01_sim.ota_target == 0);
  for (unsigned i = 0; i < 11; ++i) complete_async();
  CHECK(g_ap01_sim.ota == AP01_SIM_OK && g_ap01_sim.firmware_version == 41);
  CHECK(ap01_sim_restart_complete()); CHECK(g_ap01_sim.firmware_version == 42);
  g_ap01_sim.device_recovery_required = true;
  g_ap01_sim.ota_target = 1;
  CHECK(!ap01_sim_ota_start(true, false)); /* AP01 validation cannot authorize TA recovery */
  CHECK(ap01_sim_ota_prepare("TA1208", 10, package, sizeof(package), crc, false));
  CHECK(ap01_sim_ota_start(true, false));
  for (unsigned i = 0; i < 11; ++i) complete_async();
  CHECK(g_ap01_sim.ota == AP01_SIM_OK);
  CHECK(ap01_sim_restart_complete());
  CHECK(!g_ap01_sim.device_recovery_required && g_ap01_sim.device_firmware_version == 10);
  CHECK(ap01_sim_ota_prepare("TA1208", 11, package, sizeof(package), crc, true));
  CHECK(ap01_sim_ota_start(false, true));
  for (unsigned i = 0; i < 11; ++i) complete_async();
  CHECK(g_ap01_sim.ota == AP01_SIM_ERROR && g_ap01_sim.device_firmware_version == 10);
  CHECK(ap01_sim_ota_start(true, true)); CHECK(ap01_sim_ota_cancel()); complete_async();
  CHECK(g_ap01_sim.ota == AP01_SIM_IDLE);
  CHECK(ap01_sim_ota_start(true, true));
  ap01_sim_charger_connect(false); ap01_sim_charger_connect(true); complete_async();
  CHECK(g_ap01_sim.ota == AP01_SIM_ERROR);
  CHECK(!ap01_sim_protocol_start(0, 0));
  ap01_sim_connect(0, true); ap01_sim_connect(1, true);
  g_ap01_sim.next_fault = 2;
  CHECK(ap01_sim_ota_start(true, false)); complete_async();
  CHECK(g_ap01_sim.ota == AP01_SIM_TIMEOUT);
  CHECK(ap01_sim_ota_start(true, false)); g_ap01_sim.wifi_connected = false; complete_async();
  CHECK(g_ap01_sim.ota == AP01_SIM_ERROR);
  g_ap01_sim.wifi_connected = true;
  g_ap01_sim.charger_connected = false;
  CHECK(!ap01_sim_ota_start(true, false));
  g_ap01_sim.charger_connected = true;
  g_ap01_sim.ota_target = 0;
  CHECK(!ap01_sim_ota_start(true, false)); /* already installed */
  CHECK(ap01_sim_device_connect(AP01_SIM_LOCAL_BANK, 0, true));
  CHECK(!g_ap01_sim.banks[0].connected && !g_ap01_sim.banks[0].ports[0].connected && !g_ap01_sim.banks[0].ports[1].connected);
  CHECK(g_ap01_sim.ports[0].connected && !g_ap01_sim.ports[0].bms_online);
  CHECK(ap01_sim_protocol_start(AP01_SIM_LOCAL_BANK, 0));
  ap01_sim_connect(0, true);
  CHECK(!g_ap01_sim_protocol_due && g_ap01_sim.ports[0].protocol_status == AP01_SIM_ERROR);
  CHECK(!ap01_sim_protocol_confirm(AP01_SIM_LOCAL_BANK, 0, 0));
  CHECK(ap01_sim_protocol_start(0, 0)); ap01_sim_connect(0, true);
  CHECK(!g_ap01_sim_protocol_due && g_ap01_sim.banks[0].ports[0].protocol_status == AP01_SIM_ERROR);
  CHECK(ap01_sim_protocol_start(AP01_SIM_LOCAL_BANK, 1));
  CHECK(ap01_sim_device_connect(AP01_SIM_LOCAL_BANK, 1, false));
  complete_async();
  CHECK(g_ap01_sim.ports[1].protocol_status == AP01_SIM_ERROR && !g_ap01_sim_protocol_due);
  ap01_sim_connect(1, true);
  unsigned history_head = g_ap01_sim.history_head;
  g_ap01_sim.ports[1].voltage_mv = 20000; g_ap01_sim.ports[1].current_ma = 2500;
  g_ap01_sim.ports[2].connected = true; g_ap01_sim.ports[2].input = true;
  g_ap01_sim.ports[2].voltage_mv = 9000; g_ap01_sim.ports[2].current_ma = 1000;
  for (unsigned i = 0; i < AP01_SIM_HISTORY + 5; ++i)
    { g_ap01_sim_sample_due = 1; ap01_sim_tick(); }
  CHECK(g_ap01_sim.history_count == AP01_SIM_HISTORY);
  CHECK(g_ap01_sim.history_head == (history_head + AP01_SIM_HISTORY + 5) % AP01_SIM_HISTORY);
  CHECK(g_ap01_sim.ports[1].delivered_mah > 0);
  CHECK(g_ap01_sim.history[(g_ap01_sim.history_head + AP01_SIM_HISTORY - 1) % AP01_SIM_HISTORY] == 50000);
  CHECK(g_ap01_sim.banks[1].ports[1].history_count == AP01_SIM_HISTORY);

  ap01_sim_settings_t settings = g_ap01_sim.settings;
  settings.hour12 = true; settings.brightness = 6; settings.guide_completed = true;
  CHECK(ap01_sim_apply_settings(&settings));
  g_ap01_sim.next_failure = true; settings.brightness = 4;
  CHECK(!ap01_sim_apply_settings(&settings) && g_ap01_sim.settings.brightness == 6);
  char original_path[160]; snprintf(original_path, sizeof(original_path), "%s", service_test_path);
  CHECK(strlen(original_path) + sizeof("/child") <= sizeof(service_test_path));
  memcpy(service_test_path, original_path, strlen(original_path));
  memcpy(service_test_path + strlen(original_path), "/child", sizeof("/child"));
  CHECK(!ap01_sim_set_mode(1) && g_ap01_sim.settings.output_mode == 2);
  snprintf(service_test_path, sizeof(service_test_path), "%s", original_path);
  ap01_sim_init();
  CHECK(g_ap01_sim.settings.output_mode == 2 && g_ap01_sim.settings.hour12 && g_ap01_sim.settings.brightness == 6);
  CHECK(g_ap01_sim.settings.guide_completed && g_ap01_sim.bound && g_ap01_sim.wifi_configured);
  CHECK(g_ap01_sim.firmware_version == 42 && g_ap01_sim.device_firmware_version == 10);
  CHECK(g_ap01_sim.ports[1].protocol_disabled_mask == 5 && g_ap01_sim.ports[1].safe_enabled);
  CHECK(!g_ap01_sim.ports[0].enabled && !g_ap01_sim.banks[0].ports[0].enabled);
  CHECK(!g_ap01_sim.banks[0].connected); /* connection is runtime, not persisted */

  memset(g_ap01_sim.ssid, 's', 32); g_ap01_sim.ssid[32] = 0;
  memset(g_ap01_sim.weather.location, 'c', 47); g_ap01_sim.weather.location[47] = 0;
  CHECK(ap01_sim_save());
  FILE *file = fopen(service_test_path, "rb"); CHECK(file != NULL);
  uint8_t wire[AP01_SIM_CONFIG_MAX + 1]; size_t length = fread(wire, 1, sizeof(wire), file); fclose(file);
  CHECK(length == AP01_SIM_CONFIG_MAX);
  CHECK(ap01_sim_decode(wire, length));
  uint8_t saved = wire[8]; wire[8] = 99; CHECK(!ap01_sim_decode(wire, length)); wire[8] = saved;
  wire[length - 1] ^= 1; CHECK(!ap01_sim_decode(wire, length)); wire[length - 1] ^= 1;
  CHECK(!ap01_sim_decode(wire, length - 1));
  wire[0] = 0;
  file = fopen(service_test_path, "wb"); CHECK(file != NULL);
  CHECK(fwrite(wire, 1, length, file) == length); fclose(file);
  ap01_sim_init(); CHECK(g_ap01_sim_store_invalid && g_ap01_sim.reply.status == AP01_SIM_ERROR);
  CHECK(!ap01_sim_set_mode(2));
  ap01_sim_connect(0, true);
  CHECK(ap01_sim_protocol_start(AP01_SIM_LOCAL_BANK, 0));
  CHECK(ap01_sim_factory_reset());
  CHECK(!g_ap01_sim_protocol_due && g_ap01_sim.ports[0].protocol_status == AP01_SIM_IDLE);
  CHECK(!g_ap01_sim_store_invalid && g_ap01_sim.settings.output_mode == 0 && !g_ap01_sim.bound);
  CHECK(g_ap01_sim.firmware_version == 41); /* corrupt record never supplies a version */
  CHECK(unlink(service_test_path) == 0);
  char wifi_path[256];
  CHECK(ap01_wifi_path(wifi_path, ".wifi-list") && unlink(wifi_path) == 0);
  CHECK(ap01_wifi_path(wifi_path, ".wapi.conf") && unlink(wifi_path) == 0);
  printf("SIM service checks PASS: %u; config_max=%u state_bytes=%zu\n", checks,
         (unsigned)AP01_SIM_CONFIG_MAX, sizeof(g_ap01_sim));
  return 0;
}
