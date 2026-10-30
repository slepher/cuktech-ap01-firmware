#!/usr/bin/env bash
set -euo pipefail
repo=$(realpath "$(dirname "$0")/../..")
src="$repo/tooling/firmware-modules"
out=${2:?existing output directory required}
prefix=${1:?new build prefix required}
tool="$repo/../cuktech-ap01-firmware-tools/tools/docker/toolchain/bin/riscv64-unknown-elf"
[[ "$prefix" =~ ^[a-zA-Z0-9_-]+$ && -d "$out" && ! -e "$out/$prefix.elf" ]]
flags=(-march=rv32imafc_zicsr_zifencei -mabi=ilp32f -Os -ffreestanding -fno-builtin
    -ffunction-sections -fdata-sections -fpie -fvisibility=hidden -mcmodel=medany
    -mno-relax -msmall-data-limit=0 -nostdlib -nostartfiles -Wall -Wextra -Werror -fstack-usage)
mode=${3:-release}
[[ "$mode" == release || "$mode" == probe || "$mode" == full-upload ]]
units=(ota_channel ota_0031 ota_image diagnostic_console diagnostic_console_0031 device_code_0031 device_code_native_0031)
if [[ "$mode" != release ]]; then
    flags+=(-DOTA_PORT_NO_ENTRY -DAP01_HTTP_PROBE)
    units+=(probe_network_console_0031)
fi
if [[ "$mode" == full-upload ]]; then flags+=(-DAP01_HTTP_FULL_UPLOAD); fi
objects=()
for unit in "${units[@]}"; do
    "$tool-gcc" -B"$(dirname "$tool")/" "${flags[@]}" -DAP01_RAM_MODULE -DOTA_CHANNEL_VERSION='"ap01-diag/ram1"' \
        -S "$src/$unit.c" -o "$out/$prefix.$unit.s"
    "$tool-as" -march=rv32imafc_zicsr_zifencei -mabi=ilp32f "$out/$prefix.$unit.s" -o "$out/$prefix.$unit.o"
    objects+=("$out/$prefix.$unit.o")
done
cat > "$out/$prefix.manifest.s" <<ASM
.section .ota_manifest,"a"
.global ota_0031_manifest
.hidden ota_0031_manifest
ota_0031_manifest:
.zero 256
.section .rodata.ota_reference,"a"
.global ota_0031_reference_header
.hidden ota_0031_reference_header
ota_0031_reference_header:
.incbin "$repo/roms/0031/ap01-1.0.2_0031.bin",0,256
.section .text.snprintf,"ax"
.global snprintf
.hidden snprintf
snprintf:
li t0,0xa002d6fc
jr t0
ASM
"$tool-as" -march=rv32imafc_zicsr_zifencei -mabi=ilp32f "$out/$prefix.manifest.s" -o "$out/$prefix.manifest.o"
# Local trampoline overrides the absolute PROVIDE; all module references must
# remain PC-relative. Retained relocations are audited by the package builder.
"$tool-ld" -m elf32lriscv --gc-sections --no-relax --emit-relocs --defsym=ota_base=0 \
    -T "$src/ota_0031.ld" "${objects[@]}" "$out/$prefix.manifest.o" -Map="$out/$prefix.map" -o "$out/$prefix.elf"
"$tool-objcopy" -O binary "$out/$prefix.elf" "$out/$prefix.bin"
"$tool-gcc" -B"$(dirname "$tool")/" "${flags[@]}" -S "$src/diagnostic_loader_0031.c" -o "$out/$prefix.loader.s"
"$tool-as" -march=rv32imafc_zicsr_zifencei -mabi=ilp32f "$out/$prefix.loader.s" -o "$out/$prefix.loader.o"
cat > "$out/$prefix.loader.ld" <<'LD'
OUTPUT_ARCH(riscv)
ENTRY(diagnostic_loader_0031)
SECTIONS {
 . = 0xa0000060;
 .text : { KEEP(*(.text.entry)) *(.text*) *(.rodata*) }
 ASSERT(. <= 0xa0000400, "loader exceeds original startup padding")
 .forbidden : { *(.data*) *(.bss*) *(.sdata*) *(.sbss*) *(.got*) }
 ASSERT(SIZEOF(.forbidden)==0,"loader writable state")
 /DISCARD/ : { *(.comment .eh_frame* .note*) }
}
LD
"$tool-ld" -m elf32lriscv --gc-sections --no-relax -T "$out/$prefix.loader.ld" "$out/$prefix.loader.o" -o "$out/$prefix.loader.elf"
"$tool-objcopy" -O binary "$out/$prefix.loader.elf" "$out/$prefix.loader.bin"
"$tool-readelf" -r "$out/$prefix.elf" > "$out/$prefix.relocations.txt"
[[ -z $("$tool-nm" -u "$out/$prefix.elf") ]]
wc -c "$out/$prefix.bin" "$out/$prefix.loader.bin"
