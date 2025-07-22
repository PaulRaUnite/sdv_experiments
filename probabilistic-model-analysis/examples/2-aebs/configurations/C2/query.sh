inputModel="aebs-final-pts"
nums=4

inputProp="prop-template"
inputPropDir=(${inputProp//-/ })

rm -rf $inputPropDir && mkdir $inputPropDir
idxacts=0
until [ $idxacts == $(($nums+1)) ]
do
    sed -e "s/number-of-n/"$idxacts"/" $inputProp".mcl" > $inputPropDir"/prop-"$idxacts".mcl"
    idxacts=$((idxacts + 1))
done

echo -n "" > "verdict.txt"
idxacts=0
until [ $idxacts == $(($nums+1)) ]
do
    bcg_open -create $inputModel".bcg" evaluator5 $inputPropDir"/prop-"$idxacts".mcl" >> "verdict.txt"
    idxacts=$((idxacts + 1))
done
