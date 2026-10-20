/* SPDX-License-Identifier: Apache-2.0 */
/* SIM-only profiles. Native configuration is opaque: never add list metadata
 * to it, parse/re-serialize it, or claim a guessed password layout is native. */
#ifndef AP01_SIM_WIFI_H
#define AP01_SIM_WIFI_H
#include <fcntl.h>
#include <sys/stat.h>
#define AP01_WIFI_SLOTS 8
#define AP01_WIFI_NATIVE_MAX 1024
#define AP01_WIFI_MENU_END (AP01_WIFI_SLOTS + 1)
#define AP01_WIFI_SNAPSHOT_MAX (4 + 33 + 4 + AP01_WIFI_NATIVE_MAX + 4)
#define AP01_WIFI_WIRE_MAX (8 + AP01_WIFI_SLOTS * (33 + 4 + AP01_WIFI_NATIVE_MAX) + 4)
typedef struct { char ssid[33]; unsigned length; uint8_t native[AP01_WIFI_NATIVE_MAX]; } ap01_sim_wifi_profile;
static ap01_sim_wifi_profile g_ap01_wifi[AP01_WIFI_SLOTS];
/* List edits never mutate these independent connection snapshots. */
static ap01_sim_wifi_profile g_ap01_wifi_current, g_ap01_wifi_attempt, g_ap01_wifi_old;
static int g_ap01_wifi_active = -1;
static bool g_ap01_wifi_invalid;
/* SIM network driver results are separate from opaque configuration storage. */
static int g_ap01_wifi_target = -1, g_ap01_wifi_previous = -1;
static bool g_ap01_wifi_pending, g_ap01_wifi_restoring;
static const char *g_ap01_wifi_phase = "disconnected";
static unsigned g_ap01_wifi_plan, g_ap01_wifi_rollback_plan, g_ap01_wifi_delay = 300;
static unsigned g_ap01_wifi_result, g_ap01_wifi_step;
static uint64_t g_ap01_wifi_due, g_ap01_wifi_deadline;
static bool ap01_wifi_has_attempt(void) { return g_ap01_wifi_due != 0; }
static void ap01_wifi_tick(uint64_t now);
static void ap01_wifi_start(int slot, bool restoring);

static bool ap01_wifi_error(const char *error)
{ return ap01_sim_reply("wifi-profiles", AP01_SIM_ERROR, "storage-or-validation", error); }

static bool ap01_wifi_path(char path[256], const char *suffix)
{
  int n = snprintf(path, 256, "%s%s", AP01_SIM_STATE_PATH, suffix);
  return n > 0 && n < 256;
}

/* Write to a private sibling and rename only after sync. Failed writes leave
 * the previous file untouched. Payloads and passwords never enter replies. */
static bool ap01_wifi_write(const char *suffix, const uint8_t *data, size_t length)
{
  char path[256], temp[260];
  if (!ap01_wifi_path(path, suffix)) return ap01_wifi_error("path-too-long");
  snprintf(temp, sizeof(temp), "%s.new", path);
  int fd = open(temp, O_WRONLY | O_CREAT | O_TRUNC, 0600);
  if (fd < 0) return ap01_wifi_error("open-failed");
  bool ok = fchmod(fd, 0600) == 0;
  size_t done = 0;
  while (ok && done < length)
    {
      ssize_t n = write(fd, data + done, length - done);
      if (n <= 0) ok = false; else done += (size_t)n;
    }
  if (fsync(fd)) ok = false;
  if (close(fd)) ok = false;
  if (!ok || rename(temp, path)) { unlink(temp); return ap01_wifi_error("commit-failed"); }
  return true;
}

/* -1 means absent; -2 means unreadable or oversized. */
static int ap01_wifi_read(const char *suffix, uint8_t *data, size_t capacity)
{
  char path[256];
  if (!ap01_wifi_path(path, suffix)) return -2;
  FILE *file = fopen(path, "rb");
  if (!file) return errno == ENOENT ? -1 : -2;
  size_t n = fread(data, 1, capacity, file);
  bool ok = !ferror(file) && fgetc(file) == EOF;
  if (fclose(file)) ok = false;
  return ok ? (int)n : -2;
}

