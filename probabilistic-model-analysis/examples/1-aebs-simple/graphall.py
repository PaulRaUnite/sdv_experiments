import matplotlib.pyplot as plt 
import sys
from collections import OrderedDict
import numpy as np
import seaborn 
seaborn.set(font_scale=2.1) 
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams.update({'font.size': 22})
plt.rcParams["figure.figsize"] = (18, 10)
# fig = plt.figure()
figure, axis = plt.subplots(1, 2)
for query in ["sensor", "controller"]:
    for conf in ["C1", "C2", "C3", "C4"]:  
        file1 = open("configurations\\" + conf + "\\" + query + ".txt", 'r')
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
        if conf == "C1":
            clr = "red"
            stl = "solid"
        elif conf == "C2":
            clr = "blue"
            stl = "dotted"
        elif conf == "C3":
            clr = "purple"
            stl = "dashed"
        else:
            clr = "green"
            stl = "dashdot"
        
        if query == "sensor":
            axis[0].plot(x, y, linestyle=stl, linewidth=2, color=clr, label=conf)
        else:
            axis[1].plot(x, y, linestyle=stl, linewidth=2, color=clr, label=conf)
    
figure.suptitle("Probability of having a number of useless actuations")
figure.supxlabel('Number of useless actuations')
axis[0].set_title('During sensor sampling')
axis[1].set_title('During controller execution') 
axis[0].set_xticks([0, 1, 2, 3])
axis[1].set_xticks([0, 1, 2, 3])
axis[0].set_xlim(-0.05, 3.2)
axis[1].set_xlim(-0.05, 3.2)
axis[0].set_ylim(0, 1.02)
axis[1].set_ylim(0, 1.02)
axis[0].set_ylabel('Probability')
axis[1].set_ylabel('') 
axis[1].legend() 
figure.tight_layout()
plt.show()