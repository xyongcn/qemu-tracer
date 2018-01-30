## argv[1]: symbol file, produced by `nm vmlinux`
## argv[2]: function address file need to be convert
## argv[3]: which column need to be converted
## eg: python addr2name.py func_addr.txt test.txt 2

import sys
symbol_file = sys.argv[1]
addr_file = sys.argv[2]
which_column = int(sys.argv[3])
fp_sym = open(symbol_file,'r')
dic={}
line = fp_sym.readline();
while line:
  para = line.split(' ')
  para[2] = para[2].strip('\n')
  dic[para[0]] = para[2]
  line = fp_sym.readline()
fp_sym.close()

fp_funcaddr = open(addr_file,'r')
fpw = open("out.txt",'w')

line = fp_funcaddr.readline()
while line:
  try:
    line = line.strip('\n')
    para = line.split(',')
    size = len(para)
    para[which_column] = para[which_column].lstrip('0')
    print para[which_column]
    if para[which_column] in dic:
      para[which_column] = dic[para[which_column]]

    for i in range(0,size-1):
      if i==which_column:
        fpw.write(para[i].ljust(30,' ')+",")
      else:
        fpw.write(para[i]+",")
    fpw.write(para[i+1]+"\n")
  except:
    fpw.write(line+"\n")
  line = fp_funcaddr.readline()
fpw.close();
fp_funcaddr.close()

