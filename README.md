一、安装qemu
=
目前QEMU的版本是2.0.2  
过程中可能需要安装pkg-config、libsdl1.2-dev、libpixman-1-dev、libfdt-dev、libtool、gcc-multilib等必要软件包  
./configure --target-list=i386-softmmu --enable-sdl进行配置，--target-list指定目标机的平台  
参见./configure --help  
然后执行make命令。如果是在64位机器上的话，最好使用make ARCH=x86_32,否则输出结果可能会增多

二、安装简单系统busybox
=
下载busybox1.22.1源代码  
编译对应平台的busybox  
修改busybox目录下的Makefile  
第293行："LD =$(CC) -nostdlib " -->"LD =$(CC) -nostdlib -m32"  
参见configs/busybox/Makefile文件  
以x86_32为例  
make ARCH=i386 defconfig  
make ARCH=i386 menuconfig  
1.修改Busybox Settings->  
		Build Option ->   
			[*]Build Busybox as a static binary(no shared libs)  
2.[Busybox Settings]--->  
	[Build Options]--->  
		(-m32) Additional CFLAGS  
        (-m32) Additional LDFLAGS  
3.去掉不需要的功能，其它模块编译错误做法类似  
  Networking Utilities --->  
      [ ] inetd   
最终的配置文件参见configs/busybox/config文件  
4.make ARCH=i386  
5.make ARCH=i386 install

三、使用qemu模拟linux
=
1.编写initrd启动脚本，其中BUSYBOX是busybox的路径  
cd  BUSYBOX/_install  
mkdir proc sys dev etc  
cd etc  
mkdir init.d  
vim BUSYBOX/_install/etc/init.d/rcS
```
	#!/bin/sh
	mount -t proc none /proc
	mount -t sysfs none /sys
	/sbin/mdev -s
```
参见configs/scripts/rcS文件  

2.制作rootfs.img镜像  
cd  BUSYBOX/_install  
find . | cpio -o --format=newc > BUSYBOX/rootfs.img  
注意rootfs.img不能生产在当前文件夹下，否则会生产自己的镜像。这里产生的镜像供下一步使用。
               
3.编写启动脚本  
首先要在工作的目录下新建一个addrs文件，存有5行地址，分别是内核起始地址，内核结束地址，busybox起始地址，busybox结束地址和内核符号表中modules的地址，可以参见configs/scripts/addrs文件，但需要注意的是每个内核镜像中的地址都不相同，需要自己查询。内核编译的过程是先生成一个带符号表的vmlinux文件，然后进行裁剪生成bzImage文件。qemu需要的是bzImage文件，但是查询符号表时要查询相应的vmlinux文件。可以使用nm -n命令查询符号表。busybox的地址可以在编译出的busybox_unstripped的符号表中查到（使用nm命令）。还可以使用insert-busybox.rb脚本将busybox符号表导入数据库中。  
使用以下命令运行qemu 
``` 
	#!/bin/sh
	qemut-tracer/i386-softmmu/qemu-system-i386 -kernel bzImage -initrd rootfs.img -append "root=/dev/ram rdinit=sbin/init" –d func –D log
``` 
其中bzImage是linux内核编译出的文件，在arch/i386/boot文件夹下，rootfs.img是上一步创建的镜像文件  
-d 参数指定日志输出项目,对qemu做了一定的修改,并增加了一个选项func可以追踪函数调用  
-D 参数指定日志输出文件  
针对自动测试的要求，已经写好了脚本，参见configs/scripts/a.sh
还需要对数据文件进行解析，包括parse.rb linux-3.5.4 x86_32 log result,然后使用self_time.py等脚本再处理，可以参见db-rtl-callgraph的帮助文档 

四、可加载模块
=
编译可加载模块，代码应满足一定的格式  
示例参见configs/module/factorial.c文件  
并要有Makefile，参见configs/module/Makefile文件   
在虚拟机中执行modprobe或insmod命令（具体使用可参考Linux使用帮助）载入模块
