#pragma once
#include "app_update_record_0041.h"
#include "apx2.h"

enum class Ap01AppDownloadResult {Ok,Conflict,Bounds,Storage,Unknown,Package,State};
// Single maintenance executor, exclusively owns journal and package files.
// Authentication, MAC/current-App checks and space reservation precede begin.
class Ap01AppDownload0041 {
    LittleFSClass &fs;
    Ap01AppUpdateJournal0041 &journal;
    Apx2Limits limits;
public:
    static constexpr uint32_t chunkMax=1024;
    Ap01AppDownload0041(LittleFSClass &f,Ap01AppUpdateJournal0041 &j,const Apx2Limits &l):fs(f),journal(j),limits(l){}
    Ap01AppDownloadResult begin(const Ap01AppUpdateRecord &);
    Ap01AppDownloadResult chunk(const uint8_t transaction[16],uint32_t offset,const uint8_t *,uint32_t);
    Ap01AppDownloadResult ready(const uint8_t transaction[16],Apx2Error &detail);
};
