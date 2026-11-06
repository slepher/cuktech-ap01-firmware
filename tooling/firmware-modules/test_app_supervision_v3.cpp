#include "app_supervision_v3.h"
#include <cassert>
#include <cstdio>
#include <thread>
using State=Ap01SupervisorStateV3;using Fault=Ap01SupervisorFaultV3;
static void expect(const Ap01AppSupervisionV3 &s,State state,Fault fault=Fault::None){auto v=s.snapshot();assert(v.state==state&&v.fault==fault);}
int main(){
    int32_t good[8]={},pending[8]={},bad[8]={};pending[1]=AP01_APP_V3_PENDING;bad[7]=AP01_APP_V3_FAILED;
    {Ap01AppSupervisionV3 s;s.tick(100,-1,true,100,true);expect(s,State::Fault,Fault::Boot);
     s.publish(200,good,2);s.tick(200,1,true,200,true);expect(s,State::Fault,Fault::Boot);}
    {Ap01AppSupervisionV3 s;s.tick(UINT32_MAX-100,0,false,0,false);s.tick(29899,0,false,0,false);expect(s,State::Fault,Fault::StartupTimeout);}
    {Ap01AppSupervisionV3 s;s.publish(100,good,2);s.tick(100,1,true,100,true);expect(s,State::Healthy);
     s.tick(10101,1,true,100,true);expect(s,State::Fault,Fault::MaintenanceStale);}
    {Ap01AppSupervisionV3 s;s.publish(100,good,2);s.tick(100,1,true,100,true);
     s.tick(200,1,false,100,true);expect(s,State::Fault,Fault::MaintenanceStale);}
    {Ap01AppSupervisionV3 s;s.publish(100,good,2);s.tick(100,1,true,100,true);
     s.tick(5101,1,true,5101,true);expect(s,State::Fault,Fault::UiStale);}
    {Ap01AppSupervisionV3 s;s.publish(100,pending,2);s.tick(100,1,true,100,true);expect(s,State::Starting);
     s.publish(30100,pending,2);s.tick(30100,1,true,30100,true);expect(s,State::Fault,Fault::AppTimeout);assert(s.snapshot().app_index==1);}
    {Ap01AppSupervisionV3 s;s.publish(100,bad,8);s.tick(100,1,true,100,true);expect(s,State::Fault,Fault::AppFailed);assert(s.snapshot().app_index==7);}
    {Ap01AppSupervisionV3 s;s.publish(100,pending,2);s.tick(100,1,true,100,true);
     s.tick(60000,1,true,60000,false);expect(s,State::WindowAbsent);
     s.publish(60001,good,2);s.tick(60001,1,true,60001,true);expect(s,State::Healthy);
     s.fail(Fault::Worker);expect(s,State::Fault,Fault::Worker);}
    {Ap01AppSupervisionV3 s;s.publish(0,nullptr,0);s.tick(0,1,true,0,true);expect(s,State::Healthy);}
    {Ap01AppSupervisionV3 s;s.publish(101,good,2);s.tick(100,1,true,101,true);expect(s,State::Healthy);}
    {Ap01AppSupervisionV3 s;std::atomic<bool> done{false};
     std::thread writer([&]{for(unsigned n=1;n<=20000;++n){int32_t v[8];for(auto &x:v)x=n&1?AP01_APP_V3_FAILED:0;s.publish(n,v,8);}done.store(true);});
     do{auto v=s.snapshot();if(v.count){assert(v.count==8);for(auto x:v.health)assert(x==(v.sampled_at&1?AP01_APP_V3_FAILED:0));}}while(!done.load());writer.join();}
    // All published samples are fresh. Seqlock contention must not latch UiStale.
    {Ap01AppSupervisionV3 s;s.publish(100,good,8);s.tick(100,1,true,100,true);
     s.publish(10000,good,8);s.tick(10000,1,true,10000,true);
     std::atomic<bool> done{false};std::thread writer([&]{while(!done.load())s.publish(10000,good,8);});
     for(unsigned i=0;i<200000;++i)s.tick(10000,1,true,10000,true);
     done.store(true);writer.join();expect(s,State::Healthy);
     s.tick(15001,1,true,15001,true);expect(s,State::Fault,Fault::UiStale);}
    // Trial faults stay latched; approved UI stalls recover only from fresh, all-good samples.
    {Ap01AppSupervisionV3 s;s.publish(100,good,2);s.tick(100,1,true,100,true);
     s.tick(5101,1,true,5101,true);s.publish(5200,good,2);s.tick(5200,1,true,5200,true);
     expect(s,State::Fault,Fault::UiStale);}
    {Ap01AppSupervisionV3 s;s.publish(100,good,2);s.tick(100,1,true,100,true);s.allowUiRecovery();
     s.tick(5101,1,true,5101,true);expect(s,State::Fault,Fault::UiStale);
     s.publish(5200,pending,2);s.tick(5200,1,true,5200,true);expect(s,State::Fault,Fault::UiStale);
     s.publish(5300,good,2);s.tick(5300,1,true,5300,false);expect(s,State::Fault,Fault::UiStale);
     s.tick(5300,1,true,5300,true);expect(s,State::Healthy);
     s.tick(10301,1,true,10301,true);expect(s,State::Fault,Fault::UiStale);
     s.publish(10400,bad,8);s.tick(10400,1,true,10400,true);expect(s,State::Fault,Fault::AppFailed);
     s.publish(10500,good,8);s.tick(10500,1,true,10500,true);expect(s,State::Fault,Fault::AppFailed);}
    puts("supervision: boot/startup, maintenance loss/stall, UI stall, indexed App failure/timeout, window recreation, wraparound, empty set, latched faults and concurrent snapshots passed");
}
