#ifndef AP01_APP_FILE_ABI_V2_H
#define AP01_APP_FILE_ABI_V2_H
#include "app_core_abi_v2.h"
#define AP01_APP_SERVICE_FILE 2u
#define AP01_APP_FILE_CAPABILITY UINT64_C(2)
#define AP01_APP_FILE_CHUNK 1024u
enum {AP01_FILE_OPEN=1,AP01_FILE_CLOSE,AP01_FILE_READ,AP01_FILE_WRITE,AP01_FILE_SEEK,
      AP01_FILE_SIZE,AP01_FILE_EXISTS,AP01_FILE_MKDIR,AP01_FILE_REMOVE,AP01_FILE_RENAME,AP01_FILE_CAPACITY};
enum {AP01_FILE_BUSY=-4,AP01_FILE_READ_ONLY=-5,AP01_FILE_LIMIT=-6};
// Borrowed fixed-width request, native little endian. OPEN argument: 0 read,
// 1 truncate, 2 append. WRITE argument bytes follow this header (max 1024).
// READ uses output capacity (max 1024). Paths are NUL-padded, relative to the
// firmware-owned business root; absolute '/name' syntax, no '.', '..' or '//'.
// OPEN/WRITE/SEEK/SIZE/EXISTS output uint32; CAPACITY outputs uint64 total,used.
// CLOSE/MKDIR/REMOVE/RENAME have no output. Native descriptors never cross ABI.
typedef struct ap01_app_file_request_v2 {
    uint32_t handle,argument;
    int32_t offset;
    uint32_t origin;
    char path[96],destination[96];
} ap01_app_file_request_v2;
#endif
