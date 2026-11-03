#pragma once
#include "app_runtime_v3.h"
// Source adapter for the existing renderer/host integration. The referenced
// host/window/registry slot are owned by the resident platform.
#define ap01_lvgl_0041 (*ap01RuntimeApiV3()->ui.lvgl)
#define ap01_host_api (*ap01RuntimeApiV3()->ui.screens)
#define ap01_host_find ap01_host_api.find_screen
#define ap01_host_enter_ready ap01_host_api.enter_ready
#define ap01_host_current ap01RuntimeApiV3()->ui.current
#define ap01_host_retire ap01RuntimeApiV3()->ui.retire
#define ap01_host_poll ap01RuntimeApiV3()->ui.poll
#define ap01_host_set_blocked ap01RuntimeApiV3()->ui.blocked
#define ap01_host_cancel ap01RuntimeApiV3()->ui.cancel
#define ap01_host_button ap01RuntimeApiV3()->ui.button
#define ap01_host_rotate ap01RuntimeApiV3()->ui.rotate
#define ap01_host_short ap01RuntimeApiV3()->ui.short_press
#define ap01_window_active ap01RuntimeApiV3()->ui.active
#define ap01_window_visible ap01RuntimeApiV3()->ui.visible
#define ap01_window_awake ap01RuntimeApiV3()->ui.awake
#define ap01_window_idle ap01RuntimeApiV3()->ui.idle
#define ap01_window_overlay ap01RuntimeApiV3()->ui.overlay
#define ap01_window_activity ap01RuntimeApiV3()->ui.activity
#define ap01_window_wake ap01RuntimeApiV3()->ui.wake
#define ap01_event_code ap01RuntimeApiV3()->ui.event_code
#define ap01_event_key ap01RuntimeApiV3()->ui.event_key
#define ap01_event_context ap01RuntimeApiV3()->ui.event_context
#define ap01_event_target ap01RuntimeApiV3()->ui.event_target