static bool ap01_wifi_valid(const ap01_sim_wifi_profile *p)
{
  size_t n = strnlen(p->ssid, sizeof(p->ssid));
  if (!p->length) return !n;
  if (!n || n > 32 || p->length > AP01_WIFI_NATIVE_MAX) return false;
  for (size_t i = 0; i < n; ++i)
    {
      unsigned c = (unsigned char)p->ssid[i];
      if (c < 32 || c == 127) return false;
      if (c < 128) continue;
      unsigned extra = c >= 0xc2 && c <= 0xdf ? 1 : c >= 0xe0 && c <= 0xef ? 2 : c >= 0xf0 && c <= 0xf4 ? 3 : 0;
      if (!extra || i + extra >= n) return false;
      unsigned cp = c & (0x7f >> extra);
      for (unsigned j = 0; j < extra; ++j)
        {
          unsigned next = (unsigned char)p->ssid[++i];
          if ((next & 0xc0) != 0x80) return false;
          cp = (cp << 6) | (next & 0x3f);
        }
      if ((extra == 2 && cp < 0x800) || (extra == 3 && cp < 0x10000) ||
          (cp >= 0xd800 && cp <= 0xdfff) || cp > 0x10ffff) return false;
    }
  return true;
}

static bool ap01_wifi_save(void)
{
  uint8_t wire[AP01_WIFI_WIRE_MAX], *out = wire;
  memcpy(out, "AP01WFL1", 8); out += 8;
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
    {
      memcpy(out, g_ap01_wifi[i].ssid, 33); out += 33;
      ap01_sim_put32(&out, g_ap01_wifi[i].length);
      memcpy(out, g_ap01_wifi[i].native, g_ap01_wifi[i].length); out += g_ap01_wifi[i].length;
    }
  uint32_t crc = ap01_sim_crc(wire, out - wire);
  ap01_sim_put32(&out, crc);
  return ap01_wifi_write(".wifi-list", wire, out - wire);
}

static bool ap01_wifi_load(void)
{
  uint8_t wire[AP01_WIFI_WIRE_MAX];
  int n = ap01_wifi_read(".wifi-list", wire, sizeof(wire));
  if (n == -1) return true;
  if (n < 8 + AP01_WIFI_SLOTS * 37 + 4 || memcmp(wire, "AP01WFL1", 8)) return false;
  const uint8_t *end = wire + n - 4, *checksum = end, *in = wire + 8;
  if (ap01_sim_get32(&checksum) != ap01_sim_crc(wire, n - 4)) return false;
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
    {
      if (end - in < 37) return false;
      ap01_sim_wifi_profile *p = &g_ap01_wifi[i];
      memcpy(p->ssid, in, 33); in += 33;
      p->length = ap01_sim_get32(&in);
      if (!ap01_wifi_valid(p) || end - in < (ptrdiff_t)p->length) return false;
      memcpy(p->native, in, p->length); in += p->length;
      for (unsigned j = 0; j < i; ++j)
        if (p->length && (strcmp(p->ssid, g_ap01_wifi[j].ssid) == 0 ||
            (p->length == g_ap01_wifi[j].length && !memcmp(p->native, g_ap01_wifi[j].native, p->length)))) return false;
    }
  return in == end;
}

/* Private SIM snapshots identify opaque bytes without inferring their format. */
static bool ap01_wifi_snapshot_save(const char *suffix, const char magic[4],
                                     const ap01_sim_wifi_profile *profile)
{
  uint8_t wire[AP01_WIFI_SNAPSHOT_MAX], *out = wire;
  memcpy(out, magic, 4); out += 4;
  memcpy(out, profile->ssid, 33); out += 33;
  ap01_sim_put32(&out, profile->length);
  memcpy(out, profile->native, profile->length); out += profile->length;
  ap01_sim_put32(&out, ap01_sim_crc(wire, out - wire));
  return ap01_wifi_write(suffix, wire, out - wire);
}

