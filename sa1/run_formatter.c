#include <stdio.h>
#include "make_formatter.h"

int main() {
    formatter x08_format = make_formatter("%08x\n");
    formatter xalt_format = make_formatter("%#x\n");
    formatter d_format = make_formatter("%d\n");
    formatter verbose_format = make_formatter("Liczba: %9d!\n");

    x08_format(0x1234);
    xalt_format(0x5678);
    d_format(0x9abc);
    verbose_format(0xdef0);
}
