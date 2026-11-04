#pragma once
#include "app_manifest_v3.h"
#include "native_vfs_api_0041.h"
#include <memory>

// Worker-owned staging, then immutable UI reads. No filesystem callback from UI.
// The caller reserves staging_bytes in addition to Manifest runtime budgets.
enum class Ap01SetFilesResultV3 {Empty,Ready,Io,Manifest,Identity,Budget,Memory,Package};
class Ap01AppSetFilesV3 {
    struct Buffer {std::unique_ptr<uint8_t[]> bytes;uint32_t size=0;};
    Ap01VfsOps io;
    uint8_t manifestBytes[AP01_MANIFEST_HEADER_V3+AP01_MANIFEST_APPS_V3*AP01_MANIFEST_ENTRY_V3+
                          AP01_MANIFEST_DEPS_V3*AP01_MANIFEST_DEP_V3]{};
    uint32_t manifestSize=0;
    Ap01ManifestV3 manifest{};
    Buffer buffers[AP01_MANIFEST_APPS_V3];
    bool readFile(const char *,uint8_t *,uint32_t,uint32_t &,bool);
    static bool readManifest(void *,uint32_t,uint8_t *,uint32_t);
    static bool readPackage(void *,uint32_t,uint8_t *,uint32_t);
    static bool open(void *,const Ap01ManifestEntryV3 &,Apx2Reader &,uint32_t &);
    static void close(void *,Apx2Reader &);
public:
    explicit Ap01AppSetFilesV3(const Ap01VfsOps &ops):io(ops){}
    // expected=nullptr is the fixed-file D2 bootstrap, not a trusted journal selection.
    Ap01SetFilesResultV3 stage(const char *,const uint8_t *expected,const Ap01ManifestLimitsV3 &,uint32_t stagingBytes);
    Apx2Reader reader(){return {this,manifestSize,readManifest};}
    const uint8_t *digest()const{return manifest.digest;}
    uint64_t version()const{return manifest.sequence;}
    Ap01ManifestPackagesV3 packages(){return {this,open,close};}
    void discard();
};