/* -1 absent, 0 corrupt, 1 valid (including a deactivated empty snapshot). */
static int ap01_wifi_snapshot_load(const char *suffix, const char magic[4],
                                    ap01_sim_wifi_profile *profile)
{
  uint8_t wire[AP01_WIFI_SNAPSHOT_MAX];
  int n = ap01_wifi_read(suffix, wire, sizeof(wire));
  if (n == -1) return -1;
  if (n < 45 || memcmp(wire, magic, 4)) return 0;
  ap01_sim_wifi_profile value = {0}; const uint8_t *in = wire + 4;
  memcpy(value.ssid, in, 33); in += 33; value.length = ap01_sim_get32(&in);
  if (!ap01_wifi_valid(&value) || n != (int)(45 + value.length)) return 0;
  memcpy(value.native, in, value.length); in += value.length;
  if (ap01_sim_get32(&in) != ap01_sim_crc(wire, n - 4)) return 0;
  *profile = value;
  return 1;
}

static int ap01_wifi_find_ssid(const ap01_sim_wifi_profile *profile)
{
  if (!profile->length) return -1;
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
    if (g_ap01_wifi[i].length && !strcmp(g_ap01_wifi[i].ssid, profile->ssid)) return (int)i;
  return AP01_WIFI_SLOTS; /* independent current recovery entry */
}

static const ap01_sim_wifi_profile *ap01_wifi_menu_profile(unsigned slot)
{
  return slot < AP01_WIFI_SLOTS ? &g_ap01_wifi[slot] :
    slot == AP01_WIFI_SLOTS ? &g_ap01_wifi_current : NULL;
}

static bool ap01_wifi_current_virtual(void)
{ return ap01_wifi_find_ssid(&g_ap01_wifi_current) == AP01_WIFI_SLOTS; }

static bool ap01_wifi_restore_snapshot(const ap01_sim_wifi_profile *profile)
{
  return ap01_wifi_write(".wapi.conf", profile->native, profile->length) &&
    ap01_wifi_snapshot_save(".wifi-current", "WFC1", profile);
}

static void ap01_wifi_init(void)
{
  g_ap01_wifi_pending = g_ap01_wifi_restoring = false;
  g_ap01_wifi_target = g_ap01_wifi_previous = -1;
  g_ap01_wifi_due = g_ap01_wifi_deadline = 0;
  g_ap01_wifi_plan = g_ap01_wifi_rollback_plan = 0; g_ap01_wifi_delay = 300;
  g_ap01_wifi_phase = "disconnected";
  memset(&g_ap01_wifi_current, 0, sizeof(g_ap01_wifi_current));
  memset(&g_ap01_wifi_attempt, 0, sizeof(g_ap01_wifi_attempt));
  memset(&g_ap01_wifi_old, 0, sizeof(g_ap01_wifi_old));
  memset(g_ap01_wifi, 0, sizeof(g_ap01_wifi)); g_ap01_wifi_active = -1;
  g_ap01_wifi_invalid = !ap01_wifi_load();
  if (g_ap01_wifi_invalid)
    { memset(g_ap01_wifi, 0, sizeof(g_ap01_wifi)); ap01_wifi_error("wifi-list-corrupt"); }
  /* Full old bytes survive edits/deletions of every list entry. A legacy WFP1
   * journal is rejected and preserved rather than guessed from mutable slots. */
  ap01_sim_wifi_profile old = {0};
  int pending = ap01_wifi_snapshot_load(".wifi-pending", "WFP2", &old);
  if (pending != -1)
    {
      char path[256];
      if (pending != 1 || !ap01_wifi_restore_snapshot(&old) ||
          !ap01_wifi_path(path, ".wifi-pending") || unlink(path))
        {
          g_ap01_sim.wifi_configured = g_ap01_sim.wifi_connected = false;
          g_ap01_sim.ssid[0] = 0; g_ap01_wifi_phase = "restore-error";
          ap01_wifi_error("pending-recovery-failed"); return;
        }
    }
  uint8_t active[AP01_WIFI_NATIVE_MAX];
  int n = ap01_wifi_read(".wapi.conf", active, sizeof(active));
  int current = ap01_wifi_snapshot_load(".wifi-current", "WFC1", &g_ap01_wifi_current);
  if (current == -1 && n == -1) return; /* legacy SCF1 remains readable */
  if (current == -1 && n >= 0)
    {
      if (n > 0 && !g_ap01_wifi_invalid)
        for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
          if ((unsigned)n == g_ap01_wifi[i].length && !memcmp(active, g_ap01_wifi[i].native, n))
            { g_ap01_wifi_current = g_ap01_wifi[i]; current = 1; break; }
      if (!n) current = 1;
      if (current == 1 && !ap01_wifi_snapshot_save(".wifi-current", "WFC1", &g_ap01_wifi_current)) current = 0;
    }
  if (current != 1 || n < 0 || (unsigned)n != g_ap01_wifi_current.length ||
      (n && memcmp(active, g_ap01_wifi_current.native, n)))
    {
      memset(&g_ap01_wifi_current, 0, sizeof(g_ap01_wifi_current));
      g_ap01_sim.wifi_configured = g_ap01_sim.wifi_connected = false;
      g_ap01_sim.ssid[0] = 0; g_ap01_wifi_phase = "restore-error";
      ap01_wifi_error("current-config-unmatched-or-corrupt"); return;
    }
  g_ap01_sim.wifi_configured = g_ap01_wifi_current.length != 0;
  memcpy(g_ap01_sim.ssid, g_ap01_wifi_current.ssid, 33);
  g_ap01_wifi_active = ap01_wifi_find_ssid(&g_ap01_wifi_current);
  if (g_ap01_wifi_current.length)
    { g_ap01_wifi_attempt = g_ap01_wifi_current; ap01_wifi_start(g_ap01_wifi_active, true); }
}

