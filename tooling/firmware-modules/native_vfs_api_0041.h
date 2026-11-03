#ifndef AP01_NATIVE_VFS_API_0041_H
#define AP01_NATIVE_VFS_API_0041_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Frozen C layout on RV32/ILP32F; size_t and int are 32 bits there.
 * Buffers/paths are borrowed until return. No STL or native File crosses ABI.
 * App tables are scoped by context: descriptors are opaque App-local handles.
 * In an App table, prepare only checks the platform-prepared private root;
 * it never mounts/formats or creates directories.
 * write succeeds only after sync (including length zero); rename commits
 * metadata. All operations may block on VFS and belong on a worker, not UI.
 * Return negative on error; close/mutations/prepare/statfs return 0 on success,
 * read/write return byte count; exists returns 0 absent, 1 present.
 */
typedef struct Ap01VfsOps {
    void *context;
    int (*prepare)(void *, const char *);
    int (*open)(void *, const char *, unsigned); /* 0 read, 1 truncate, 2 append */
    int (*close)(void *, int);
    int (*read)(void *, int, void *, size_t);
    int (*write)(void *, int, const void *, size_t);
    int32_t (*seek)(void *, int, int32_t, unsigned);
    int32_t (*size)(void *, int);
    int (*exists)(void *, const char *);
    int (*mkdir)(void *, const char *);
    int (*remove)(void *, const char *);
    int (*rename)(void *, const char *, const char *);
    int (*statfs)(void *, const char *, uint64_t *, uint64_t *);
} Ap01VfsOps;
#ifdef __cplusplus
}
#endif
#endif
