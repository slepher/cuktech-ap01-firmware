/* Exact 0031 Settings continuations, verified against the original image. */
.section .text.ap01_access_hooks,"ax",@progbits
.balign 2
.global ap01_access_register_hook_0031
ap01_access_register_hook_0031:
addi sp,sp,-16
sw ra,12(sp)
call ap01_access_register_0031
lw ra,12(sp)
addi sp,sp,16
lui a1,0xa00f4
ret
.global ap01_access_list_hook_0031
ap01_access_list_hook_0031:
addi sp,sp,-16
sw ra,12(sp)
call ap01_access_list_0031
lw ra,12(sp)
addi sp,sp,16
li a1,0
sw a0,8(s3)
ret
