typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef short int16_t;
typedef unsigned int uint32_t;
#define CT_ABI          2
#define CT_MAX_OPS      64
#define CT_MAX_REQS     32
#define CT_MAX_RES      16
#define CT_BIND_MAX     64
#define CT_TEXT_MAX     48
#define CT_STR_MAX      12
#define CT_B64_MAX      64
#define CT_NONE_IDX     0xFF
#define BS_MAX_TEMPLATES 8
#define BS_MAX_BUNDLE_BYTES 262144
#define BS_CTX_LEN 33
#define BS_ID_LEN 17
#define BS_JOB_LEN 17
typedef struct CtReq CtReq;
typedef struct CtOp CtOp;
typedef struct CtResource CtResource;
typedef struct CtTemplate CtTemplate;
typedef struct SlotHeader SlotHeader;
typedef struct MetaRecord MetaRecord;
#pragma pack(push, 1)
struct CtReq {
    uint8_t kind;          // BindKind from template_engine.cpp
    uint8_t winMode;       // 0 weekly, 1 5h, 2 index, 3 monthly
    int16_t winIndex;
    char    bucket[16];
    char    path[CT_BIND_MAX];
};
struct CtOp {
    uint8_t  type;
    uint8_t  flags;        // bit0 fill, bit1 region, bit2 align, bit3 timefmt, bit4 digit_x
    uint8_t  font;         // index into CT_FONTS (f8,f12,f16,f20,f24,nt16,nt30)
    uint8_t  scale;
    int16_t  x, y, w, h;   // primary rect / text origin
    int16_t  x2, y2;       // line end; for digit_x: two/three-digit origins
    int16_t  whenEqNum;    // numeric `equals`
    int16_t  maxVal;       // bar max (default 100)
    uint8_t  bindIdx;      // CT_NONE_IDX or requirement index
    uint8_t  whenIdx;      // CT_NONE_IDX or requirement index
    uint8_t  whenMode;     // CtWhenMode
    uint8_t  align;        // 0 left, 1 center, 2 right
    uint8_t  timeFormat;   // 0 date, 1 hhmm
    uint8_t  resourceIdx;  // icon resource; for digit_x text: numeric bind index
    uint8_t  color;        // 0 black, 1 white
    uint8_t  bg;           // 0xFF none, else 0/1
    uint8_t  fg;           // bar fg
    uint8_t  border;       // 1 when the bar draws a border
    char     text[CT_TEXT_MAX];
    char     prefix[CT_STR_MAX];
    char     suffix[CT_STR_MAX];
    char     whenEqStr[16];
};
struct CtResource {
    uint8_t w, h;
    char    bits[CT_B64_MAX];
};
struct CtTemplate {
    uint8_t  abi;
    uint8_t  opCount;
    uint8_t  reqCount;
    uint8_t  resCount;
    uint32_t sourceCrc;
    char     id[17];
    CtOp       ops[CT_MAX_OPS];
    CtReq      reqs[CT_MAX_REQS];
    CtResource res[CT_MAX_RES];
};
struct SlotHeader {
    uint32_t magic;
    uint16_t count;
    uint8_t initial;
    uint8_t flags;
    char jobId[BS_JOB_LEN];
    char contextId[BS_CTX_LEN];
    char firmwareTarget[32];
    char renderTarget[32];
    uint32_t payloadCrc;   // CRC of the bundle payload that produced this slot
    uint32_t reserved;
};
struct MetaRecord {
    uint32_t magic;
    uint32_t seq;
    uint8_t slot;
    uint8_t prevSlot;
    uint8_t configured;
    uint8_t reserved;
    uint32_t fileLen;
    uint32_t fileCrc;
    char jobId[BS_JOB_LEN];
    char contextId[BS_CTX_LEN];
    char firmwareTarget[32];
    char renderTarget[32];
    uint32_t recordCrc;
};
#pragma pack(pop)
_Static_assert(sizeof(void*) == 4 && sizeof(uint32_t) == 4, "RV32 required");
__attribute__((section(".budget"),used)) const uint32_t sizes[] = {0x42554447,sizeof(CtReq),sizeof(CtOp),sizeof(CtResource),sizeof(CtTemplate),sizeof(SlotHeader),sizeof(MetaRecord)};