static bool ap01_wifi_put(unsigned slot, const ap01_sim_wifi_profile *profile)
{
  if (g_ap01_wifi_pending) return ap01_wifi_error("network-attempt-busy");
  if (g_ap01_wifi_invalid) return ap01_wifi_error("wifi-list-corrupt");
  if (slot >= AP01_WIFI_SLOTS || !profile || !ap01_wifi_valid(profile)) return ap01_wifi_error("invalid-profile");
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
    if (i != slot && profile->length && (strcmp(profile->ssid, g_ap01_wifi[i].ssid) == 0 ||
        (profile->length == g_ap01_wifi[i].length && !memcmp(profile->native, g_ap01_wifi[i].native, profile->length))))
      return ap01_wifi_error("duplicate-network-or-config");
  if (!ap01_sim_command("wifi-put")) return false;
  ap01_sim_wifi_profile old = g_ap01_wifi[slot]; g_ap01_wifi[slot] = *profile;
  if (!ap01_wifi_save()) { g_ap01_wifi[slot] = old; return false; }
  g_ap01_wifi_active = ap01_wifi_find_ssid(&g_ap01_wifi_current);
  if (g_ap01_wifi_restoring && g_ap01_wifi_due) g_ap01_wifi_target = g_ap01_wifi_active;
  return ap01_sim_reply("wifi-put", AP01_SIM_OK, "list-only", "");
}

static bool ap01_wifi_clear_pending(void)
{
  char path[256];
  if (!ap01_wifi_path(path, ".wifi-pending") || (unlink(path) && errno != ENOENT))
    return ap01_wifi_error("pending-clear-failed");
  g_ap01_wifi_pending = false;
  return true;
}

static void ap01_wifi_start(int slot, bool restoring)
{
  g_ap01_wifi_target = slot; g_ap01_wifi_restoring = restoring;
  g_ap01_wifi_step = 0;
  g_ap01_wifi_result = restoring ? g_ap01_wifi_rollback_plan : g_ap01_wifi_plan;
  g_ap01_wifi_phase = restoring ? "rollback" : "associating";
  g_ap01_wifi_due = ap01_sim_millis() + g_ap01_wifi_delay;
  g_ap01_wifi_deadline = g_ap01_wifi_due + g_ap01_wifi_delay + 3000;
  g_ap01_sim.wifi_connected = false;
}

static bool ap01_wifi_rollback(void)
{
  g_ap01_wifi_due = 0; g_ap01_sim.wifi_connected = false;
  if (!ap01_wifi_restore_snapshot(&g_ap01_wifi_old) || !ap01_wifi_clear_pending())
    { g_ap01_wifi_phase = "restore-error"; return false; }
  g_ap01_wifi_current = g_ap01_wifi_old;
  g_ap01_wifi_active = ap01_wifi_find_ssid(&g_ap01_wifi_current);
  g_ap01_sim.wifi_configured = g_ap01_wifi_current.length != 0;
  memcpy(g_ap01_sim.ssid, g_ap01_wifi_current.ssid, 33);
  if (g_ap01_wifi_current.length)
    { g_ap01_wifi_attempt = g_ap01_wifi_current; ap01_wifi_start(g_ap01_wifi_active, true); }
  else { g_ap01_wifi_target = -1; g_ap01_wifi_phase = "disconnected"; }
  return ap01_sim_reply("wifi-select", AP01_SIM_PENDING, "rollback", "");
}

