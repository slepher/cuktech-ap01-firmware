#include "app_network_0041.h"
#include "app_services_0041.h"
#include "app_network_client_v2.h"
#include <cassert>
#include <cstdio>
#include <cstring>
struct Transport {
    unsigned opened=0,closed=0;bool ready=true,again=false,eof=false,closeFail=false;
    Ap01AppGeneration0041 *gate=nullptr;Ap01AppNetwork0041 *network=nullptr;bool interrupt=false;
    uint64_t now=0;unsigned yields=0;bool closeOnYield=false,stuck=false,backwards=false;
    static bool clock(void *p,uint64_t *out){*out=((Transport *)p)->now;return true;}
    static bool yield(void *p){auto &t=*(Transport *)p;++t.yields;
        if(t.closeOnYield)t.gate->close();if(t.backwards)--t.now;else if(!t.stuck)++t.now;return true;}
    static int listen(void *p,uint16_t,bool){return int(++((Transport *)p)->opened);}
    static int accept(void *p,int){return int(++((Transport *)p)->opened);}
    static int close(void *p,int){auto &t=*(Transport *)p;++t.closed;return t.closeFail?-1:0;}
    static int poll(void *p,int,unsigned events){return ((Transport *)p)->ready?int(events):0;}
    static int receive(void *p,int,uint8_t *out,uint32_t n,ap01_app_peer_v2 *peer){auto &t=*(Transport *)p;
        if(t.interrupt){t.gate->close();assert(!t.network->drain());}
        if(t.again)return AP01_NET_AGAIN;
        if(t.eof)return 0;
        assert(n>=3);memcpy(out,"abc",3);if(peer)*peer={{192,168,1,2},8767,0};return 3;
    }
    static int send(void *p,int,const uint8_t *bytes,uint32_t n,const ap01_app_peer_v2 *){
        assert(n>=3&&!memcmp(bytes,"abc",3));return ((Transport *)p)->again?AP01_NET_AGAIN:int(n);
    }
    Ap01AppNetworkPort0041 port(){return {this,listen,accept,close,poll,receive,send};}
};
int main(){
    Ap01AppGeneration0041 gate;Transport t;Ap01AppNetwork0041 net(gate,t.port());t.gate=&gate;t.network=&net;
    auto table=net.table(gate.begin());uint8_t out[1032]{};uint32_t written=0;
    auto call=[&](unsigned op,ap01_app_network_request_v2 r,unsigned cap,const char *payload=nullptr){
        uint8_t input[1040]{};memcpy(input,&r,sizeof(r));unsigned n=sizeof(r);
        if(payload){memcpy(input+n,payload,r.argument);n+=r.argument;}
        written=99;return table.invoke(table.context,table.generation,3,op,input,n,out,cap,&written);
    };
    auto word=[&](){uint32_t v=0;assert(written==4);memcpy(&v,out,4);return v;};
    ap01_app_network_request_v2 r{};r.peer.port=80;
    assert(call(AP01_NET_LISTEN,r,4)==AP01_SERVICE_INVALID&&!t.opened);
    r.peer.port=18081;assert(!call(AP01_NET_LISTEN,r,4));uint32_t listener=word();
    r={};r.handle=listener;t.ready=false;assert(call(AP01_NET_ACCEPT,r,4)==AP01_NET_AGAIN&&!written);
    t.ready=true;assert(!call(AP01_NET_ACCEPT,r,4));uint32_t client=word();
    r.handle=client;r.argument=5;assert(!call(AP01_NET_POLL,r,4)&&word()==5);
    r.argument=0;assert(!call(AP01_NET_RECEIVE,r,16)&&written==3&&!memcmp(out,"abc",3));
    t.again=true;assert(call(AP01_NET_RECEIVE,r,16)==AP01_NET_AGAIN&&!written);t.again=false;
    t.eof=true;assert(!call(AP01_NET_RECEIVE,r,16)&&!written);t.eof=false;
    r.argument=3;assert(!call(AP01_NET_SEND,r,4,"abc")&&word()==3);
    r.argument=0;assert(call(AP01_NET_RECEIVE_FROM,r,16)==AP01_SERVICE_INVALID);
    r={};r.argument=1;r.peer.port=8767;assert(!call(AP01_NET_LISTEN,r,4));uint32_t udp=word();
    r={};r.handle=udp;assert(!call(AP01_NET_RECEIVE_FROM,r,16)&&written==11);
    memcpy(&r.peer,out,8);r.argument=3;assert(!call(AP01_NET_SEND_TO,r,4,"abc")&&word()==3);
    r.peer.reserved=1;assert(call(AP01_NET_SEND_TO,r,4,"abc")==AP01_SERVICE_INVALID);
    for(unsigned i=3;i<8;++i){r={};r.handle=listener;assert(!call(AP01_NET_ACCEPT,r,4));}
    assert(call(AP01_NET_ACCEPT,r,4)==AP01_NET_LIMIT&&t.opened==8);
    r={};r.handle=client;t.interrupt=true;
    assert(!call(AP01_NET_RECEIVE,r,16));assert(!t.closed);
    assert(call(AP01_NET_RECEIVE,r,16)==AP01_SERVICE_UNAVAILABLE);
    assert(net.drain()&&t.closed==8);assert(gate.begin()==2);
    assert(call(AP01_NET_RECEIVE,r,16)==AP01_SERVICE_UNAVAILABLE);
    table=net.table(2);assert(call(AP01_NET_CLOSE,r,0)==AP01_SERVICE_INVALID);
    r={};r.peer.port=18081;assert(!call(AP01_NET_LISTEN,r,4));uint32_t fresh=word();assert(fresh>8);
    r={};r.handle=fresh;t.closeFail=true;assert(call(AP01_NET_CLOSE,r,0)==AP01_SERVICE_IO);
    gate.close();assert(!net.drain()&&t.closed==9);assert(!net.drain()&&t.closed==9);
    {
        Ap01AppGeneration0041 g;Transport transport;transport.gate=&g;
        Ap01AppCore0041 core(g,{&transport,Transport::clock,nullptr,nullptr,Transport::yield});
        Ap01AppFiles0041 files(g,{},"/unused");Ap01AppNetwork0041 network(g,transport.port());
        Ap01AppServices0041 bus(core,files,&network);auto s=bus.table(g.begin());
        Ap01AppNetworkClientV2 client(s);int listener=client.listen(18081);assert(listener>0);
        transport.ready=false;assert(!client.wait(listener,1,5)&&transport.now==5&&transport.yields==5);
        transport.ready=true;assert(client.wait(listener,1,10));int tcp=client.accept(listener);assert(tcp>0);
        uint8_t bytes[2048]{};memcpy(bytes,"abc",3);
        assert(client.receive(tcp,bytes,sizeof(bytes),10)==3);assert(client.send(tcp,bytes,sizeof(bytes),10)==1024);
        transport.eof=true;assert(client.receive(tcp,bytes,16,10)==0);transport.eof=false;
        transport.again=true;assert(client.receive(tcp,bytes,16,8)==-1&&transport.now==8);transport.again=false;
        int udp=client.listen(8767,true);ap01_app_peer_v2 peer{};
        assert(client.receiveFrom(udp,bytes,16,peer)==3&&peer.port==8767);
        assert(client.sendTo(udp,bytes,3,peer)==3&&client.sendTo(udp,bytes,sizeof(bytes),peer)==-1);
        assert(client.close(tcp));
        transport.ready=false;transport.stuck=true;unsigned count=transport.yields;
        assert(!client.wait(listener,1,11)&&transport.yields-count==3);transport.stuck=false;
        transport.backwards=true;assert(!client.wait(listener,1,11));transport.backwards=false;
        transport.closeOnYield=true;assert(!client.wait(listener,1,11)&&g.drained());
        assert(network.drain()&&transport.opened==transport.closed);
        assert(client.listen(18081)<0&&!client.close(listener));
    }
    puts("network service/client: TCP/UDP, retry/EOF, original deadlines, bounded clock-stall retries, rollback clock/closed gate exit, chunk limits, handle budgets and drain passed");
}
