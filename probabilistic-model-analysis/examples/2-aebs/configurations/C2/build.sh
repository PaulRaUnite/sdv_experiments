inputModel="aebs"
inputFinal="aebs-final"

if2gen $inputModel".if"
kp='./'$inputModel'.x -t '$inputModel'.aut'
eval $kp
bcg_io $inputModel".aut" $inputModel".bcg"
svl mod.svl