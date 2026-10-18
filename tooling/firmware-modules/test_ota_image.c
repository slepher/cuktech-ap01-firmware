#include "ota_image.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MODEL_OFFSET 0x4d48u
#define MIN_IMAGE (MODEL_OFFSET + 17u + 40u)
#define MAX_IMAGE 0x700000u

typedef struct {
    unsigned char *data;
    size_t size;
} blob;

static uint32_t le32(const unsigned char *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void put_le32(unsigned char *p, uint32_t value)
{
    p[0] = (unsigned char)value;
    p[1] = (unsigned char)(value >> 8);
    p[2] = (unsigned char)(value >> 16);
    p[3] = (unsigned char)(value >> 24);
}

static void put_be32(unsigned char *p, uint32_t value)
{
    p[0] = (unsigned char)(value >> 24);
    p[1] = (unsigned char)(value >> 16);
    p[2] = (unsigned char)(value >> 8);
    p[3] = (unsigned char)value;
}

static uint32_t crc32_update(uint32_t value, const unsigned char *p, size_t n)
{
    while (n--) {
        unsigned bit;
        value ^= *p++;
        for (bit = 0; bit != 8; ++bit)
            value = (value >> 1) ^ (0xedb88320u & (0u - (value & 1u)));
    }
    return value;
}

static void fix_header(unsigned char *data)
{
    put_le32(data + 252, crc32_update(0xffffffffu, data, 252) ^ 0xffffffffu);
}

static void fix_recovery(unsigned char *data, size_t size)
{
    unsigned char *tail = data + size - 40;
    put_le32(tail + 36, crc32_update(0, data, size - 4));
}

static blob read_blob(const char *name)
{
    blob result;
    FILE *file = fopen(name, "rb");
    long length;
    size_t got;

    assert(file);
    assert(!fseek(file, 0, SEEK_END));
    length = ftell(file);
    assert(length > 0);
    assert(!fseek(file, 0, SEEK_SET));
    result.size = (size_t)length;
    result.data = (unsigned char *)malloc(result.size);
    assert(result.data);
    got = fread(result.data, 1, result.size, file);
    assert(!fclose(file));
    assert(got == result.size);
    return result;
}

static int check(const unsigned char *data, size_t available, uint32_t length,
                 size_t width, const unsigned char *reference, int expected)
{
    ota_image image;
    size_t position = 0;

    if (ota_image_begin(&image, length))
        return expected ? 0 : 1;
    while (position < available) {
        size_t bytes = available - position;
        if (bytes > width)
            bytes = width;
        if (ota_image_chunk(&image, data + position, bytes))
            return expected ? 0 : 1;
        position += bytes;
    }
    return ota_image_valid(&image, reference) == expected;
}

static blob resized(const blob *source, size_t size)
{
    blob result;
    size_t body = size - 40;
    size_t source_body = source->size - 40;

    assert(size >= MIN_IMAGE && size <= MAX_IMAGE);
    result.size = size;
    result.data = (unsigned char *)calloc(size, 1);
    assert(result.data);
    memcpy(result.data, source->data, body < source_body ? body : source_body);
    if (body > source_body)
        memset(result.data + source_body, 0xa5, body - source_body);
    memcpy(result.data + body, source->data + source_body, 40);
    put_be32(result.data + body + 32, (uint32_t)size);
    put_le32(result.data + 0x84, (uint32_t)(size - 0x1000));
    fix_header(result.data);
    fix_recovery(result.data, size);
    assert(le32(result.data + 0x84) == size - 0x1000);
    return result;
}

static void negative_cases(const blob *source, const unsigned char *reference,
                           unsigned *checks)
{
    blob copy;
    size_t tail = source->size - 40;

    copy.size = source->size;
    copy.data = (unsigned char *)malloc(copy.size);
    assert(copy.data);
    memcpy(copy.data, source->data, copy.size);

    copy.data[0] ^= 1;
    fix_header(copy.data);
    assert(check(copy.data, copy.size, (uint32_t)copy.size, 1024, reference, 0));
    ++*checks;
    /* Recompute both CRCs: these must fail compatibility, not just corruption. */
    {
        const unsigned offsets[] = { 0x10, 0x78, 0x7c, 0xb0 };
        size_t i;
        for (i = 0; i < sizeof(offsets)/sizeof(offsets[0]); ++i) {
            memcpy(copy.data, source->data, copy.size);
            copy.data[offsets[i]] ^= 1;
            fix_header(copy.data);
            fix_recovery(copy.data, copy.size);
            assert(check(copy.data, copy.size, (uint32_t)copy.size, 13, reference, 0));
            ++*checks;
        }
    }
    memcpy(copy.data, source->data, copy.size);
    put_le32(copy.data+0x84, (uint32_t)copy.size);
    fix_header(copy.data);
    fix_recovery(copy.data, copy.size);
    assert(check(copy.data, copy.size, (uint32_t)copy.size, 1024, reference, 0));
    ++*checks;
    memcpy(copy.data, source->data, copy.size);
    copy.data[0x10] ^= 1;
    fix_header(copy.data);
    assert(check(copy.data, copy.size, (uint32_t)copy.size, 7, reference, 0));
    ++*checks;
    memcpy(copy.data, source->data, copy.size);
    put_le32(copy.data + 0x84, 0);
    fix_header(copy.data);
    assert(check(copy.data, copy.size, (uint32_t)copy.size, 1, reference, 0));
    ++*checks;
    memcpy(copy.data, source->data, copy.size);
    copy.data[MODEL_OFFSET] ^= 1;
    fix_recovery(copy.data, copy.size);
    assert(check(copy.data, copy.size, (uint32_t)copy.size, 1024, reference, 0));
    ++*checks;
    memcpy(copy.data, source->data, copy.size);
    copy.data[tail] ^= 1;
    fix_recovery(copy.data, copy.size);
    assert(check(copy.data, copy.size, (uint32_t)copy.size, 7, reference, 0));
    ++*checks;
    memcpy(copy.data, source->data, copy.size);
    put_be32(copy.data + tail + 32, (uint32_t)(copy.size - 1));
    fix_recovery(copy.data, copy.size);
    assert(check(copy.data, copy.size, (uint32_t)copy.size, 1, reference, 0));
    ++*checks;
    memcpy(copy.data, source->data, copy.size);
    copy.data[copy.size - 1] ^= 1;
    assert(check(copy.data, copy.size, (uint32_t)copy.size, 1024, reference, 0));
    ++*checks;
    assert(check(source->data, source->size - 1, (uint32_t)source->size,
                 7, reference, 0));
    ++*checks;
    assert(ota_image_begin((ota_image *)copy.data, MAX_IMAGE + 1));
    ++*checks;
    assert(ota_image_begin((ota_image *)copy.data, MIN_IMAGE - 1));
    ++*checks;
    free(copy.data);
}

int main(int argc, char **argv)
{
    static const size_t widths[] = { 1, 7, 1024 };
    blob original;
    blob small;
    blob large;
    blob maximum;
    unsigned checks = 0;
    size_t i;

    assert(argc >= 2 && argc <= 3);
    original = read_blob(argv[1]);
    assert(original.size >= MIN_IMAGE && original.size <= MAX_IMAGE);
    for (i = 0; i < sizeof(widths) / sizeof(widths[0]); ++i) {
        assert(check(original.data, original.size, (uint32_t)original.size,
                     widths[i], original.data, 1));
        ++checks;
    }
    small = resized(&original, MIN_IMAGE + 31);
    large = resized(&original, original.size + 4096);
    maximum = resized(&original, MAX_IMAGE);
    assert(check(small.data, small.size, (uint32_t)small.size, 1,
                 original.data, 1));
    ++checks;
    assert(check(maximum.data, maximum.size, (uint32_t)maximum.size, 1024,
                 original.data, 1));
    ++checks;
    assert(check(large.data, large.size, (uint32_t)large.size, 1024,
                 original.data, 1));
    ++checks;
    negative_cases(&original, original.data, &checks);
    if (argc == 3) {
        blob candidate = read_blob(argv[2]);
        assert(candidate.size >= MIN_IMAGE && candidate.size <= MAX_IMAGE);
        assert(check(candidate.data, candidate.size, (uint32_t)candidate.size,
                     7, original.data, 1));
        ++checks;
        free(candidate.data);
    }
    printf("{\"passed\":true,\"checks\":%u,\"original_bytes\":%zu,\"small_bytes\":%zu,\"large_bytes\":%zu}\n",
           checks, original.size, small.size, large.size);
    free(large.data);
    free(maximum.data);
    free(small.data);
    free(original.data);
    return 0;
}
