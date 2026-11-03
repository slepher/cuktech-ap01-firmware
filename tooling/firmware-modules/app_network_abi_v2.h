#ifndef AP01_APP_NETWORK_ABI_V2_H
#define AP01_APP_NETWORK_ABI_V2_H
#include "app_core_abi_v2.h"
#define AP01_APP_SERVICE_NETWORK 3u
#define AP01_APP_NETWORK_CAPABILITY UINT64_C(4)
#define AP01_APP_NETWORK_CHUNK 1024u
enum {AP01_NET_LISTEN=1,AP01_NET_ACCEPT,AP01_NET_CLOSE,AP01_NET_POLL,
      AP01_NET_RECEIVE,AP01_NET_SEND,AP01_NET_RECEIVE_FROM,AP01_NET_SEND_TO};
enum {AP01_NET_BUSY=-4,AP01_NET_LIMIT=-6,AP01_NET_AGAIN=-7};
// IPv4 octets in network order; port in host order. No native sockaddr layout.
typedef struct ap01_app_peer_v2 {uint8_t ip[4];uint16_t port,reserved;} ap01_app_peer_v2;
// Exact 16-byte header. LISTEN: argument 0 TCP/1 UDP, peer.port;
// POLL: argument 1 readable/4 writable/5 both, immediate snapshot, no wait.
// SEND/SEND_TO: argument payload bytes following header, <=1024.
// Other operations: argument zero. Only LISTEN/SEND_TO use peer.
// LISTEN/ACCEPT/POLL/SEND/SEND_TO output a uint32; CLOSE has no output.
// RECEIVE returns bytes, RECEIVE_FROM returns peer header followed by bytes.
// AGAIN distinguishes not-ready from TCP EOF (successful zero-byte RECEIVE).
typedef struct ap01_app_network_request_v2 {
    uint32_t handle,argument;
    ap01_app_peer_v2 peer;
} ap01_app_network_request_v2;
#endif
