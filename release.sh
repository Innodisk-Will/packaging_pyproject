#!/bin/bash

# ----------------------------------------------------
# Print help
helper(){
    echo "Package whole project and replace the python api to shared object"
    echo ""
    echo "$ ./release.sh [OPTION]"
    echo ""
    echo "[OPTION]"
    echo "  -r  the root to the project"
    echo "  -a  the path of the python API in target project which will be converted to dynamic shared objects."
    echo "  -z  compress the release project, default is True"
    echo "  -e  exclude files, like \"data;.git;.gitignore\""
    echo ""
    echo "[Example]"
    echo "$ ./release.sh -r ../iVINNO-api -a ../iVINNO-api/ivinno/trt -e data;.git;.gitignore "
    exit -1
}

# Check if the argument is need.
check_argument(){
    ARG="$1"
    if [[ -z $ARG ]];then helper; fi
}

# ----------------------------------------------------
# Parse argument and set default value
ZIP=1
OUT="output"
BACKUP_API="./backup"    # the folder will be generated when run setup.py
while getopts ":h:r:a:z:e:?" option; do
    case $option in
        h )
            helper ;;
        r )
            ROOT=$OPTARG ;;
        a )
            API=$OPTARG ;;
        z )
            ZIP=$OPTARG ;;
        e )
            EXC=$OPTARG ;;
        ? )
            helper ;;
    esac    
done

if [[ ! -d $OUT ]];then
    mkdir $OUT
else
    rm -rf "${OUT}/*"
fi

# ----------------------------------------------------
# Basic argument
check_argument $ROOT
check_argument $API 

PROJECT=$(basename ${ROOT})
TRG_ROOT="$(pwd)/${OUT}/${PROJECT}"
TRG_API=`echo ${API//$ROOT/$TRG_ROOT}`

# ----------------------------------------------------
# Make exclude template
arrIN=(${EXC//;/ })
TEMP=""
for i in "${arrIN[@]}";do
    NEW=$i
    TEMP="$TEMP --exclude=$NEW"
done     
echo $TEMP

# ----------------------------------------------------
# Copy the project to here
rsync $TEMP -r ${ROOT} $(dirname ${TRG_ROOT})

# ----------------------------------------------------
# Package the python file to shared objects 
python3 setup.py build_ext --inplace --src $TRG_API --backup $BACKUP_API

# Capture the error from python script
if [ $? == 1 ];
then
    echo "got error when running setup.py ..."
    exit -1
fi


# ----------------------------------------------------
# Compress project ...
if [[ -n $ZIP ]];then
    T_CUR=`date +"%y%m%d-%H%M"`
    cd ${OUT}
    zip -r "./${PROJECT}_release_${T_CUR}.zip" ${PROJECT}
    cd ..
fi

# ----------------------------------------------------
# Remove Temp file
# rm -rf ${TRG_ROOT}
rm -rf ${BACKUP_API}

echo "Done!"