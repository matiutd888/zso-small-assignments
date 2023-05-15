#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdlib.h>
#include <string.h>
#include "make_formatter.h"

static uint8_t function_content[] = {
        0x55,
        0x48, 0x89, 0xE5,
        0x48, 0x83, 0xEC, 0x10,
        0x89, 0x7D, 0xFC,
        0x8B, 0x45, 0xFC,
        0x89, 0xC6,
        0x48, 0xB8, 0, 0, 0, 0, 0, 0, 0, 0,
        0x48, 0x89, 0xC7,
        0xB8, 0x0, 0, 0, 0,
        0x48, 0xBA, 0, 0, 0, 0, 0, 0, 0, 0,
        0xFF, 0xD2,
        0x90,
        0xC9,
        0xC3,
};

#define FUNCTION_SIZE (sizeof(function_content) / sizeof(uint8_t))
#define FORMAT_ARG_INDEX 18
#define PRINT_ARG_INDEX 36

static void fill_memory(uint8_t *place, uint64_t address) {
    for (int i = 0; i < 8; i++) {
        place[i] = address % (1 << 8);
        address >>= 8;
    }
}

formatter make_formatter(const char *format) {
    uint64_t *format_addr = (uint64_t *) format;
    uint64_t *printf_addr = (uint64_t *) printf;
    fill_memory(&function_content[FORMAT_ARG_INDEX], (uint64_t) format_addr);
    fill_memory(&function_content[PRINT_ARG_INDEX], (uint64_t) printf_addr);
    uint8_t *ptr = mmap(NULL, FUNCTION_SIZE,
                        PROT_READ | PROT_WRITE | PROT_EXEC, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

    if (ptr == MAP_FAILED) {
        fprintf(stderr, "Mapping Failed\n");
        exit(1);
    }
    memcpy(ptr, function_content, FUNCTION_SIZE);

    return (formatter) ptr;
}
