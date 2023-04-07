#!/usr/bin/python
#
# stacksnoop    Trace a kernel function and print all kernel stack traces.
#               For Linux, uses BCC, eBPF, and currently x86_64 only. Inline C.
#
# USAGE: stacksnoop [-h] [-p PID] [-s] [-v] function
#
# Copyright 2016 Netflix, Inc.
# Licensed under the Apache License, Version 2.0 (the "License")
#
# 12-Jan-2016   Brendan Gregg   Created this.

from __future__ import print_function
from bcc import BPF
import argparse
import time
import os

# arguments
examples = """examples:
    ./stacksnoop ext4_sync_fs           # print kernel stack traces for ext4_sync_fs
"""
parser = argparse.ArgumentParser(
    description="Trace and print kernel stack traces for a kernel function",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog=examples)
parser.add_argument("function",
    help="kernel function name")
args = parser.parse_args()
function = args.function
debug = 0

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct data_t {
    u64 stack_id;
    u32 pid;
//    char comm[TASK_COMM_LEN];
};

BPF_STACK_TRACE(stack_traces, 128);
BPF_PERF_OUTPUT(events);

void trace_stack(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    FILTER
    struct data_t data = {};
    data.stack_id = stack_traces.get_stackid(ctx, 0),
    data.pid = pid;
 //   bpf_get_current_comm(&data.comm, sizeof(data.comm));
    events.perf_submit(ctx, &data, sizeof(data));
}
"""

bpf_text = bpf_text.replace('FILTER',
        'if (pid == %s) { return; }' % os.getpid())


# initialize BPF
b = BPF(text=bpf_text)
b.attach_kprobe(event=function, fn_name="trace_stack")

# TASK_COMM_LEN = 16  # linux/sched.h

matched = b.num_open_kprobes()
if matched == 0:
    print("Function \"%s\" not found. Exiting." % function)
    exit()

stack_traces = b.get_table("stack_traces")
start_ts = time.time()

# header
print("%-18s %-6s %-3s %s" % ("TIME(s)", "PID", "CPU", "FUNCTION"))

def print_event(cpu, data, size):
    event = b["events"].event(data)

    ts = time.time() - start_ts

    print("%-18.9f %-6d %-3d %s" %
         (ts, event.pid, cpu, function))

    for addr in stack_traces.walk(event.stack_id):
        sym = b.ksym(addr, show_offset=True).decode('utf-8', 'replace')
        print("\t%s" % sym)

    print("END PRINT EVENT")

if __name__ == "__main__":
    b["events"].open_perf_buffer(print_event)
    
    n_seconds = 5
    t_end = time.time() + n_seconds
    while time.time() < t_end:
        diff = 1000 * (t_end - time.time())
        try:
            b.perf_buffer_poll(int(diff))
        except KeyboardInterrupt:
            exit()
