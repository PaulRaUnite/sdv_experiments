inputFinal="simple-final"
inputModel="simple-final-pts"
inputTrace="trace"
nums=4
inputProp="props-template"
inputPropDir=(${inputProp//-/ })

java -cp ptsv.jar ptsv $inputFinal $inputTrace
bcg_io $inputFinal"-pts.aut" $inputFinal"-pts.bcg"

rm -rf $inputPropDir && mkdir $inputPropDir
idxacts=0
until [ $idxacts == $(($nums+1)) ]
do
    sed -e "s/number-of-n/"$idxacts"/" $inputProp".mcl" > $inputPropDir"/prop-"$idxacts".mcl"
    idxacts=$((idxacts + 1))
done

echo -n "" > "verdicts.txt"
idxacts=0
until [ $idxacts == $(($nums+1)) ]
do
    bcg_open -create $inputModel".bcg" evaluator5 $inputPropDir"/prop-"$idxacts".mcl" >> "verdicts.txt"
    idxacts=$((idxacts + 1))
done

