inputModel="simple-final-pts"
nums=3

# sensor

inputProp="propsensor-template"
inputPropDir=(${inputProp//-/ })

rm -rf $inputPropDir && mkdir $inputPropDir
idxacts=0
until [ $idxacts == $(($nums+1)) ]
do
    sed -e "s/number-of-n/"$idxacts"/" $inputProp".mcl" > $inputPropDir"/prop-"$idxacts".mcl"
    idxacts=$((idxacts + 1))
done

echo -n "" > "sensor.txt"
idxacts=0
until [ $idxacts == $(($nums+1)) ]
do
    bcg_open -create $inputModel".bcg" evaluator5 $inputPropDir"/prop-"$idxacts".mcl" >> "sensor.txt"
    idxacts=$((idxacts + 1))
done

# controller

inputProp="propcontroller-template"
inputPropDir=(${inputProp//-/ })

rm -rf $inputPropDir && mkdir $inputPropDir
idxacts=0
until [ $idxacts == $(($nums+1)) ]
do
    sed -e "s/number-of-n/"$idxacts"/" $inputProp".mcl" > $inputPropDir"/prop-"$idxacts".mcl"
    idxacts=$((idxacts + 1))
done

echo -n "" > "controller.txt"
idxacts=0
until [ $idxacts == $(($nums+1)) ]
do
    bcg_open -create $inputModel".bcg" evaluator5 $inputPropDir"/prop-"$idxacts".mcl" >> "controller.txt"
    idxacts=$((idxacts + 1))
done