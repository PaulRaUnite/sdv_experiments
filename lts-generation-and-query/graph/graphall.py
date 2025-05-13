import matplotlib.pyplot as plt 
import sys
from collections import OrderedDict
import numpy as np
import seaborn 
seaborn.set(font_scale=2.1) 
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams.update({'font.size': 19})
fig = plt.figure()

for thefile in ["C2", "C3"]:  
    file1 = open(thefile + ".txt", 'r')
    content = {}
    Lines = file1.readlines()
    ctr = 0
    checknum = 0
    tmpKey = ""
    for line in Lines:
        if "bcg_open" in line:
            content[str(ctr)] = 0
        elif "TRUE" in line:
            ctr = ctr + 1
        elif len(line.strip()) != 0 and "bcg_open" not in line and "TRUE" not in line:
            content[str(ctr)] = content[str(ctr)] + float(line)
            if ctr == 0:
                checknum = checknum + 1    
    x=[]
    y=[]
    ctr = 0        
    for con in content:
        y.append(content[con] / checknum)
        x.append(ctr)
        ctr = ctr + 1
    if thefile == "C2-normal" or thefile == "C3-normal":
        stl = "dashed"
    else:
        stl = "solid"
    if thefile == "C3":
        clr = "#1563c2"
    else:
        clr = "green"
    plt.plot(x, y, linestyle=stl, linewidth=2, color=clr, label=thefile)
    
plt.xticks([0, 1, 2, 3, 4])
plt.xlabel('Number of useless actuations', fontsize=30) 
plt.ylabel('Probability', fontsize=30) 
plt.ylim(0, 1.02)
plt.legend(fontsize=30) 
plt.show() 
