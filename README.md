# QEMU-TRACER实现细节

### 新增加文件

```
include/comm_struct/List.h //链表
comm_struct/List.c
include/comm_struct/Stack.h //栈
comm_struct/Stack.c
include/comm_struct/MachineBit.h //有关不同cpu、内核的配置
comm_struct/Makefile.objs //编译以上有关头文件

注意：为了能够编译以上头文件，还需要修改qemu-tracer/Makefile.objs，一遍使用comm_struct编译后的结果
```

### 代码实现

#### vl.c文件

新增加的的函数

```
read_configs() //读取配置文件的入口函数
map_reg() //去读configs/reg_map.txt中寄存器与参数、返回值的对应关系
```

在main函数中调用read_configs函数，读取配置文件信息
```
if (qemu_loglevel_mask(CPU_LOG_FUNC)) {    
/*
param1: program which need to be traced,eg:sshd,kernel 
param2: address range of tracing, it can be 00~ff,1f,5d..., it's union set 
param3: record parameter, it should be string,int,socket
param4: record link map, it should be linkMap if link map is needed, else no
param5: record function stack, it should be funcStack else no
*/

read_configs();
}
```

配置文件细节

1. qemu-tracer对vl.c文件进行了修改，主要用来读取配置文件，配置文件的名字固定为configs.txt

2. qemu-tracer需要通过一个配置文件来指定寄存器和对应的函数位置之间的关系，该文件放在configs/reg_map.txt中，目前内容如下：

   ```
    32 R_EAX 0 --> 0
    32 R_EAX 1 --> 0
    32 R_ECX 2 --> 1
    32 R_EDX 3 --> 2 
    64 R_EAX 0 --> 0
    64 R_EDI 1 --> 7
    64 R_ESI 2 --> 6 
    64 R_EDX 3 --> 2
    64 R_ECX 4 --> 1
    64 R_8 5 --> 8
    64 R_9 6 --> 9
   ```

   ```
   第一列表示平台位数，第二列为寄存器，第三列为参数的位置（其中0表示返回值），第四列位“-->”，第五列为QEMU-TRACER中寄存器定义的宏(该值与第二列绑定)
   配置文件中，返回值必须出现在参数之前，而且，当没有配置返回值时，默认按照int输出
   ```

#### cpu-exec.c文件

截获qemu中的函数调用和返回主要通过修改该文件实现，该文件中增加了一下函数：

```
record_info()//在tb块执行完毕之后，记录相关信息，记录的主要控制函数
record_stack()//在线记录函数调用栈，在跟踪到特定的函数后，将函数调用栈输出
record_stack_call() //记录分析函数调用栈中的call指令
record_stack_ret() //记录分析函数调用栈中的ret指令
print_stack_to_file() //将函数调用栈输出到stack文件
print_log_to_file() //将函数调用和返回输出到log文件
print_all_regs_para() //输出所有寄存器的值，按十六进制输出
print_return() //输出返回值
print_parameter() //输出参数，不同参数的输出方法不相同
print_reg() //输出相应寄存器中的参数
printIntParameter() //输出int型参数
printStrParameter() //输出string类型的参数
funcistraced() //通过二分法查找函数地址，判断某个函数是否会被指定跟踪，所以读入的地址需要有序
init_some_list() //初始化返回地址列表
get_write_file() //打开日志stack文件，单例模式
printLinkMap() //输出got表
traverseLinkMap() //遍历got表，输出动态链接库的名字和加载地址
getLinkMapStartAddrByDynamic() //通过.dynamic段得到link map的起始地址
getLinkMapStartAddrByGot() //通过.got.plt段得到link map的起始地址
print_cred_by_task_struct() //输出task_struct中的cred字段，提供task_struct的起始地址
print_file_inode_by_dentry() //输出dentry中的inode字段，提供dentry的起始地址
print_inode() //输出inode
mySocket() //获取socket的内容
getPid() //获取pid
getParentPid() //获取父进程pid
printList() //遍历链表
```

在cpu-exec.c函数中，执行完一个tb块后，记录相关信息