/* Events 0=associated, 1=IP ready, 2=failed. The same explicit events are
 * emitted by the deterministic SIM network driver, never by file writes. */
static bool ap01_wifi_event(unsigned event)
{
  if (!g_ap01_wifi_due || event > 2) return ap01_wifi_error("no-network-attempt");
  if (event == 0)
    {
      g_ap01_wifi_step = 1; g_ap01_wifi_phase = "waiting-ip";
      return ap01_sim_reply("wifi-select", AP01_SIM_PENDING, "waiting-ip", "");
    }
  if (event == 1)
    {
      if (!g_ap01_wifi_step) return ap01_wifi_error("association-required");
      if (!ap01_wifi_snapshot_save(".wifi-current", "WFC1", &g_ap01_wifi_attempt) ||
          (g_ap01_wifi_pending && !ap01_wifi_clear_pending()))
        { g_ap01_wifi_phase = "restore-error"; g_ap01_wifi_due = 0; return false; }
      g_ap01_wifi_current = g_ap01_wifi_attempt;
      g_ap01_wifi_active = ap01_wifi_find_ssid(&g_ap01_wifi_current);
      g_ap01_wifi_target = g_ap01_wifi_active;
      memcpy(g_ap01_sim.ssid, g_ap01_wifi_current.ssid, 33);
      g_ap01_sim.wifi_configured = g_ap01_sim.wifi_connected = true;
      g_ap01_wifi_due = 0; g_ap01_wifi_phase = "confirmed";
      return ap01_sim_reply("wifi-select", AP01_SIM_OK, "ip-confirmed", "");
    }
  g_ap01_sim.wifi_connected = false;
  if (g_ap01_wifi_pending) return ap01_wifi_rollback();
  g_ap01_wifi_due = 0; g_ap01_wifi_phase = "disconnected";
  return ap01_sim_reply("wifi-select", AP01_SIM_ERROR, "network", "association-or-ip-failed");
}

static void ap01_wifi_tick(uint64_t now)
{
  if (!g_ap01_wifi_due) return;
  if (now >= g_ap01_wifi_deadline) { ap01_wifi_event(2); return; }
  if (now < g_ap01_wifi_due || g_ap01_wifi_result == 2) return;
  if (g_ap01_wifi_result == 1) { ap01_wifi_event(2); return; }
  if (!g_ap01_wifi_step)
    { ap01_wifi_event(0); g_ap01_wifi_due = now + g_ap01_wifi_delay; }
  else ap01_wifi_event(1);
}

static bool ap01_wifi_select(unsigned slot)
{
  const ap01_sim_wifi_profile *profile = ap01_wifi_menu_profile(slot);
  if (!profile || !profile->length || (g_ap01_wifi_invalid && slot != AP01_WIFI_SLOTS))
    return ap01_wifi_error("network-unavailable");
  if (g_ap01_wifi_pending)
    return !strcmp(profile->ssid, g_ap01_wifi_old.ssid) ? ap01_wifi_rollback() : ap01_wifi_error("network-attempt-busy");
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK || g_ap01_sim.binding == AP01_SIM_PENDING)
    return ap01_wifi_error("update-or-binding-busy");
  if (!ap01_sim_command("wifi-select")) return false;
  if (!ap01_wifi_snapshot_save(".wifi-pending", "WFP2", &g_ap01_wifi_current)) return false;
  g_ap01_wifi_old = g_ap01_wifi_current; g_ap01_wifi_attempt = *profile;
  g_ap01_wifi_previous = ap01_wifi_find_ssid(&g_ap01_wifi_old); g_ap01_wifi_pending = true;
  if (!ap01_wifi_write(".wapi.conf", g_ap01_wifi_attempt.native, g_ap01_wifi_attempt.length))
    { ap01_wifi_clear_pending(); return false; }
  ap01_sim_wifi_disconnect();
  ap01_wifi_start((int)slot, false);
  g_ap01_wifi_plan = 0;
  return ap01_sim_reply("wifi-select", AP01_SIM_PENDING, "associating", "");
}

