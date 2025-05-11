inputModel="simple"
inputFinal="simple-final"
inputHidden="simple-hidden"
inputTrace="trace"

if2gen $inputModel".if"
kp='./'$inputModel'.x -t '$inputModel'.aut -q '$inputModel'.kpri'
eval $kp
bcg_io $inputModel".aut" $inputModel".dot"
bcg_io $inputModel".aut" $inputModel".bcg"
svl mod.svl
bcg_io $inputFinal".aut" $inputFinal".dot"
bcg_io $inputHidden".aut" $inputHidden".dot"
dot -Tpdf -Gdpi=300 $inputHidden".dot" > $inputHidden".pdf"

java -cp ptsv.jar ptsv $inputFinal $inputTrace
bcg_io $inputFinal"-pts.aut" $inputFinal"-pts.bcg"

./verify.sh

python graphall.py
