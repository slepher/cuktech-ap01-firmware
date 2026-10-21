#pragma once
/* Opt-in offline fixture; not linked into ordinary application candidates. */
#include "screen_port_0041.h"
struct ap01_test_peer_0041 {
    ap01_screen_slot slots[2]{};
    ap01_page_0041 pages[2]{};
    ap01_screen_app *app=nullptr;
    unsigned polls=0,draws=0,inputs=0,escapes=0,drawEvents=0,matchedEvents=0;
};
int ap01_test_peer_mount(ap01_test_peer_0041 *,ap01_screen_app *,ap01_window_0041 *);
int ap01_test_peer_replace(ap01_test_peer_0041 *,unsigned count,int reverse);
int ap01_test_peer_hidden(ap01_test_peer_0041 *);
unsigned ap01_test_peer_diagnostic(ap01_test_peer_0041 *,unsigned);