```
next_tb = cpu_tb_exec(cpu, tc_ptr);
if(qemu_loglevel_mask(CPU_LOG_FUNC) && (next_tb & TB_EXIT_MASK)<2){
if(tb->type==TB_CALL || tb->type==TB_RET){
record_info(env,cpu,tb);
```

#### target-i386/translate.c

对tb翻译块中的call和return进行标记，可以查看TB__CALL和TB_RET相关的位置

#### qemu-log.c和 include/qemu/log.h

加入了-d func参数来指定对函数进行跟踪

### 扩展QEMU-TRACER

1. 新增对参数类型的支持？

   1. 在include/comm_struct/MachineBit.h中增加一个新的宏定义，仿照如下：

      ```
      #define PARA_INT 0
      #define PARA_STRING 1 
      #define PARA_SOCKET 2 
      #define PARA_CRED 3 
      #define PARA_INODE 4
      #define PARA_DENTRY 5
      ```

   2. 修改vl.c中的reg_map函数，加一个如下类似```else if```

      ```
      else if(strcmp(trace_func[i].para[j].type,"dentry")==0){
           trace_func[i].para[j].i_type = PARA_DENTRY;
      }
      ```

   3. 在vl.c中加入一个读取该参数的函数，并```print_reg```函数中调用，添加相应的```case```

      ```
      static void print_reg(FILE *fp,CPUState *cpu, my_target_ulong reg, int i_type){
          switch(i_type){
              case PARA_SOCKET :
                  printSocket(stackWrite,cpu,reg);
                  break;
      ```

      ​

# 使用前的准备工作

### 安装QEMU-TRACER

QEMU的版本：2.4.50  

1. 下载：

在linux环境中下载本仓库的代码

2. 安装依赖:

   ```
   pkg-config、libsdl1.2-dev、libpixman-1-dev、libfdt-dev、libtool、gcc-multilib
   ```

3. 配置:

  ​x86_32

  ​```./configure --target-list=i386-softmmu --enable-sdl```

  ​x86_64

  ​```./configure --target-list=x86_64-softmmu --enable-sd```

  ​参考 ./configure --help

  ​目前在跟踪状态下，不管客户机操作系统是32位还是64位，QEMU-TRACER统一编译成x86_64平台

4. 编译：

   执行make命令，为了加快速度可以使用-j参数，例如使用-j4表示使用4核编译。如果是在64位机器上使用qemu-system-i386的话，使用make ARCH=x86_32

5. 运行（以x86_64为例）：

   Lubuntu

   ```
   qemu-system-x86_64 -m 2G lubuntu.raw
   ```

   busybox

   ```
   qemu-system-x86_64 -kernel bzImage -initrd rootfs.img -append "root=/dev/ram rdinit=sbin/init" -rtc clock=vm -net nic -net user
   ```



### 简单系统busybox

1. 下载busybox1.22.1源代码  

2. 编译对应平台的busybox  

   1. 修改busybox目录下的Makefile 的第293行，参见本仓库中configs/busybox/Makefile文件：

      ```
      "LD =$(CC) -nostdlib " ====修改成====> "LD =$(CC) -nostdlib -m32"   
      ```

   2. 配置，以x86_32为例 

      ```
      make ARCH=i386 defconfig
      make ARCH=i386 menuconfig
      ```

      修改配置项

      ```
      Busybox Settings->  
      Build Option ->   
      	[*]Build Busybox as a static binary(no shared libs)
      	(-m32) Additional CFLAGS  
          (-m32) Additional LDFLAGS 
      ```

   3. 去掉不需要的功能，其它模块编译错误做法类似 ，例如：

      ```
      Networking Utilities --->  
      	[ ] inetd   
      ```

   最终的配置文件参见本仓库中的configs/busybox/config文件  

3. make ARCH=i386  

4. make ARCH=i386 install

### QEMU-TRACER中运行busybox

上一节中编译生成了busybox，但其只是一个壳，还需要Linux内核来与之配合，下面介绍如何利用busybox来启动Linux内核

1. 编写initrd启动脚本，其中BUSYBOX是busybox的路径  

   ```
   cd  BUSYBOX/_install
   mkdir -p proc sys dev etc/init.d
   vim BUSYBOX/_install/etc/init.d/rcS
   ```

   rcS文件如下，参见本仓库configs/scripts/rcS文件  ：

    ```
   #!/bin/sh
   mount -t proc none /proc
   mount -t sysfs none /sys
   /sbin/mdev -s
    ```

