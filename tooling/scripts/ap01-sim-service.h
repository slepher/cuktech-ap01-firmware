/* SPDX-License-Identifier: Apache-2.0 */
/* Controlled local services for the AP01 application rehost. */
#ifndef AP01_SIM_SERVICE_H
#define AP01_SIM_SERVICE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define AP01_SIM_BANKS 2
#define AP01_SIM_PORTS 4
#define AP01_SIM_LOCAL_BANK AP01_SIM_BANKS
#define AP01_SIM_GROUPS (AP01_SIM_BANKS + 1)
#define AP01_SIM_HISTORY 180
#define AP01_SIM_CONFIG_MAX (13 + 16 + 2 + 8 + AP01_SIM_GROUPS * AP01_SIM_PORTS * 12 + 1 + 32 + 1 + 47 + 4)
#define AP01_SIM_CAP_SAFE 1U
#define AP01_SIM_CAP_PROTOCOL 2U

enum ap01_sim_status_e { AP01_SIM_IDLE, AP01_SIM_PENDING, AP01_SIM_OK, AP01_SIM_ERROR, AP01_SIM_TIMEOUT };
typedef struct
{
  bool enabled;
  bool connected;
  bool input;
  bool bms_online;
  unsigned int battery;
  unsigned int cable_amps;
  char device_name[48];
  enum ap01_sim_status_e protocol_status;
  unsigned int protocol_mask;
  unsigned int supported_protocol_mask;
  unsigned int protocol_disabled_mask;
  bool safe_enabled;
  unsigned int safe_mode;
  unsigned int safe_limit;
  unsigned int protocol;
  unsigned int voltage_mv;
  unsigned int capabilities;
  unsigned int max_watts;
  unsigned int current_ma;
  unsigned int delivered_mah;
  unsigned int history[AP01_SIM_HISTORY];
  unsigned int history_count;
  unsigned int history_head;
} ap01_sim_port_t;
typedef struct
{
  bool connected;
  unsigned int battery;
  int temperature;
  unsigned int remaining_minutes;
  ap01_sim_port_t ports[AP01_SIM_PORTS];
  unsigned int history[AP01_SIM_HISTORY];
  unsigned int history_count;
  unsigned int history_head;
} ap01_sim_bank_t;
typedef struct
{
  enum ap01_sim_status_e status;
  int condition;
  unsigned int native_code;
  int temperature;
  int high;
  int low;
  int feels_like;
  unsigned int humidity;
  unsigned int aqi;
  unsigned int uvi;
  unsigned int sunrise_minutes;
  unsigned int sunset_minutes;
  struct { int condition, high, low; unsigned int native_code; } forecast[7];
  char location[48];
} ap01_sim_weather_t;
typedef struct
{
  bool enabled[2];
  unsigned int brightness;
  bool hour12;
  unsigned int output_mode;
  unsigned int pet;
  bool guide_completed;
  unsigned int saver_seconds;
  unsigned int blank_seconds;
  unsigned int saver_mode;
} ap01_sim_settings_t;
typedef struct
{
  unsigned int sequence;
  enum ap01_sim_status_e status;
  char operation[40];
  char error[64];
  char stage[24];
  char action_hint[64];
} ap01_sim_reply_t;
typedef struct
{
  ap01_sim_settings_t settings;
  ap01_sim_bank_t banks[AP01_SIM_BANKS];
  bool charger_connected;
  bool device_recovery_required;
  int charger_temperature;
  ap01_sim_port_t ports[AP01_SIM_PORTS];
  unsigned int history[AP01_SIM_HISTORY];
  unsigned int history_count;
  unsigned int history_head;
  ap01_sim_weather_t weather;
  bool wifi_connected;
  bool wifi_configured;
  char ssid[33];
  bool bound;
  enum ap01_sim_status_e binding;
  enum ap01_sim_status_e ota;
  unsigned int ota_target;
  unsigned int firmware_version;
  unsigned int offered_version;
  unsigned int device_firmware_version;
  unsigned int device_offered_version;
  bool update_available;
  bool device_update_available;
  enum ap01_sim_status_e update_check;
  unsigned int update_target;
  unsigned int ota_progress;
  bool ota_crc_valid;
  bool ota_signed;
  struct { bool validated, is_signed; unsigned int version; } packages[2];
  bool next_failure;
  unsigned int next_fault;
  unsigned int revision;
  ap01_sim_reply_t reply;
} ap01_sim_state_t;
static ap01_sim_state_t g_ap01_sim;

static void ap01_wifi_init(void);
static void ap01_wifi_offline(void);
static bool ap01_wifi_reset(void);
static void ap01_wifi_tick(uint64_t now);
static bool ap01_wifi_has_attempt(void);
static void ap01_sim_init(void);
static void ap01_sim_tick(void);
static bool ap01_sim_save(void);
static bool ap01_sim_apply_settings(const ap01_sim_settings_t *settings);
static bool ap01_sim_factory_reset(void);
static void ap01_sim_connect(unsigned int bank, bool connected);
static ap01_sim_port_t *ap01_sim_get_port(unsigned int bank, unsigned int port);
static bool ap01_sim_device_connect(unsigned int bank, unsigned int port, bool connected);
static bool ap01_sim_set_mode(unsigned int mode);
static bool ap01_sim_set_port(unsigned int bank, unsigned int port, bool enabled);
static bool ap01_sim_set_safe(unsigned int bank, unsigned int port, bool enabled,
                              unsigned int mode, unsigned int limit);
static bool ap01_sim_protocol_start(unsigned int bank, unsigned int port);
static bool ap01_sim_protocol_cancel(void);
static bool ap01_sim_protocol_confirm(unsigned int bank, unsigned int port, unsigned int disabled_mask);
static bool ap01_sim_wifi_configure(const char *ssid);
static void ap01_sim_wifi_disconnect(void);
static void ap01_sim_charger_connect(bool connected);
static bool ap01_sim_weather_refresh(void);
static bool ap01_sim_binding_start(void);
static bool ap01_sim_binding_cancel(void);
static bool ap01_sim_update_check(unsigned int target);
static bool ap01_sim_update_cancel(void);
static bool ap01_sim_ota_prepare(const char *model, unsigned int version, const uint8_t *data, size_t length, uint32_t crc, bool is_signed);
static bool ap01_sim_restart_complete(void);
static bool ap01_sim_ota_start(bool crc_valid, bool is_signed);
static bool ap01_sim_ota_cancel(void);

#include "ap01-sim-service-impl.h"
#endif
