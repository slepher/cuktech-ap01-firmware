// Four exact-stock call-site continuations; no writable state.
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
li a3,0
li a2,1
ret
.global ap01MenuRegisterTwo0041
ap01MenuRegisterTwo0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsRegister0041
lw ra,12(sp)
addi sp,sp,16
li a3,0
li a2,11
ret
.global ap01MenuRegisterThree0041
ap01MenuRegisterThree0041:
addi sp,sp,-16
sw ra,12(sp)
call ap01SettingsRegister0041
lw ra,12(sp)
addi sp,sp,16
lui a1,0xa00f4
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
