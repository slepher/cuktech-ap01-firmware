#include "app_files_0041.h"
#include "test_app_file_store_0041.h"
#include <cstdio>
#include <initializer_list>
static Disk disk;static Ap01AppFiles0041 *service;
static bool freezeDuringWrite=false,closeFault=false;
static unsigned mutationCalls=0,closes=0;
static int open(void *,const char *p,unsigned mode){if(mode)++mutationCalls;return Disk::open(&disk,p,mode);}
static int write(void *,int fd,const void *p,size_t n){++mutationCalls;if(freezeDuringWrite)assert(!service->writes(1,false));return Disk::write(&disk,fd,p,n);}
static int close(void *,int fd){++closes;if(closeFault)return -1;return Disk::close(&disk,fd);}
static int remove(void *,const char *p){++mutationCalls;return Disk::remove(&disk,p);}
static int rename(void *,const char *a,const char *b){++mutationCalls;return Disk::rename(&disk,a,b);}
static int mkdir(void *,const char *p){++mutationCalls;return ::mkdir(p,0700);}
static ap01_app_file_request_v2 request(const char *path="",uint32_t handle=0,uint32_t arg=0){ap01_app_file_request_v2 r{};strcpy(r.path,path);r.handle=handle;r.argument=arg;return r;}
static int call(const ap01_app_services_v2 &table,unsigned op,const ap01_app_file_request_v2 &r,void *out=nullptr,uint32_t capacity=0,const void *data=nullptr){
    uint8_t input[sizeof(r)+1024];memcpy(input,&r,sizeof(r));
    unsigned n=op==AP01_FILE_WRITE?r.argument:0;assert(n<=1024);if(n)memcpy(input+sizeof(r),data,n);
    uint32_t written=99;int result=table.invoke(table.context,table.generation,2,op,input,sizeof(r)+n,out,capacity,&written);
    if(result)assert(!written);else if(op!=AP01_FILE_READ)assert(written==capacity);
    return result;
}
int main(int argc,char **argv){
    assert(argc==2);auto io=disk.ops();io.open=open;io.write=write;io.close=close;io.mkdir=mkdir;io.remove=remove;io.rename=rename;
    Ap01AppGeneration0041 gate;Ap01AppFiles0041 files(gate,io,argv[1]);service=&files;
    auto table=files.table(gate.begin());uint32_t handle=0,word=0;
    assert(call(table,AP01_FILE_OPEN,request("/test",0,1),&handle,4)==AP01_FILE_READ_ONLY&&!mutationCalls);
    assert(files.writes(1,true));assert(call(table,AP01_FILE_OPEN,request("/test",0,1),&handle,4)==0&&handle);
    freezeDuringWrite=true;assert(call(table,AP01_FILE_WRITE,request("",handle,3),&word,4,"abc")==0&&word==3);freezeDuringWrite=false;
    assert(files.writes(1,false));unsigned before=mutationCalls;
    assert(call(table,AP01_FILE_WRITE,request("",handle,1),&word,4,"z")==AP01_FILE_READ_ONLY);
    assert(call(table,AP01_FILE_REMOVE,request("/test"))==AP01_FILE_READ_ONLY);
    assert(call(table,AP01_FILE_MKDIR,request("/dir"))==AP01_FILE_READ_ONLY);
    auto renameRequest=request("/test");strcpy(renameRequest.destination,"/other");
    assert(call(table,AP01_FILE_RENAME,renameRequest)==AP01_FILE_READ_ONLY);
    assert(call(table,AP01_FILE_OPEN,request("/test",0,1),&word,4)==AP01_FILE_READ_ONLY&&mutationCalls==before);
    assert(call(table,AP01_FILE_CLOSE,request("",handle))==0);
    uint32_t reader=0;assert(call(table,AP01_FILE_OPEN,request("/test"),&reader,4)==0&&reader!=handle);
    char bytes[4]={};assert(call(table,AP01_FILE_READ,request("",reader),bytes,3)==0&&!memcmp(bytes,"abc",3));
    assert(call(table,AP01_FILE_SIZE,request("",handle),&word,4)==AP01_SERVICE_INVALID);
    assert(files.writes(1,true));
    for(const char *bad:{"/../escape","/dir/../escape","/./test","//test","/test/","/dir\\test"})
        assert(call(table,AP01_FILE_OPEN,request(bad,0,1),&word,4)==AP01_SERVICE_INVALID);
    before=mutationCalls;assert(call(table,AP01_FILE_WRITE,request("",reader,1),&word,4,"x")==AP01_FILE_READ_ONLY&&before==mutationCalls);
    auto malformed=request("/test");malformed.path[95]='x';
    assert(call(table,AP01_FILE_OPEN,malformed,&word,4)==AP01_SERVICE_INVALID);
    uint32_t written=99;auto plain=request("/test");
    assert(table.invoke(table.context,1,2,AP01_FILE_OPEN,&plain,sizeof(plain)-1,&word,4,&written)==AP01_SERVICE_INVALID&&!written);
    uint64_t oversized=0;before=mutationCalls;
    assert(call(table,AP01_FILE_OPEN,request("/test",0,1),&oversized,8)==AP01_SERVICE_INVALID&&mutationCalls==before);
    // Sixteen live handles, never reused within or across generations.
    for(unsigned i=1;i<16;++i)assert(call(table,AP01_FILE_OPEN,request("/test"),&word,4)==0);
    assert(call(table,AP01_FILE_OPEN,request("/test"),&word,4)==AP01_FILE_LIMIT);
    assert(!files.drain());assert(gate.acquire(1));gate.close();assert(!files.drain());gate.release();
    before=closes;assert(files.drain()&&closes==before+16);
    auto next=files.table(gate.begin());
    assert(call(table,AP01_FILE_OPEN,request("/test"),&word,4)==AP01_SERVICE_UNAVAILABLE);
    assert(call(next,AP01_FILE_SIZE,request("",reader),&word,4)==AP01_SERVICE_INVALID);
    assert(call(next,AP01_FILE_OPEN,request("/test",0,1),&word,4)==AP01_FILE_READ_ONLY);
    assert(call(next,AP01_FILE_OPEN,request("/test"),&word,4)==0&&word>reader);
    assert(files.writes(2,true));assert(call(next,AP01_FILE_RENAME,renameRequest)==0);
    assert(call(next,AP01_FILE_EXISTS,request("/other"),&word,4)==0&&word==1);
    assert(call(next,AP01_FILE_EXISTS,request("/test"),&word,4)==0&&word==0);
    uint64_t sizes[2]={};assert(call(next,AP01_FILE_CAPACITY,request(),sizes,16)==0&&sizes[0]>sizes[1]);
    assert(call(next,AP01_FILE_MKDIR,request("/dir"))==0);
    assert(call(next,AP01_FILE_REMOVE,request("/other"))==0);
    // Ambiguous close failure is not retried against a potentially reused fd.
    closeFault=true;gate.close();assert(!files.drain());before=closes;assert(!files.drain()&&closes==before);
    puts("file C service: frozen mutations, read access, in-flight freeze exclusion, path isolation, opaque handle budget/staleness, generation drain and sticky close failure passed");
}
