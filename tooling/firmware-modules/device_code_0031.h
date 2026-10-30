#ifndef AP01_DEVICE_CODE_0031_H
#define AP01_DEVICE_CODE_0031_H
#include <stddef.h>
#include <stdint.h>
#if __STDC_HOSTED__
#include <string.h>
#else
void *memcpy(void *,const void *,size_t);
void *memset(void *,int,size_t);
int memcmp(const void *,const void *,size_t);
#endif

/* Same DVC1 record and generation/commit policy as 0041, separate namespace.
 * read: exact 16 bytes, 0/-2(missing)/-22(corrupt)/-5(IO).
 * write: complete, synced and closed before success. replace: same-filesystem
 * atomic rename. Only the UI thread writes; readers open the committed file. */
typedef struct {
    void *context;
    int (*read)(void *,const char *,unsigned char[16]);
    int (*write)(void *,const char *,const unsigned char[16]);
    int (*replace)(void *,const char *,const char *);
    int (*random)(void *,unsigned char[4]);
} ap01_code_io_0031;
int ap01_code_load_0031(const ap01_code_io_0031 *,char[9]);
int ap01_code_ensure_0031(const ap01_code_io_0031 *,char[9]);
int ap01_code_regenerate_0031(const ap01_code_io_0031 *,char[9]);
ap01_code_io_0031 ap01_code_native_0031(void);

/* Caller serializes gate access across all request tasks. Credential is read
 * for each request; unavailable state fails closed without generating a code. */
typedef struct { unsigned failures; uint64_t retry_at; } ap01_code_gate_0031;
enum ap01_code_auth_result { AP01_CODE_OK, AP01_CODE_DENIED, AP01_CODE_LIMITED, AP01_CODE_UNAVAILABLE };
int ap01_code_auth_0031(ap01_code_gate_0031 *,const char *actual,
                        const char *token,size_t length,uint64_t now);
#endif
