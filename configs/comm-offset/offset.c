#include <linux/module.h>
#include <linux/sched.h>
#include <linux/dcache.h>
#include <linux/fs.h>
#include <linux/module.h>
int init_module()
{
    printk(KERN_INFO "comm offset in task_struct is 0x%lx\n", offsetof(struct task_struct, comm));
    printk(KERN_INFO "pid offset in task_struct is 0x%lx\n", offsetof(struct task_struct, pid));
    printk(KERN_INFO "tgid offset in task_struct is 0x%lx\n", offsetof(struct task_struct, tgid));
    printk(KERN_INFO "real_parent offset in task_struct is 0x%lx\n", offsetof(struct task_struct, real_parent));

	printk(KERN_INFO "parent offset in task_struct is 0x%lx\n", offsetof(struct task_struct, parent));
	printk(KERN_INFO "cred offset in task_struct is 0x%lx\n", offsetof(struct task_struct, cred));

	printk(KERN_INFO "uid offset in task_struct is 0x%lx\n", offsetof(struct cred, uid));
	printk(KERN_INFO "gid offset in task_struct is 0x%lx\n", offsetof(struct cred, gid));

	printk(KERN_INFO "d_inode offset in dentry is 0x%lx\n", offsetof(struct dentry, d_inode));
	printk(KERN_INFO "i_mode offset in inode is 0x%lx\n", offsetof(struct inode, i_mode));
	printk(KERN_INFO "i_uid offset in inode is 0x%lx\n", offsetof(struct inode, i_uid));
	printk(KERN_INFO "i_gid offset in inode is 0x%lx\n", offsetof(struct inode, i_gid));
	printk(KERN_INFO "i_ino offset in inode is 0x%lx\n", offsetof(struct inode, i_ino));

    printk(KERN_INFO "name offset in module is 0x%lx\n", offsetof(struct module, name));
    printk(KERN_INFO "module_core offset in module is 0x%lx\n", offsetof(struct module, module_core));

	return 0;
}

void cleanup_module() { }
