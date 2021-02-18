# c2shellcode

Converts `c` programs that only use syscalls to 64 bit `assembly` file.

It is works with `64 bit syscalls`

## Usage

```bash
python3 c2shellcode.py [d] input.c output.s
```

Using `-d` deletes `input_temp.s` which created with `gcc`.

`input.c` must only contains syscalls.

## Example input.c code

```c
#define _GNU_SOURCE 1
#include <sys/sendfile.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>
#include <assert.h>
#include <unistd.h>
#include <stdio.h>
#include <errno.h>
#include <fcntl.h>
#include <time.h>
#include <dirent.h>

int main(int argc, char **argv)
{
    char* argv[3] = {"/bin/cat", "/flag", NULL};
    execve("/bin/cat", argv, NULL);
}
```

```bash
python3 -d input.c output.s
```

## Example output.s assembly

```as
.global _start
.intel_syntax noprefix
_start:
    endbr64
    push	rbp
    mov	rbp, rsp
    sub	rsp, 32
    lea	rax, .LC0[rip]
    mov	QWORD PTR -32[rbp], rax
    lea	rax, .LC1[rip]
    mov	QWORD PTR -24[rbp], rax
    mov	QWORD PTR -16[rbp], 0
    lea	rax, -32[rbp]
    mov	edx, 0
    mov	rsi, rax
    lea	rdi, .LC0[rip]
    # call	execve@PLT
    mov rax, 59
    syscall

    mov	eax, 0
    leave
    ret
.LC0:
	.string	"/bin/cat"
.LC1:
	.string	"/flag"

```


Also you can use my [runner.sh](https://gist.github.com/ebubekirtrkr/e8cce31ab32e6ec291dc2d9b5412abb6) script to get raw-bytes from shellcode and analys it.

I created `syscalls.csv` with `getSyscalsFromWebsite.py` which gets syscall numbers, syscall names and argument length from the awesome site [Searchable Linux Syscall Table,  filippo.io](https://filippo.io/linux-syscall-table/)