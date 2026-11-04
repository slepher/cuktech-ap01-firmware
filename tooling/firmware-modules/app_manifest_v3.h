#pragma once
#include "apx2.h"
// Format bound only; actual count/resources are admitted by platform limits.
enum : uint32_t {AP01_MANIFEST_HEADER_V3=64,AP01_MANIFEST_ENTRY_V3=160,
    AP01_MANIFEST_DEP_V3=40,AP01_MANIFEST_APPS_V3=8,AP01_MANIFEST_DEPS_V3=56};
struct Ap01ManifestEntryV3 {
    char id[32],version[32];uint8_t digest[32];
    uint32_t package_bytes,image_bytes,heap_bytes,stack_bytes;
    uint32_t data_min,data_max,data_write;
    uint64_t capabilities;
    uint16_t tcp,udp,order,tasks,pages;
};
struct Ap01ManifestV3 {
    uint64_t sequence=0;uint32_t count=0;uint8_t digest[32]={};
    Ap01ManifestEntryV3 entries[AP01_MANIFEST_APPS_V3]{};
    uint8_t order[AP01_MANIFEST_APPS_V3]{};
};
struct Ap01ManifestLimitsV3 {
    uint32_t apps;uint64_t package_bytes,image_bytes,heap_bytes,stack_bytes;
    uint32_t tasks,pages;uint64_t capabilities;
    // Total usable RAM and resident maintenance reserve are explicit, not guessed.
    uint64_t ram_bytes,resident_bytes;
};
enum class Ap01ManifestErrorV3 {Ok,Read,Header,Identity,Integrity,Order,Resource,Dependency,Package};
// Reader immutable throughout. Output is usable only on Ok. No allocation/start.
Ap01ManifestErrorV3 ap01ReadManifestV3(const Apx2Reader &,const Ap01ManifestLimitsV3 &,Ap01ManifestV3 &);
// Validate every APX2 before any executable reservation/start. Open callback returns
// an immutable reader for the requested digest; close always follows a successful open.
struct Ap01ManifestPackagesV3 {
    void *context;
    bool (*open)(void *,const Ap01ManifestEntryV3 &,Apx2Reader &,uint32_t &dataVersion);
    void (*close)(void *,Apx2Reader &);
};
Ap01ManifestErrorV3 ap01CheckManifestPackagesV3(const Ap01ManifestV3 &,const Ap01ManifestPackagesV3 &);

Ap01ManifestErrorV3 ap01CheckManifestPackageV3(const Ap01ManifestEntryV3 &,const Apx2Reader &,uint32_t dataVersion);
