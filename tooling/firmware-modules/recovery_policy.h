#ifndef AP01_RECOVERY_POLICY_H
#define AP01_RECOVERY_POLICY_H
#include <stdint.h>

enum rg_action {
    RG_WAIT=0, RG_SELECT_BASE=1, RG_RUN_TRIAL=2,
    RG_SELECT_TRIAL=3, RG_REBOOT_BASE=4, RG_BASE=5, RG_FAULT=6
};
enum rg_phase { RG_NEW=0, RG_GRACE=1, RG_CONFIRMING=2, RG_CONFIRMED=3, RG_FAILED=4, RG_ESCAPING=5 };
typedef struct { uint32_t phase, armed_ms, healthy_since, tracking_health; } recovery_policy;
/* selected is the independently read-back durable selection, not XIP slot.
 * This policy has no Flash/GPIO drivers and does not run before its caller.
 * commit_failed is terminal for this boot: never continue a failed arm. */
uint32_t recovery_step(recovery_policy *,uint32_t running,uint32_t selected,
                       uint32_t now_ms,uint32_t button_low,uint32_t healthy,
                       uint32_t commit_failed);
/* Firmware bytes only. Trusted redundant-table commits are separate.
 * Prototype policy: fallback updater runs in slot0 and only writes slot1. */
uint32_t recovery_firmware_write_allowed(uint32_t running,uint32_t address,uint32_t length);
#endif
