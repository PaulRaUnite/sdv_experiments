inputModel="simple"
inputFinal="simple-final"

if2gen $inputModel".if"
kp='./'$inputModel'.x -t '$inputModel'.aut -q '$inputModel'.kpri'
eval $kp
bcg_io $inputModel".aut" $inputModel".dot"
bcg_io $inputModel".aut" $inputModel".bcg"
svl mod.svl
bcg_io $inputFinal".aut" $inputFinal".dot"
dot -Tpdf $inputFinal".dot" > $inputFinal".pdf"
