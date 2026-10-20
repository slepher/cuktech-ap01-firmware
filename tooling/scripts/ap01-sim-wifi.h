/* SPDX-License-Identifier: Apache-2.0 */
/* SIM-only profiles. Native configuration is opaque: never add list metadata
 * to it, parse/re-serialize it, or claim a guessed password layout is native. */
#ifndef AP01_SIM_WIFI_H
#define AP01_SIM_WIFI_H
#include <fcntl.h>
#include <sys/stat.h>
#define AP01_WIFI_SLOTS 8
#define AP01_WIFI_NATIVE_MAX 1024
#define AP01_WIFI_WIRE_MAX (8 + AP01_WIFI_SLOTS * (33 + 4 + AP01_WIFI_NATIVE_MAX) + 4)
typedef struct { char ssid[33]; unsigned length; uint8_t native[AP01_WIFI_NATIVE_MAX]; } ap01_sim_wifi_profile;
static ap01_sim_wifi_profile g_ap01_wifi[AP01_WIFI_SLOTS];
static int g_ap01_wifi_active = -1;
static bool g_ap01_wifi_invalid;

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

static void ap01_wifi_init(void)
{
  memset(g_ap01_wifi, 0, sizeof(g_ap01_wifi)); g_ap01_wifi_active = -1;
  g_ap01_wifi_invalid = !ap01_wifi_load();
  if (g_ap01_wifi_invalid)
    { memset(g_ap01_wifi, 0, sizeof(g_ap01_wifi)); ap01_wifi_error("wifi-list-corrupt"); }
  uint8_t active[AP01_WIFI_NATIVE_MAX];
  int n = ap01_wifi_read(".wapi.conf", active, sizeof(active));
  if (n == -1) return; /* Existing SCF1 state remains readable, unchanged. */
  if (n == 0) { g_ap01_sim.wifi_configured = false; g_ap01_sim.ssid[0] = 0; return; }
  for (unsigned i = 0; !g_ap01_wifi_invalid && i < AP01_WIFI_SLOTS; ++i)
    if (n > 0 && (unsigned)n == g_ap01_wifi[i].length && !memcmp(active, g_ap01_wifi[i].native, n))
      { g_ap01_wifi_active = (int)i; break; }
  if (g_ap01_wifi_active < 0)
    { g_ap01_sim.wifi_configured = false; g_ap01_sim.ssid[0] = 0; ap01_wifi_error("active-config-unmatched-or-corrupt"); }
  else
    { g_ap01_sim.wifi_configured = true; memcpy(g_ap01_sim.ssid, g_ap01_wifi[g_ap01_wifi_active].ssid, 33); }
}

static bool ap01_wifi_put(unsigned slot, const ap01_sim_wifi_profile *profile)
{
  if (g_ap01_wifi_invalid) return ap01_wifi_error("wifi-list-corrupt");
  if (slot >= AP01_WIFI_SLOTS || !profile || !ap01_wifi_valid(profile)) return ap01_wifi_error("invalid-profile");
  if ((int)slot == g_ap01_wifi_active) return ap01_wifi_error("select-another-network-before-editing-active");
  for (unsigned i = 0; i < AP01_WIFI_SLOTS; ++i)
    if (i != slot && profile->length && (strcmp(profile->ssid, g_ap01_wifi[i].ssid) == 0 ||
        (profile->length == g_ap01_wifi[i].length && !memcmp(profile->native, g_ap01_wifi[i].native, profile->length))))
      return ap01_wifi_error("duplicate-network-or-config");
  if (!ap01_sim_command("wifi-put")) return false;
  ap01_sim_wifi_profile old = g_ap01_wifi[slot]; g_ap01_wifi[slot] = *profile;
  if (!ap01_wifi_save()) { g_ap01_wifi[slot] = old; return false; }
  return ap01_sim_reply("wifi-put", AP01_SIM_OK, "committed", "");
}

static bool ap01_wifi_select(unsigned slot)
{
  if (g_ap01_wifi_invalid || slot >= AP01_WIFI_SLOTS || !g_ap01_wifi[slot].length)
    return ap01_wifi_error("network-unavailable");
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK || g_ap01_sim.binding == AP01_SIM_PENDING)
    return ap01_wifi_error("update-or-binding-busy");
  if (!ap01_sim_command("wifi-select")) return false;
  /* The authoritative active file is EXACT native bytes, with no header or
   * checksum of ours. Startup matches it to the separately stored profile. */
  if (!ap01_wifi_write(".wapi.conf", g_ap01_wifi[slot].native, g_ap01_wifi[slot].length)) return false;
  ap01_sim_wifi_disconnect();
  g_ap01_wifi_active = (int)slot;
  memcpy(g_ap01_sim.ssid, g_ap01_wifi[slot].ssid, 33);
  g_ap01_sim.wifi_configured = true;
  /* Only simulated association; writing credentials cannot prove RF success. */
  g_ap01_sim.wifi_connected = true;
  return ap01_sim_reply("wifi-select", AP01_SIM_OK, "simulated-connected", "");
}

static bool ap01_wifi_release(void)
{
  if (g_ap01_sim.ota == AP01_SIM_PENDING || g_ap01_sim.ota == AP01_SIM_OK || g_ap01_sim.binding == AP01_SIM_PENDING)
    return ap01_wifi_error("update-or-binding-busy");
  if (!ap01_sim_command("wifi-release")) return false;
  /* Empty native file is a SIM deactivation tombstone, never a real config. */
  if (!ap01_wifi_write(".wapi.conf", NULL, 0)) return false;
  ap01_sim_wifi_disconnect();
  g_ap01_wifi_active = -1;
  g_ap01_sim.wifi_configured = false;
  g_ap01_sim.ssid[0] = 0;
  return ap01_sim_reply("wifi-release", AP01_SIM_OK, "deactivated", "");
}

static bool ap01_wifi_reset(void)
{
  /* Factory reset owns cancellation of pending binding, unlike release. */
  if (!ap01_wifi_write(".wapi.conf", NULL, 0)) return false;
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
