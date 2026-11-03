#include "app_download_0041.h"
#include <assert.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string>
#include <vector>
#include <fstream>
#include <iterator>
#include "test_app_file_store_0041.h"

int main(int argc,char **argv){
    assert(argc==3);std::ifstream input(argv[2],std::ios::binary);
    std::vector<uint8_t> package{std::istreambuf_iterator<char>(input),{}};assert(package.size()==320);
    uint8_t mac[6]={1,2,3,4,5,6};Ap01AppUpdateRecord request;
    memcpy(request.mac,mac,6);request.transaction[0]=1;request.total=package.size();
    memcpy(request.newDigest,package.data()+192,32);strcpy(request.principal,"menu-maintenance");
    Apx2Limits limits{4096,4096,1024,1024,2,UINT64_MAX,nullptr};
    using R=Ap01AppDownloadResult;using J=Ap01AppJournalResult;
    for(int cut=0;cut<=160;++cut){
        std::string root=std::string(argv[1])+"/case"+std::to_string(cut);assert(!mkdir(root.c_str(),0700));
        Disk disk;auto ops=disk.ops();LittleFSClass fs(ops,root.c_str());
        Ap01AppUpdateJournal0041 journal(fs,mac);assert(journal.load()==J::Empty);
        Ap01AppDownload0041 download(fs,journal,limits);assert(download.begin(request)==R::Ok);
        assert(download.chunk(request.transaction,1,package.data(),1)==R::Conflict);
        disk.cut=cut;
        auto result=download.chunk(request.transaction,0,package.data(),160);
        assert(result==(cut<160?R::Storage:R::Ok));disk.cut=-1;
        // Reconstruct both objects, as after a reset with a partial uncommitted tail.
        Ap01AppUpdateJournal0041 reboot(fs,mac);assert(reboot.load()==J::Ok);
        Ap01AppDownload0041 resumed(fs,reboot,limits);assert(resumed.begin(request)==R::Ok);
        assert(resumed.chunk(request.transaction,0,package.data(),160)==R::Ok);
        assert(reboot.current()->received==160);
        uint8_t wrong=package[0]^1;assert(resumed.chunk(request.transaction,0,&wrong,1)==R::Conflict);
        disk.loseJournalAck=true;
        assert(resumed.chunk(request.transaction,160,package.data()+160,160)==R::Unknown);
        assert(resumed.chunk(request.transaction,160,package.data()+160,160)==R::Unknown);
        disk.loseJournalAck=false;assert(reboot.load()==J::Ok&&reboot.current()->received==320);
        Apx2Error detail;assert(resumed.ready(request.transaction,detail)==R::Ok);
        assert(resumed.ready(request.transaction,detail)==R::Ok);
        assert(reboot.current()->phase==Ap01AppUpdatePhase::Ready);
        assert(resumed.chunk(request.transaction,0,package.data(),1)==R::State);
    }
    // File fully synced, journal save never wrote: retry must not append again.
    std::string root=std::string(argv[1])+"/journal-failure";assert(!mkdir(root.c_str(),0700));
    Disk disk;auto ops=disk.ops();LittleFSClass fs(ops,root.c_str());
    Ap01AppUpdateJournal0041 journal(fs,mac);assert(journal.load()==J::Empty);
    Ap01AppDownload0041 download(fs,journal,limits);assert(download.begin(request)==R::Ok);
    disk.failJournal=true;assert(download.chunk(request.transaction,0,package.data(),320)==R::Unknown);
    disk.failJournal=false;assert(journal.load()==J::Ok&&journal.current()->received==0);
    assert(download.chunk(request.transaction,0,package.data(),320)==R::Ok);
    File file=fs.open("/app-incoming.apx2","r");assert(file.size()==320);
    Apx2Error detail;assert(download.ready(request.transaction,detail)==R::Ok);
    for(unsigned scenario=0;scenario<3;++scenario){
        std::string folder=std::string(argv[1])+"/reject"+std::to_string(scenario);assert(!mkdir(folder.c_str(),0700));
        Disk faults;auto io=faults.ops();LittleFSClass store(io,folder.c_str());
        Ap01AppUpdateJournal0041 log(store,mac);assert(log.load()==J::Empty);
        Ap01AppDownload0041 transfer(store,log,limits);auto requested=request;
        if(scenario==1)requested.newDigest[0]^=1;
        assert(transfer.begin(requested)==R::Ok);
        uint8_t unknown[16]={9};assert(transfer.chunk(unknown,0,package.data(),1)==R::Conflict);
        assert(transfer.chunk(request.transaction,319,package.data(),2)==R::Bounds);
        assert(transfer.ready(request.transaction,detail)==R::Bounds);
        auto payload=package;
        if(scenario==2)payload[256]^=1;
        if(scenario==0){
            faults.failSync=true;
            assert(transfer.chunk(request.transaction,0,payload.data(),320)==R::Storage);
            assert(log.current()->received==0);faults.failSync=false;
        }
        assert(transfer.chunk(request.transaction,0,payload.data(),320)==R::Ok);
        assert(transfer.ready(request.transaction,detail)==(scenario?R::Package:R::Ok));
        if(scenario)assert(log.current()->phase==Ap01AppUpdatePhase::Receiving&&detail==Apx2Error::Integrity);
    }
    puts("download: 161 partial tails/reboots, duplicate/conflict, lost journal ACK, persisted-file/uncommitted-offset retry, sync failure, digest rejection, APX2 ready passed");
}
