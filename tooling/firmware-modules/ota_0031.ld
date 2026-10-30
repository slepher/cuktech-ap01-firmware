OUTPUT_ARCH(riscv)
ENTRY(ota_0031_main)
SECTIONS
{
  /* Default is the legacy compatibility location; expanded builds override. */
  . = DEFINED(ota_base) ? ota_base : 0xa01f8640;
  .ota_manifest : { KEEP(*(.ota_manifest)) }
  ASSERT(SIZEOF(.ota_manifest) == 256, "OTA manifest must be 256 bytes")
  .text : { KEEP(*(.text.entry)) KEEP(*(.text.ap01_access_hooks)) *(.text .text.*) }
  .rodata : { *(.rodata .rodata.* .srodata .srodata.*) }
  .forbidden : { *(.data .data.* .bss .bss.* .sdata .sdata.* .sbss .sbss.* .got .got.* COMMON) }
  ASSERT(SIZEOF(.forbidden) == 0, "OTA port must have no writable static state")
  /DISCARD/ : { *(.comment .note* .eh_frame*) }
}
PROVIDE(snprintf = 0xa002d6fc);
