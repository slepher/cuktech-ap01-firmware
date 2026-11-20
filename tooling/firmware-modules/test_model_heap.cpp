#include "model_heap.h"
#include <assert.h>
#include <string.h>

int main() {
    alignas(16) unsigned char arena[1024];
    Ap01ModelHeap heap;
    assert(heap.bind(arena, sizeof(arena)));
    assert(!heap.bind(arena, sizeof(arena)));
    auto *first = static_cast<unsigned char *>(heap.reallocate(nullptr, 64));
    void *second = heap.reallocate(nullptr, 64);
    assert(first && second && first != second);
    memset(first, 0x5a, 64);
    auto *grown = static_cast<unsigned char *>(heap.reallocate(first, 160));
    assert(grown && grown != first);
    for (unsigned i = 0; i < 64; ++i) assert(grown[i] == 0x5a);
    assert(!heap.reallocate(grown, 2048));
    for (unsigned i = 0; i < 64; ++i) assert(grown[i] == 0x5a);
    assert(heap.reallocate(grown, 32) == grown);
    heap.reallocate(grown, 0);
    heap.reallocate(second, 0);
    void *whole = heap.reallocate(nullptr, sizeof(arena) - 16);
    assert(whole); // Adjacent free blocks coalesce after moved realloc/free.
    assert(!heap.reallocate(nullptr, 1));
    heap.reallocate(whole, 0);
}