2. 制作rootfs.img镜像 

   ```
   cd  BUSYBOX/_install
   find . | cpio -o --format=newc > BUSYBOX/rootfs.img
   注意: rootfs.img不能生产在当前文件夹下，否则会生产自己的镜像。这里产生的镜像供下一步使用。
   ```

3. 启动

   ```
   qemu-system-x86_64 -kernel bzImage -initrd rootfs.img -append "root=/dev/ram rdinit=sbin/init" -rtc clock=vm -net nic -net user
   ```

### QEMU-TRACER中运行Lubuntu

1. 创建镜像文件，raw格式，

   ```
   qemu-img create -f raw lubuntu.raw 8G
   ```

2. 下载Lubuntu镜像（iso文件）

3. 在raw中安装Lubuntu

   ```
   qemu-system-x86_64 -enable-kvm -boot d -cdrom lubuntu.iso -m 2G -hda lubuntu.raw
   //在不跟踪的时候可以启用kvm来加速
   ```

4. 启动Lubuntu

   ```
   qemu-system-x86_64 -enable-kvm -m 2G lubuntu.raw
   ```



# 利用QEMU-TRACER进行跟踪

1. 根据被跟踪系统的平台以及是否记录所有的log，具体方式是修改include/comm_struct/MachineBit.h文件中的如下宏，0标识关闭，1标识打开，目前支持32位和64位系统，如果当前系统为32位则使用```#define osBit32 1``` ，64位则使用```#define osBit32 0```，```define QEMULOG 1```表示是否将函数调用和返回都记录下来，其结果存在在log文件中，1表示打开日志。

   ```
   #define osBit32 1
   #define isBusybox 1
   #define isLubuntu32 0 
   #define isLubuntu64 0
   #define QEMULOG 1 //whether record the functions call log
   ```

2. include/comm_struct/MachineBit.h文件涉及到各个系统中相关结构体成员的偏移，例如下面的宏中，```#define commOffset 0x3f0```表示在Lubuntu系统中，task_struct的comm字段相对于task_struct的偏移，计算结构体成员的偏移可以使用内核可加载模块，并通过C语言的offset函数来计算，具体参考configs/comm-offset文件夹中的内容；如果是busybox环境中，不具备编译内核可加载模块的环境，可以事先在外部编译好模块后，然后在busybox中加载。

   ```
   #if isLubuntu32
   #define commOffset 0x3f0 
   #define pidOffset 0x308 
   #define tgidOffset 0x30c
   #define parentOffset 0x318
   #define realParentOffset 0x314
   #endif
   ```

3. include/comm_struct/MachineBit.h中模块相关的宏如下，moduleNameoffset表示模module结构体中name字段的偏移，moduleCoreOffset表示module结构体中module_core（模块的加载地址）的偏移。FUNC_PARA_MODULE表示内核中的一个函数，该函数用来加载一个module，可以从该函数的参数读取module的加载地址，MODULE_NAME表示module的名字。

   ```
   #define moduleNameOffset 0x18
   #define moduleCoreOffset 0x1c8
   //do_init_module, linux-4.2.0
   #define FUNC_PARA_MODULE 0xffffffff817e66a0
   #define MODULE_NAME "overlay"
   ```

4. 目前模块相关的处理还不是很完善，可以看到cpu-exec.c中record_info函数有专门一段处理内核模块的，如果内核发生变化，跟踪不同模块时需要改动的部分还比较多，例如目前include/comm_struct/MachineBit.h默认配置中，isLubuntu64的4.2.0的内核采用```do_init_module```函数加载模块，此时R_EDI寄存器中存储着被加载module的地址，所以读取该module结构体就能知道模块的加载地址。

   ```
   // trim_init_extable_addr defined in MachineBit.h
       if(ld.goAddr == FUNC_PARA_MODULE){
           char mod_name[16];
           my_target_ulong mod = env->regs[R_EDI];
           cpu_memory_rw_debug(cpu,mod + moduleNameOffset,(uint8_t*)&mod_name,sizeof(mod_name),0);
           fprintf(stackWrite,MY_TARGET_FMT_lx",%s  !!!!\n",mod_core,mod_name);

           if(strcmp(mod_name,MODULE_NAME)==0){
               cpu_memory_rw_debug(cpu,mod + moduleCoreOffset,(uint8_t*)&mod_core,sizeof(mod_core),0);
               fprintf(stackWrite,MY_TARGET_FMT_lx",%s",mod_core,mod_name);
           }
       }
   ```

