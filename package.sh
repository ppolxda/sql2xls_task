rm -rf build
rm -rf dist
rm -f sql2xls_webapp.spec
rm -f sql2xls_worker.spec

OUTPUT=../output
PATH_NAME=`basename \`pwd\``

cp pkg/sql2xls_webapp.py ./sql2xls_webapp.py
cp pkg/sql2xls_worker.py ./sql2xls_worker.py

pipenv run pyinstaller -F sql2xls_webapp.py
pipenv run pyinstaller -F sql2xls_worker.py

mkdir dist/log
mkdir dist/log/app
mkdir dist/log/worker
mkdir dist/config
cp -r config dist/
cp -r ./pkg/conv_funcs.py dist/funcs.py

mkdir ${OUTPUT}
rm -rf ${OUTPUT}/${PATH_NAME}
mv dist ${OUTPUT}/${PATH_NAME}

rm -rf ${OUTPUT}/${PATH_NAME}.tar.gz
tar zcvf ${OUTPUT}/${PATH_NAME}.tar.gz ${OUTPUT}/${PATH_NAME}

rm -rf build
rm -rf dist
rm -f sql2xls_webapp.spec
rm -f sql2xls_worker.spec
rm -f sql2xls_webapp.py
rm -f sql2xls_worker.py