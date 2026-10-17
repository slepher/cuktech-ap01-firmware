OUTPUT_ARCH(riscv)
ENTRY(ota_0031_main)
SECTIONS
{
  /* 0031 pet-GIF extent (file 0x1f80ac..0x2563d6); manifest then code. */
  . = 0xa01f8640;
  .ota_manifest : { KEEP(*(.ota_manifest)) }
  ASSERT(SIZEOF(.ota_manifest) == 256, "OTA manifest must be 256 bytes")
  . = 0xa01f8740;
  .text : { KEEP(*(.text.entry)) *(.text .text.*) }
  .rodata : { *(.rodata .rodata.* .srodata .srodata.*) }
  .forbidden : { *(.data .data.* .bss .bss.* .sdata .sdata.* .sbss .sbss.* COMMON) }
  ASSERT(SIZEOF(.forbidden) == 0, "OTA port must have no writable static state")
  /DISCARD/ : { *(.comment .note* .eh_frame*) }
}
PROVIDE(snprintf = 0xa002d6fc);