5. 重新编译QEMU-TRACER，如果之前编译过，现在可以直接make，否则参考上面QEMU-TRACER的编译方法

6. 在本地增加一个配置文件configs.txt，其中的内容如下：

   ```
   helloWorld
   ffffffffffffffff~ffffffffffffffff
   0~0
   funcstack:0
   linkmap:610000
   trace_type:spec_func_with_param
   ffffffff12345678,0,int,1,string
   ```

   ```
   第一行，helloWorld表示跟踪的程序的名字
   第二行，跟踪的内核的地址范围
   第三行，跟踪的用户态程序的地址范围
   第四行，是否打印函数调用栈，取值1或0
   第五行，got表的地址，打印动态链接库的地址的加载地址，可以从反汇编的.got.plt段中读取地址，可以用于时候解析动态链接库中的地址与函数名的对应关系，不过目前该功能暂未使用
   第六行，跟踪的类型，目前有一下选项：
   	spec_func_with_param //只跟踪配置文件中指定函数的信息
   	all_func_without_param //跟踪所有的函数，但是没有参数信息
   	all_func_with_param //跟踪所有函数，同时打印参数，但是参数只是寄存器中的值，没有做任何解析
   	process_func_without_param //跟踪指定程序的所有函数，但没有参数
   	process_func_with_param //跟踪指定的程序的函数，打印寄存器的值
   	nomal //跟踪指定范围能的函数，并根据funcstack的配置来跟踪函数调用栈
   	
   第七行，指定特定的跟踪函数，第一个为函数地址，后面的会成对出现例如(0，int)，(1，string)，数字表示参数或返回值位置，第二项表示类型。注意：0表示返回值的位置，int表示返回值类型，0,int必须放在最前面，不关心返回值的话，可以写成ffffffff12345678,1,string，但是不能写成ffffffff12345678,1,string,0,int。跟踪多个函数时，地址需要按从小到大的顺序排列。

   注意：all_func_without_param，all_func_with_param，process_func_without_param，		process_func_with_param的输出文件为log，需要打开#define QEMULOG 1 
   ```

   如何查询函数地址？

   ```
   1. 内核编译的过程是先生成一个带符号表的vmlinux文件，然后进行裁剪生成bzImage文件。qemu需要的是bzImage文件，但是查询符号表时要查询相应的vmlinux文件。可以使用nm -n命令查询符号表。busybox的地址可以在编译出的busybox_unstripped的符号表中查到（使用nm命令）。也可以查看内核和busybox编译出来生成的System.map，也含有符号表。
   2. Lubuntu则可以直接查看System.map文件
   3. 二进制文件则可以使用objdump来反汇编得到函数入口地址
   ```

7. 配置完成后，在configs.txt所在的文件夹下运行QEMU-TRACER，主要是指定-d func 和-D log参数，-d 参数指定日志输出项目，对qemu做了一定的修改，并增加了一个选项func可以追踪函数调用；-D 参数指定日志输出文件

   ```
   qemu-system-x86_64 -m 2G lubuntu.raw -d func -D log
   ```

   busybox，需要提供kernel编译的bzImage和busybox的rootfs.img，并且由于目前的busybox为32位cpu平台，而且没有动态链接相关工具，所以编译程序时需要静态编译，即加入-static -m32编译选项

   ```
   qemu-system-x86_64 -kernel bzImage -initrd rootfs.img -append "root=/dev/ram rdinit=sbin/init" -rtc clock=vm -net nic -net user -d func -D log
   ```

8. 结果位于stack和log文件

9. 注意：跟踪过程中不可开启kvm加速



—by aquan
