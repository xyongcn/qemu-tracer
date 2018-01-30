ifndef KERNELDIR
	#KERNELDIR  := /lib/modules/$(shell uname -r)/build
	KERNELDIR  := /lib/modules/3.5.4/build
endif

obj-m := offset.o

all:
	$(MAKE) -C $(KERNELDIR) M=$(PWD)

clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean

install:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules_install
	/sbin/depmod -ae
