#pragma once
#include "app_core_0041.h"
#include "app_files_0041.h"
#include "app_network_0041.h"
#include "app_heap_0041.h"
// Resident routing only. Services share the executor's generation gate and
// outlive every App/table snapshot. No App function pointer is stored here.
class Ap01AppServices0041 {
    Ap01AppCore0041 &core;
    Ap01AppFiles0041 &files;
    Ap01AppNetwork0041 *network;
    Ap01AppHeap0041 *heap;
    static int32_t invoke(void *context,uint32_t generation,uint32_t service,uint32_t operation,
                          const void *input,uint32_t length,void *output,uint32_t capacity,uint32_t *written){
        if(!written)return AP01_SERVICE_INVALID;
        *written=0;if(!context)return AP01_SERVICE_INVALID;
        auto &self=*(Ap01AppServices0041 *)context;
        ap01_app_services_v2 target{};
        switch(service){
        case AP01_APP_SERVICE_CORE:target=self.core.table(generation);break;
        case AP01_APP_SERVICE_FILE:target=self.files.table(generation);break;
        case AP01_APP_SERVICE_NETWORK:
            if(!self.network)return AP01_SERVICE_UNAVAILABLE;
            target=self.network->table(generation);break;
        case AP01_APP_SERVICE_HEAP:
            if(!self.heap)return AP01_SERVICE_UNAVAILABLE;
            target=self.heap->table(generation);break;
        default:return AP01_SERVICE_UNAVAILABLE;
        }
        return target.invoke(target.context,generation,service,operation,input,length,output,capacity,written);
    }
public:
    Ap01AppServices0041(Ap01AppCore0041 &c,Ap01AppFiles0041 &f,Ap01AppNetwork0041 *n=nullptr,Ap01AppHeap0041 *h=nullptr):core(c),files(f),network(n),heap(h){}
    ap01_app_services_v2 table(uint32_t generation){
        return {AP01_APP_ABI_V2,sizeof(ap01_app_services_v2),generation,0,
                AP01_APP_CORE_CAPABILITY|AP01_APP_FILE_CAPABILITY|(network?AP01_APP_NETWORK_CAPABILITY:0)|(heap?AP01_APP_HEAP_CAPABILITY:0),this,invoke};
    }
};
