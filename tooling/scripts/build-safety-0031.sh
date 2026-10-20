#!/usr/bin/env bash
# Build the 0031 safety-return prototype module (no HTTP server).
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
repo=$(realpath "$script_dir/../..")
out="$repo/evidence/qemu/0031-20261017"
source_dir="$repo/tooling/firmware-modules"
tool="$repo/../cuktech-ap01-firmware-tools/tools/docker/toolchain/bin/riscv64-unknown-elf"
prefix=${1:-safety-linked-0031-v1}
[[ "$prefix" =~ ^[a-zA-Z0-9_-]+$ && -d "$out" ]]
for suffix in s o su manifest.s manifest.o elf bin map; do
    [[ ! -e "$out/$prefix.$suffix" ]] || { echo 'Choose a new output prefix' >&2; exit 2; }
done
"$tool-gcc" -B"$(dirname -- "$tool")/" -march=rv32imafc_zicsr -mabi=ilp32f \
    -Os -ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
    -fno-pic -mno-relax -msmall-data-limit=0 -nostdlib -nostartfiles \
    -Wall -Wextra -Werror -fstack-usage -S "$source_dir/ota_0031_safety.c" \
    -o "$out/$prefix.s"
"$tool-as" -march=rv32imafc_zicsr -mabi=ilp32f "$out/$prefix.s" -o "$out/$prefix.o"
cat > "$out/$prefix.manifest.s" <<'ASM'
.section .ota_manifest,"a"
.global ota_0031_manifest
ota_0031_manifest:
.zero 256
ASM
"$tool-as" -march=rv32imafc_zicsr -mabi=ilp32f \
    "$out/$prefix.manifest.s" -o "$out/$prefix.manifest.o"
"$tool-ld" -m elf32lriscv --gc-sections --no-relax -T "$source_dir/ota_0031.ld" \
    "$out/$prefix.o" "$out/$prefix.manifest.o" -Map="$out/$prefix.map" -o "$out/$prefix.elf"
"$tool-objcopy" -O binary "$out/$prefix.elf" "$out/$prefix.bin"
[[ -z $("$tool-nm" -u "$out/$prefix.elf") ]]
sha256sum "$out/$prefix.elf" "$out/$prefix.bin" "$source_dir/ota_0031_safety.c"
cat "$out/$prefix.su"
