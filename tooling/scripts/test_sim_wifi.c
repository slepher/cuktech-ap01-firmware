/* SPDX-License-Identifier: Apache-2.0 */
#include <assert.h>
#include <sys/stat.h>
#include <unistd.h>
static char wifi_test_path[160];
#define AP01_SIM_STATE_PATH wifi_test_path
#include "ap01-sim-service.h"

static void ip_ready(void)
{
  assert(!g_ap01_sim.wifi_connected);
  assert(!ap01_wifi_event(1)); /* writing config or IP before association is insufficient */
  unsigned revision = g_ap01_sim.revision;
  assert(ap01_wifi_event(0)); assert(!g_ap01_sim.wifi_connected);
  assert(g_ap01_sim.revision > revision && g_ap01_sim.reply.status == AP01_SIM_PENDING);
  assert(!strcmp(g_ap01_sim.reply.stage, "waiting-ip"));
  assert(ap01_wifi_event(1)); assert(g_ap01_sim.wifi_connected);
}

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
  assert(g_ap01_wifi_pending && g_ap01_wifi_active == -1); ip_ready();
  uint8_t active[AP01_WIFI_NATIVE_MAX];
  assert(ap01_wifi_read(".wapi.conf", active, sizeof(active)) == 6);
  assert(!memcmp(active, home.native, 6));
  f = fopen(wifi_test_path, "rb"); assert(f);
  assert(fread(after, 1, sizeof(after), f) == legacy_length); fclose(f);
  assert(!memcmp(legacy, after, legacy_length)); /* unchanged SCF1 wire layout/bytes */
  assert(!ap01_wifi_put(0, &office)); /* duplicate SSID remains invalid */
  g_ap01_sim.next_fault = 1; assert(!ap01_wifi_select(3));
  assert(g_ap01_wifi_active == 0 && !strcmp(g_ap01_sim.ssid, "Home"));
  char path[256], temporary[260]; assert(ap01_wifi_path(path, ".wapi.conf"));
  snprintf(temporary, sizeof(temporary), "%s.new", path); assert(!mkdir(temporary, 0700));
  assert(!ap01_wifi_select(3)); assert(g_ap01_wifi_active == 0);
  assert(ap01_wifi_read(".wapi.conf", active, sizeof(active)) == 6 && !memcmp(active, home.native, 6));
  assert(!rmdir(temporary));
  g_ap01_sim.ota = AP01_SIM_PENDING; assert(!ap01_wifi_select(3)); g_ap01_sim.ota = AP01_SIM_IDLE;
  g_ap01_sim.binding = AP01_SIM_PENDING; assert(!ap01_wifi_select(3)); g_ap01_sim.binding = AP01_SIM_IDLE;
  /* Legacy .wapi migrates only with an exact opaque match in the old list. */
  assert(ap01_wifi_path(path, ".wifi-current")); assert(!unlink(path));
  ap01_sim_init(); assert(g_ap01_wifi_active == 0 && !g_ap01_sim.wifi_connected); ip_ready();
  assert(ap01_wifi_path(path, ".wifi-current")); assert(!unlink(path));
  uint8_t unknown[] = {88, 77, 66}; assert(ap01_wifi_write(".wapi.conf", unknown, sizeof(unknown)));
  ap01_sim_init();
  assert(!g_ap01_sim.wifi_configured && !g_ap01_sim.wifi_connected && !strcmp(g_ap01_wifi_phase, "restore-error"));
  assert(ap01_wifi_read(".wapi.conf", active, sizeof(active)) == 3 && !memcmp(active, unknown, 3));
  assert(ap01_wifi_read(".wifi-current", active, sizeof(active)) == -1);
  assert(ap01_wifi_write(".wapi.conf", home.native, home.length));
  ap01_sim_init(); assert(g_ap01_wifi_active == 0); ip_ready();
  /* Failed candidate returns bytes first, then awaits independent old-net IP. */
  g_ap01_sim.bound = true; assert(ap01_sim_save());
  /* Provisioning edits only the list, even for the currently used SSID. */
  ap01_sim_wifi_profile changed = home; changed.native[1] = 77;
  assert(ap01_wifi_put(0, &changed));
  assert(g_ap01_sim.wifi_connected && g_ap01_sim.bound && g_ap01_wifi_active == 0);
  assert(!memcmp(g_ap01_wifi_current.native, home.native, home.length));
  assert(!ap01_wifi_current_virtual()); /* uniq by SSID, despite different candidate credentials */
  assert(ap01_wifi_read(".wapi.conf", active, sizeof(active)) == 6 && !memcmp(active, home.native, 6));
  ap01_sim_wifi_profile empty = {0}; assert(ap01_wifi_put(0, &empty));
  assert(g_ap01_wifi_active == 8 && ap01_wifi_current_virtual() && g_ap01_sim.wifi_connected && g_ap01_sim.bound);
  assert(!strcmp(ap01_wifi_menu_profile(8)->ssid, "Home"));
  assert(ap01_wifi_read(".wapi.conf", active, sizeof(active)) == 6 && !memcmp(active, home.native, 6));
  assert(ap01_wifi_select(8)); ip_ready(); /* local independent current recovery entry */
  assert(ap01_wifi_put(0, &home)); assert(!ap01_wifi_current_virtual() && g_ap01_wifi_active == 0);
  assert(ap01_wifi_select(3));
  assert(!ap01_wifi_put(1, &home)); assert(!ap01_wifi_release());
  assert(g_ap01_wifi_active == 0 && !g_ap01_sim.wifi_connected && g_ap01_sim.bound);
  assert(ap01_wifi_event(2)); assert(g_ap01_wifi_active == 0 && !g_ap01_wifi_pending);
  assert(!strcmp(g_ap01_wifi_phase, "rollback"));
  assert(ap01_wifi_read(".wapi.conf", active, sizeof(active)) == 6 && !memcmp(active, home.native, 6));
  assert(!ap01_wifi_event(2)); /* rollback can also fail; menu profiles remain */
  assert(!g_ap01_sim.wifi_connected && g_ap01_wifi[0].length && g_ap01_wifi[3].length);
  assert(ap01_wifi_select(0)); ip_ready(); assert(g_ap01_sim.bound);
  /* Pending restart restores previous config, with binding unchanged. */
  assert(ap01_wifi_put(0, &changed));
  assert(ap01_wifi_select(3)); ap01_sim_init();
  assert(!memcmp(g_ap01_wifi_current.native, home.native, home.length));
  assert(g_ap01_wifi_active == 0 && g_ap01_sim.bound && !g_ap01_sim.wifi_connected);
  ip_ready(); assert(ap01_wifi_put(0, &home));
  /* Local old-network selection cancels a pending attempt without host session. */
  assert(ap01_wifi_select(3)); assert(ap01_wifi_select(0)); ip_ready();
  /* A failed storage restore retains the journal and local recovery route. */
  assert(ap01_wifi_select(3));
  assert(ap01_wifi_path(path, ".wapi.conf"));
  snprintf(temporary, sizeof(temporary), "%s.new", path); assert(!mkdir(temporary, 0700));
  assert(!ap01_wifi_event(2));
  assert(!g_ap01_sim.wifi_connected && g_ap01_wifi_pending && !strcmp(g_ap01_wifi_phase, "restore-error"));
  uint8_t journal[AP01_WIFI_SNAPSHOT_MAX];
  assert(ap01_wifi_read(".wifi-pending", journal, sizeof(journal)) == 45 + (int)home.length);
  assert(!rmdir(temporary)); assert(ap01_wifi_select(0)); ip_ready();
  /* No result times out; rollback itself still requires association and IP. */
  g_ap01_wifi_plan = 2; assert(ap01_wifi_select(3));
  ap01_wifi_tick(g_ap01_wifi_deadline);
  assert(g_ap01_wifi_active == 0 && !strcmp(g_ap01_wifi_phase, "rollback")); ip_ready();
  /* Driver outcomes, including a delayed DHCP/IP stage, drive confirmation. */
  g_ap01_wifi_delay = 3000;
  assert(ap01_wifi_select(3));
  ap01_wifi_tick(g_ap01_wifi_due);
  assert(!strcmp(g_ap01_wifi_phase, "waiting-ip") && !g_ap01_sim.wifi_connected);
  ap01_wifi_tick(g_ap01_wifi_due);
  assert(g_ap01_wifi_active == 3 && g_ap01_sim.wifi_connected);
  g_ap01_wifi_delay = 300;
  ap01_sim_init(); assert(g_ap01_wifi_active == 3 && !strcmp(g_ap01_sim.ssid, office.ssid));
  assert(!g_ap01_sim.wifi_connected && g_ap01_sim.wifi_configured); ip_ready();
  assert(ap01_wifi_put(0, &empty));
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
  assert(ap01_wifi_select(2)); ip_ready();
  assert(ap01_wifi_release());
  assert(!g_ap01_sim.wifi_configured && g_ap01_wifi[2].length == 6);
  assert(ap01_wifi_put(2, &empty));
  assert(ap01_wifi_put(2, &home) && ap01_wifi_select(2)); ip_ready();
  /* Corrupt records fail closed, preserve disk evidence and never auto-repair. */
  uint8_t corrupt[] = "AP01WFL1bad"; assert(ap01_wifi_write(".wifi-list", corrupt, sizeof(corrupt)));
  ap01_sim_init(); assert(g_ap01_wifi_invalid && g_ap01_sim.wifi_configured && !g_ap01_sim.wifi_connected);
  assert(g_ap01_wifi_active == 8 && ap01_wifi_current_virtual()); ip_ready();
  assert(!ap01_wifi_put(0, &home)); assert(!ap01_wifi_select(2));
  assert(ap01_wifi_select(8)); ip_ready(); /* corrupt list cannot destroy independent recovery */
  assert(ap01_wifi_write(".wifi-offline-2", staged, 39));
  assert(ap01_sim_factory_reset()); assert(!g_ap01_wifi_invalid && !g_ap01_wifi[2].length);
  ap01_sim_init(); assert(!g_ap01_sim.wifi_configured && g_ap01_wifi_active == -1);
  const char *suffixes[] = {"", ".wifi-list", ".wapi.conf", ".wifi-current"};
  for (unsigned i = 0; i < 4; ++i) { assert(ap01_wifi_path(path, suffixes[i])); assert(!unlink(path)); }
  assert(!rmdir(directory));
  puts("SIM Wi-Fi profiles PASS: opaque byte preservation, unchanged legacy state, asynchronous association/IP, pending restart, offline restore, double failure, timeout, list-only active edits/deletes, SSID uniq current recovery, independent snapshot rollback, binding retention, corruption and reset");
}
