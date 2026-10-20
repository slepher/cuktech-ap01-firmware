/* SPDX-License-Identifier: Apache-2.0 */
#include <assert.h>
#include <sys/stat.h>
#include <unistd.h>
static char wifi_test_path[160];
#define AP01_SIM_STATE_PATH wifi_test_path
#include "ap01-sim-service.h"

int main(void)
{
  char directory[] = "/tmp/ap01-wifi-XXXXXX";
  assert(mkdtemp(directory));
  snprintf(wifi_test_path, sizeof(wifi_test_path), "%s/state.bin", directory);
  ap01_sim_init(); assert(ap01_sim_save());
  uint8_t legacy[AP01_SIM_CONFIG_MAX], after[AP01_SIM_CONFIG_MAX];
  FILE *f = fopen(wifi_test_path, "rb"); assert(f);
  size_t legacy_length = fread(legacy, 1, sizeof(legacy), f); fclose(f);
  /* Deliberately opaque fixtures, NOT assertions about the real MiIO schema. */
  ap01_sim_wifi_profile home = {.ssid="Home", .length=6, .native={0,1,2,3,255,0}};
  ap01_sim_wifi_profile office = {.ssid="Office \"5G\"", .length=4, .native={9,8,7,6}};
  assert(ap01_wifi_put(0, &home)); assert(ap01_wifi_put(3, &office));
  assert(!g_ap01_sim.wifi_configured && g_ap01_wifi_active == -1);
  assert(!ap01_wifi_put(8, &home)); assert(!ap01_wifi_put(1, &home));
  ap01_sim_wifi_profile bad = home; memset(bad.ssid, 'x', 33);
  assert(!ap01_wifi_put(1, &bad));
  bad = home; bad.ssid[0] = (char)0xff; assert(!ap01_wifi_put(1, &bad));
  bad = home; bad.length = AP01_WIFI_NATIVE_MAX + 1; assert(!ap01_wifi_put(1, &bad));
  assert(!ap01_wifi_select(1)); assert(ap01_wifi_select(0));
  uint8_t active[AP01_WIFI_NATIVE_MAX];
  assert(ap01_wifi_read(".wapi.conf", active, sizeof(active)) == 6);
  assert(!memcmp(active, home.native, 6));
  f = fopen(wifi_test_path, "rb"); assert(f);
  assert(fread(after, 1, sizeof(after), f) == legacy_length); fclose(f);
  assert(!memcmp(legacy, after, legacy_length)); /* unchanged SCF1 wire layout/bytes */
  assert(!ap01_wifi_put(0, &office)); /* cannot orphan authoritative native file */
  g_ap01_sim.next_fault = 1; assert(!ap01_wifi_select(3));
  assert(g_ap01_wifi_active == 0 && !strcmp(g_ap01_sim.ssid, "Home"));
  char path[256], temporary[260]; assert(ap01_wifi_path(path, ".wapi.conf"));
  snprintf(temporary, sizeof(temporary), "%s.new", path); assert(!mkdir(temporary, 0700));
  assert(!ap01_wifi_select(3)); assert(g_ap01_wifi_active == 0);
  assert(ap01_wifi_read(".wapi.conf", active, sizeof(active)) == 6 && !memcmp(active, home.native, 6));
  assert(!rmdir(temporary));
  g_ap01_sim.ota = AP01_SIM_PENDING; assert(!ap01_wifi_select(3)); g_ap01_sim.ota = AP01_SIM_IDLE;
  g_ap01_sim.binding = AP01_SIM_PENDING; assert(!ap01_wifi_select(3)); g_ap01_sim.binding = AP01_SIM_IDLE;
  assert(ap01_wifi_select(3));
  ap01_sim_init(); assert(g_ap01_wifi_active == 3 && !strcmp(g_ap01_sim.ssid, office.ssid));
  assert(g_ap01_sim.wifi_connected && g_ap01_sim.wifi_configured);
  ap01_sim_wifi_profile empty = {0}; assert(ap01_wifi_put(0, &empty));
  assert(!g_ap01_wifi[0].length && g_ap01_wifi_active == 3);
  assert(ap01_wifi_path(path, ".wifi-list")); struct stat st;
  assert(!stat(path, &st) && (st.st_mode & 0777) == 0600);
  assert(ap01_wifi_path(path, ".wifi-list")); snprintf(temporary, sizeof(temporary), "%s.new", path);
  assert(!mkdir(temporary, 0700)); assert(!ap01_wifi_put(0, &home)); assert(!g_ap01_wifi[0].length);
  assert(!rmdir(temporary));
  /* Import before startup, even when no network is configured. */
  assert(ap01_wifi_reset());
  uint8_t staged[33 + AP01_WIFI_NATIVE_MAX]; memcpy(staged, home.ssid, 33); memcpy(staged + 33, home.native, 6);
  assert(ap01_wifi_write(".wifi-offline-2", staged, 39));
  ap01_sim_init(); assert(g_ap01_wifi[2].length == 6 && !g_ap01_sim.wifi_configured);
  assert(ap01_wifi_read(".wifi-offline-2", active, sizeof(active)) == -1);
  assert(ap01_wifi_select(2));
  assert(ap01_wifi_release());
  assert(!g_ap01_sim.wifi_configured && g_ap01_wifi[2].length == 6);
  assert(ap01_wifi_put(2, &empty));
  assert(ap01_wifi_put(2, &home) && ap01_wifi_select(2));
  /* Corrupt records fail closed, preserve disk evidence and never auto-repair. */
  uint8_t corrupt[] = "AP01WFL1bad"; assert(ap01_wifi_write(".wifi-list", corrupt, sizeof(corrupt)));
  ap01_sim_init(); assert(g_ap01_wifi_invalid && !g_ap01_sim.wifi_configured && !g_ap01_sim.wifi_connected);
  assert(!ap01_wifi_put(0, &home)); assert(!ap01_wifi_select(2));
  assert(ap01_wifi_write(".wifi-offline-2", staged, 39));
  assert(ap01_sim_factory_reset()); assert(!g_ap01_wifi_invalid && !g_ap01_wifi[2].length);
  ap01_sim_init(); assert(!g_ap01_sim.wifi_configured && g_ap01_wifi_active == -1);
  const char *suffixes[] = {"", ".wifi-list", ".wapi.conf"};
  for (unsigned i = 0; i < 3; ++i) { assert(ap01_wifi_path(path, suffixes[i])); assert(!unlink(path)); }
  assert(!rmdir(directory));
  puts("SIM Wi-Fi profiles PASS: opaque byte preservation, unchanged legacy state, restart, offline import, rollback, corruption and reset");
}
