#!/usr/bin/env bash
# Reproducible freestanding RV32 0031 OTA module; no device access or new directories.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)
repo=$(realpath "$script_dir/../..")
out=${2:-"$repo/evidence/private/ota-expansion-20261018"}
source_dir="$repo/tooling/firmware-modules"
tool="$repo/../cuktech-ap01-firmware-tools/tools/docker/toolchain/bin/riscv64-unknown-elf"
prefix=${1:-ota-channel-linked-0031-v1}
base=${3:-0xa01f8640}
version=${4:-ap01-ota/2}
mode=${5:-release}
[[ "$mode" == release || "$mode" == probe || "$mode" == full-upload ]]
extra_flags=()
units=(channel port image diagnostic_console diagnostic_console_0031)
if [[ "$mode" != release ]]; then extra_flags+=(-DOTA_PORT_NO_ENTRY -DAP01_HTTP_PROBE); units+=(probe_network_console_0031); fi
if [[ "$mode" == full-upload ]]; then extra_flags+=(-DAP01_HTTP_FULL_UPLOAD); fi
[[ "$prefix" =~ ^[a-zA-Z0-9_-]+$ && -d "$out" ]]
for suffix in channel.s channel.o channel.su port.s port.o port.su image.s image.o image.su manifest.s manifest.o elf bin map; do
    [[ ! -e "$out/$prefix.$suffix" ]] || { echo 'Choose a new output prefix' >&2; exit 2; }
done
for unit in "${units[@]}"; do
    case "$unit" in channel) source_file=ota_channel.c;; port) source_file=ota_0031.c;; image) source_file=ota_image.c;; *) source_file=$unit.c;; esac
    "$tool-gcc" -B"$(dirname -- "$tool")/" -march=rv32imafc_zicsr -mabi=ilp32f \
        -Os -ffreestanding -fno-builtin -ffunction-sections -fdata-sections \
        -fno-pic -mno-relax -msmall-data-limit=0 -nostdlib -nostartfiles \
        -Wall -Wextra -Werror -fstack-usage -S "$source_dir/$source_file" \
        -DOTA_CHANNEL_VERSION="\"$version\"" "${extra_flags[@]}" \
        -o "$out/$prefix.$unit.s"
    "$tool-as" -march=rv32imafc_zicsr -mabi=ilp32f \
        "$out/$prefix.$unit.s" -o "$out/$prefix.$unit.o"
done
cat > "$out/$prefix.manifest.s" <<'ASM'
.section .ota_manifest,"a"
.global ota_0031_manifest
ota_0031_manifest:
.zero 256
ASM
cat >> "$out/$prefix.manifest.s" <<ASM
.section .rodata.ota_reference,"a"
.global ota_0031_reference_header
ota_0031_reference_header:
.incbin "$repo/roms/0031/ap01-1.0.2_0031.bin",0,256
ASM
"$tool-as" -march=rv32imafc_zicsr -mabi=ilp32f \
    "$out/$prefix.manifest.s" -o "$out/$prefix.manifest.o"
probe_objects=()
if [[ "$mode" != release ]]; then probe_objects+=("$out/$prefix.probe_network_console_0031.o"); fi
"$tool-ld" -m elf32lriscv --gc-sections --no-relax --defsym="ota_base=$base" -T "$source_dir/ota_0031.ld" \
    "$out/$prefix.channel.o" "$out/$prefix.port.o" "$out/$prefix.image.o" "$out/$prefix.diagnostic_console.o" "$out/$prefix.diagnostic_console_0031.o" "$out/$prefix.manifest.o" "${probe_objects[@]}" \
    -Map="$out/$prefix.map" -o "$out/$prefix.elf"
"$tool-objcopy" -O binary "$out/$prefix.elf" "$out/$prefix.bin"
[[ -z $("$tool-nm" -u "$out/$prefix.elf") ]]
sha256sum "$out/$prefix.elf" "$out/$prefix.bin" \
    "$source_dir/ota_channel.c" "$source_dir/ota_0031.c"
cat "$out/$prefix.channel.su" "$out/$prefix.port.su"
