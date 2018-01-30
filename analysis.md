#qemu2.5 分析文档
##程序执行流程

x86_cpu_common_cgass_init[target-i386/cpu.c] --> 

x86_cpu_realizefn[target-i386/cpu.c] --> qemu_init_vcpu[cpus.c]


qemu_init_vcpu[cpus.c] -->  qemu_tcg_init_vcpu[cpus.c]  --> qemu_thread_create[util/qemu-thread-posix.c]  --> pthread_create[libc] -->  qemu_tcg_cpu_thread_fn[cpus.c] --> tcg_exec_all[cpus.c] --> tcg_exec_all[cpus.c] --> tcg_cpu_exec[cpus.c] --> cpu-exec[cpu-exec.c]
