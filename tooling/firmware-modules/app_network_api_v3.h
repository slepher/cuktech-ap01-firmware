#ifndef AP01_APP_NETWORK_API_V3_H
#define AP01_APP_NETWORK_API_V3_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct Ap01PeerV3 {uint8_t ip[4];uint16_t port,reserved;} Ap01PeerV3;
/* App-local opaque handles; buffers are borrowed for the call. TCP calls
 * wait only until the absolute monotonic deadline; UDP is nonblocking.
 * accept checks readiness then makes one backend attempt; its backend must
 * provide a bounded accept. These calls belong on workers, never the UI thread.
 * wait returns event bits (read=1/write=4), 0 timeout, negative error.
 * send/receive return bytes (TCP receive 0 = EOF); all other calls return 0
 * on success except listen/accept, which return positive handles.
 * listen admits only ports assigned by the platform to this App.
 */
typedef struct Ap01NetworkOpsV3 {
    void *context;
    int32_t (*listen)(void *,uint16_t port,uint32_t udp);
    int32_t (*accept)(void *,int32_t);
    int32_t (*close)(void *,int32_t);
    int32_t (*wait)(void *,int32_t,uint32_t events,uint64_t deadline);
    int32_t (*receive)(void *,int32_t,uint8_t *,uint32_t,uint64_t deadline);
    int32_t (*send)(void *,int32_t,const uint8_t *,uint32_t,uint64_t deadline);
    int32_t (*receive_from)(void *,int32_t,uint8_t *,uint32_t,Ap01PeerV3 *);
    int32_t (*send_to)(void *,int32_t,const uint8_t *,uint32_t,const Ap01PeerV3 *);
} Ap01NetworkOpsV3;
#ifdef __cplusplus
}
#endif
#endif
