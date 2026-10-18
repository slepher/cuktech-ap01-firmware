#ifndef AP01_DIAGNOSTIC_CONSOLE_H
#define AP01_DIAGNOSTIC_CONSOLE_H
#include <stddef.h>
#include <stdint.h>
typedef struct {
    void *ctx;
    int (*read)(void *,void *,size_t,uint32_t);
    int (*write)(void *,const void *,size_t,uint32_t);
    uint64_t (*now_ms)(void *);
} diagnostic_console_io;
/* Authenticate one raw TCP console session; never echo a supplied key.
 * On success the caller hands this connection to an isolated native shell.
 * This function executes no commands and accesses no firmware storage. */
int diagnostic_console_authenticate(const diagnostic_console_io *,const char *,uint64_t deadline);
enum diagnostic_operation {DIAGNOSTIC_INVALID,DIAGNOSTIC_SHELL,DIAGNOSTIC_STATUS,
                           DIAGNOSTIC_INTERRUPT,DIAGNOSTIC_CLOSE,DIAGNOSTIC_LOGS,DIAGNOSTIC_FLASH};
enum diagnostic_operation diagnostic_console_operation(const diagnostic_console_io *,uint64_t deadline);
/* Physical read only: 1..64 KiB inside the board's 16 MiB NOR. */
int diagnostic_console_flash_range(const diagnostic_console_io *,uint64_t,uint32_t *,uint32_t *);
typedef struct {int shell_pid,parent_pid;} diagnostic_console_state;
int diagnostic_console_0031_handle(int fd,diagnostic_console_state *,const char *(*logs)(void *),void *);
int diagnostic_console_0031_own_child(int pid,int parent_pid);
int ota_0031_start(void);
#endif
