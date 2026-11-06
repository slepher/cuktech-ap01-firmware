// Four exact-stock call-site continuations; no writable state.
#if defined(AP01_ROM_0055)
// 0055 schedules the event-filter setup before the call, then materializes
// the next callback argument in the two instructions covered by our jump.
#define AP01_MENU_ONE_REPLAY "addi a1,s1,0x6be\n"
#define AP01_MENU_TWO_REPLAY "addi a1,s1,0x6be\n"
#define AP01_MENU_THREE_REPLAY "lui a1,0xa00fd\n"
#else
#define AP01_MENU_ONE_REPLAY "li a3,0\nli a2,1\n"
#define AP01_MENU_TWO_REPLAY "li a3,0\nli a2,11\n"
#define AP01_MENU_THREE_REPLAY "lui a1,0xa00f4\n"
#endif
asm(R"(
.pushsection .text.ap01MenuHooks0041,"ax",@progbits
.balign 2
.global ap01MenuRegisterOne0041
ap01MenuRegisterOne0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsRegister0041
lw ra,12(sp)
addi sp,sp,16
)" AP01_MENU_ONE_REPLAY R"(
ret
.global ap01MenuRegisterTwo0041
ap01MenuRegisterTwo0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsRegister0041
lw ra,12(sp)
addi sp,sp,16
)" AP01_MENU_TWO_REPLAY R"(
ret
.global ap01MenuRegisterThree0041
ap01MenuRegisterThree0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsRegister0041
lw ra,12(sp)
addi sp,sp,16
)" AP01_MENU_THREE_REPLAY R"(
ret
.global ap01MenuList0041
ap01MenuList0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsList0041
lw ra,12(sp)
addi sp,sp,16
li a1,0
sw a0,8(s3)
ret
.popsection
)");
