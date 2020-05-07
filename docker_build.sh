#docker image cdrx/pyinstaller-linux python build
export PIP_INDEX_URL=https://pypi.douban.com/simple/
export VIRTUAL_ENV=/src
echo $VIRTUAL_ENV

cp pkg/sql2xls_webapp.py ./sql2xls_webapp.py
cp pkg/sql2xls_worker.py ./sql2xls_worker.py
chmod +x ./*

pip3 install git+https://github.com/ppolxda/pyopts

pip3 install -r req_requirements.txt

pip3 install pyinstaller -U

pip3 list

pyinstaller -F  sql2xls_webapp.py --hidden-import=pymysql

echo "finsh build sql2xls_webapp"

pyinstaller -F  sql2xls_worker.py --hidden-import=pymysql

echo "finsh build sql2xls_worker"
