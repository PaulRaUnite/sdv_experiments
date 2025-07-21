import matplotlib.pyplot as plt 
import sys
from collections import OrderedDict
import numpy as np
import seaborn 
seaborn.set(font_scale=2.1) 
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams.update({'font.size': 20})
fig = plt.figure()

for thefile in ["C1", "C2"]:  
    file1 = open("configurations\\" + thefile + "\\verdict.txt", 'r')
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
    stl = "solid"     
    for con in content:
        y.append(content[con] / checknum)
        x.append(ctr)
        ctr = ctr + 1
    if thefile == "C1":
        clr = "red"
        stl = "solid"
    elif thefile == "C2":
        clr = "blue"
        stl = "dotted"
    elif thefile == "C3":
        clr = "purple"
        stl = "dashed"
    else:
        clr = "green"
        stl = "dashdot"
    plt.plot(x, y, linestyle=stl, linewidth=2, color=clr, label=thefile)
    
plt.xticks([0, 1, 2, 3, 4], fontsize=20)
plt.yticks(fontsize=20)
plt.xlabel('Number of useless actuations', fontsize=20) 
plt.ylabel('Probability', fontsize=20) 
plt.ylim(0, 1.02)
plt.legend(fontsize=20) 
plt.savefig("myImagePDF.pdf", format="pdf", bbox_inches="tight")
plt.show()