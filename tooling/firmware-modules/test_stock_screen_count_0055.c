/* Host regression for the production screen registry and native page boundary. */
#include "screen_host_0041.h"
#include "native_rom_addresses.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static unsigned checks;
#define CHECK(expression) do { ++checks; assert(expression); } while (0)

typedef struct {
    unsigned active, slides, source, target, direction;
} Port;

static unsigned active(void *p) { return ((Port *)p)->active; }
static int ready(void *p) { (void)p; return 1; }
static void slide(void *p, unsigned child, unsigned direction) {
    Port *port = (Port *)p;
    ++port->slides;
    port->active = child;
    port->direction = direction;
}
static void edge(void *p, unsigned source, unsigned target) {
    Port *port = (Port *)p;
    port->source = source;
    port->target = target;
}
static int prepare(void *p, ap01_screen_slot *s, uint32_t transition) {
    (void)p; (void)s; (void)transition;
    return AP01_ENTER_READY;
}
static ap01_screen_port port_api(Port *p) {
    ap01_screen_port api = { p, active, ready, ready, slide, edge };
    return api;
}
static ap01_screen_desc page(const char *id) {
    ap01_screen_desc descriptor;
    memset(&descriptor, 0, sizeof(descriptor));
    descriptor.abi_version = AP01_SCREEN_ABI_0041;
    descriptor.struct_bytes = sizeof(descriptor);
    descriptor.screen_id = id;
    descriptor.prepare = prepare;
    descriptor.visible = 1;
    return descriptor;
}
static void complete(ap01_screen_host *host, Port *p, unsigned source,
                     unsigned target, unsigned direction, uint32_t now) {
    unsigned slides = p->slides;
    CHECK(ap01_host_rotate(host, direction == 2 ? 1 : -1, now) == 1);
    CHECK(p->slides == slides + 1);
    CHECK(p->source == source && p->target == target);
    CHECK(p->active == target && p->direction == direction);
    CHECK(host->phase == 2);
    ap01_host_poll(host, now + 1);
    CHECK(host->phase == 0);
}

static void boundaries(void) {
    unsigned child;
    int root;
    Port p = {7, 0, 0, 0, 0};
    ap01_screen_port api = port_api(&p);
    for (child = 0; child < AP01_STOCK_SCREEN_COUNT + 4; ++child) {
        ap01_screen_host host;
        ap01_screen_slot slot;
        ap01_screen_app app;
        memset(&slot, 0, sizeof(slot));
        memset(&app, 0, sizeof(app));
        slot.root = &root;
        slot.child = child;
        app.app_id = "one";
        app.slots = &slot;
        app.capacity = 1;
        CHECK(ap01_host_init(&host, &api, &app, 1) ==
              (child < AP01_STOCK_SCREEN_COUNT ? AP01_HOST_INVALID : AP01_HOST_OK));
    }
}

static void registry_and_navigation(void) {
    int roots[4];
    unsigned i;
    Port p = {7, 0, 0, 0, 0};
    ap01_screen_port api = port_api(&p);
    ap01_screen_host host;
    ap01_screen_slot slots[4];
    ap01_screen_app apps[2];
    ap01_screen_desc first[2] = {page("a"), page("b")};
    ap01_screen_desc second[2] = {page("c"), page("d")};
    memset(slots, 0, sizeof(slots));
    memset(apps, 0, sizeof(apps));
    for (i = 0; i < 4; ++i) {
        slots[i].root = &roots[i];
        slots[i].child = AP01_STOCK_SCREEN_COUNT + i;
    }
    apps[0].app_id = "first"; apps[0].slots = slots; apps[0].capacity = 2;
    apps[1].app_id = "second"; apps[1].slots = slots + 2; apps[1].capacity = 2;
    CHECK(ap01_host_init(&host, &api, apps, 1) == AP01_HOST_OK);
    CHECK(ap01_host_replace(&apps[0], 0, first, 2) == AP01_HOST_OK);

    /* Registration rejects stock children and overlap across different Apps. */
    slots[2].child = AP01_STOCK_SCREEN_COUNT - 1;
    CHECK(ap01_host_append(&host, apps, 2) == AP01_HOST_INVALID);
    CHECK(host.app_count == 1 && apps[1].host == NULL);
    slots[2].child = slots[1].child;
    CHECK(ap01_host_append(&host, apps, 2) == AP01_HOST_INVALID);
    CHECK(host.app_count == 1 && apps[1].host == NULL);
    slots[2].child = AP01_STOCK_SCREEN_COUNT + 2;
    slots[2].root = slots[1].root;
    CHECK(ap01_host_append(&host, apps, 2) == AP01_HOST_INVALID);
    slots[2].root = &roots[2];
    CHECK(ap01_host_append(&host, apps, 2) == AP01_HOST_OK);
    CHECK(ap01_host_replace(&apps[1], 0, second, 2) == AP01_HOST_OK);
    CHECK(host.app_count == 2 && apps[0].count == 2 && apps[1].count == 2);

    /* Added native children receive native input, never App navigation. */
    for (i = 0; i < AP01_STOCK_SCREEN_COUNT; ++i) {
        p.active = i;
        CHECK(ap01_host_current(&host) == NULL);
        if (i != 6 && i != 7) {
            unsigned before = p.slides;
            CHECK(ap01_host_rotate(&host, 1, 10) == 0);
            CHECK(ap01_host_rotate(&host, -1, 11) == 0);
            CHECK(ap01_host_short(&host) == 0);
            CHECK(p.slides == before);
        }
    }

    p.active = 7;
    complete(&host, &p, 7, AP01_STOCK_SCREEN_COUNT, 2, 100);
    for (i = 0; i < 3; ++i) {
        CHECK(ap01_host_current(&host) == &slots[i]);
        complete(&host, &p, AP01_STOCK_SCREEN_COUNT + i,
                 AP01_STOCK_SCREEN_COUNT + i + 1, 2, 110 + i * 2);
    }
    CHECK(ap01_host_current(&host) == &slots[3]);
    complete(&host, &p, AP01_STOCK_SCREEN_COUNT + 3, 6, 2, 120);
    CHECK(ap01_host_current(&host) == NULL);
    complete(&host, &p, 6, AP01_STOCK_SCREEN_COUNT + 3, 1, 130);
    for (i = 3; i > 0; --i)
        complete(&host, &p, AP01_STOCK_SCREEN_COUNT + i,
                 AP01_STOCK_SCREEN_COUNT + i - 1, 1, 140 + i * 2);
    complete(&host, &p, AP01_STOCK_SCREEN_COUNT, 7, 1, 150);
    CHECK(ap01_host_current(&host) == NULL);
    ap01_host_destroy(&host);
    CHECK(apps[0].host == NULL && apps[1].host == NULL);
}

int main(void) {
    boundaries();
    registry_and_navigation();
    printf("{\"stock_count\":%u,\"checks\":%u,\"passed\":true}\n",
           (unsigned)AP01_STOCK_SCREEN_COUNT, checks);
    return 0;
}
