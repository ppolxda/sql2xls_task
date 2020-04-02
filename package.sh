rm -rf build
rm -rf dist
rm -f pynotify_worker.spec

OUTPUT=../output
PATH_NAME=`basename \`pwd\``

pipenv run pyinstaller -F sql2xls_task.py

mkdir dist/logfile
mkdir dist/config
cp -r config/logging dist/config/logging
cp -r run.sh dist/run.sh
cp -r conv_funcs.py dist/funcs.py

mkdir ${OUTPUT}
rm -rf ${OUTPUT}/${PATH_NAME}
mv dist ${OUTPUT}/${PATH_NAME}

rm -rf ${OUTPUT}/${PATH_NAME}.tar.gz
tar zcvf ${OUTPUT}/${PATH_NAME}.tar.gz ${OUTPUT}/${PATH_NAME}

rm -rf build
rm -rf dist
rm -f pynotify_worker.spec
