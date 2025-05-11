inputModel="simple-final-pts"
nums=5
inputProp="props-template"
inputPropDir=(${inputProp//-/ })

bcg_io $inputModel".aut" $inputModel".bcg"

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