static bool ap01_wifi_release(void)
{
  if (g_ap01_wifi_pending || g_ap01_wifi_due) return ap01_wifi_error("network-attempt-busy");
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK || g_ap01_sim.binding == AP01_SIM_PENDING)
    return ap01_wifi_error("update-or-binding-busy");
  if (!ap01_sim_command("wifi-release")) return false;
  /* Empty native file is a SIM deactivation tombstone, never a real config. */
  ap01_sim_wifi_profile empty = {0};
  if (!ap01_wifi_restore_snapshot(&empty)) return false;
  memset(&g_ap01_wifi_current, 0, sizeof(g_ap01_wifi_current));
  ap01_sim_wifi_disconnect();
  g_ap01_wifi_active = g_ap01_wifi_target = -1;
  g_ap01_wifi_phase = "disconnected";
  g_ap01_sim.wifi_configured = false;
  g_ap01_sim.ssid[0] = 0;
  return ap01_sim_reply("wifi-release", AP01_SIM_OK, "deactivated", "");
}

static bool ap01_wifi_reset(void)
{
  /* Factory reset owns cancellation of pending binding, unlike release. */
  if (!ap01_wifi_clear_pending()) return false;
  g_ap01_wifi_due = 0; g_ap01_wifi_target = g_ap01_wifi_previous = -1;
  g_ap01_wifi_phase = "disconnected";
  ap01_sim_wifi_profile empty = {0};
  if (!ap01_wifi_restore_snapshot(&empty)) return false;
  memset(&g_ap01_wifi_current, 0, sizeof(g_ap01_wifi_current));
  memset(&g_ap01_wifi_attempt, 0, sizeof(g_ap01_wifi_attempt));
  memset(&g_ap01_wifi_old, 0, sizeof(g_ap01_wifi_old));
  g_ap01_wifi_active = -1;
  g_ap01_sim.wifi_connected = g_ap01_sim.wifi_configured = false;
  g_ap01_sim.ssid[0] = 0;
  memset(g_ap01_wifi, 0, sizeof(g_ap01_wifi));
  if (!ap01_wifi_save()) { g_ap01_wifi_invalid = true; return false; }
  g_ap01_wifi_invalid = false;
  /* A reset must not re-import previously staged credentials at next boot. */
  for (unsigned i = 0; i <= AP01_WIFI_SLOTS; ++i)
    {
      char suffix[32], path[256];
      if (i == AP01_WIFI_SLOTS) snprintf(suffix, sizeof(suffix), ".wifi-input");
      else snprintf(suffix, sizeof(suffix), ".wifi-offline-%u", i);
      if (!ap01_wifi_path(path, suffix) || (unlink(path) && errno != ENOENT))
        return ap01_wifi_error("staged-config-cleanup-failed");
    }
  return true;
}

/* Alternate offline entry: the host can stage this bounded binary file before
 * startup. It is also used by the existing session/id management transport. */
static bool ap01_wifi_import_file(unsigned slot, const char *suffix)
{
  uint8_t wire[33 + AP01_WIFI_NATIVE_MAX];
  int n = ap01_wifi_read(suffix, wire, sizeof(wire));
  if (n <= 33) return ap01_wifi_error("invalid-import");
  ap01_sim_wifi_profile p = {0}; memcpy(p.ssid, wire, 33);
  p.length = (unsigned)n - 33; memcpy(p.native, wire + 33, p.length);
  bool ok = ap01_wifi_put(slot, &p);
  char path[256]; if (ok && ap01_wifi_path(path, suffix)) unlink(path);
  return ok;
}
static void ap01_wifi_offline(void)
{
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
    {
      char suffix[32], path[256];
      snprintf(suffix, sizeof(suffix), ".wifi-offline-%u", i);
      if (ap01_wifi_path(path, suffix) && access(path, F_OK) == 0)
        ap01_wifi_import_file(i, suffix);
    }
}
#endif
