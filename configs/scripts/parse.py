#!/usr/bin/env python
import sys,os

filename=sys.argv[1]
execbin=sys.argv[2]
path=sys.argv[3]+'/'
linkmap=[]


def parseaddr(addrstr):
    global linkmap
    addr=int(addrstr,16)
    i=-1
    for x in linkmap:
        if addr<x[1]:
	    break
        i+=1
    if i==-1:
	tmp=os.popen('grep %s objd' %(addrstr)).read()
    	if tmp:
		return tmp.split()[1].strip('<>:')
	return os.popen('addr2line -fp -e %s %x' %(execbin,addr)).read().strip()
    return os.popen('addr2line -fp -e %s %x' %(path+linkmap[i][0],addr-linkmap[i][1])).read().strip()+' at '+linkmap[i][0]

def main():
    global linkmap
    os.system('objdump -d %s > objd' %(execbin))
    logfile=open(filename)
    out=open(filename+'-parse','w')
    for line in logfile:
        if 'linkmap begin' in line:
	    linkmap=[]
            for line1 in logfile:
                if 'linkmap end' in line1:
		    linkmap.sort(key=lambda p:p[1])
                    break
                tmp=line1.split()
                linkmap.append([tmp[0],int(tmp[1],16)])
                out.write(line1)
	else:
            tmp=line.split(',')
            if tmp[0] in ('C','R'):	    
            	pos1=parseaddr(tmp[2])
            	pos2=parseaddr(tmp[3])
            	out.write(line.strip()+','+pos1+','+pos2+'\n')
	    else:
		out.write(line)
    logfile.close()
    out.close()
    return 0

if __name__ == '__main__':
    main()
