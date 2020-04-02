BAT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
WORKER_PATH=$BAT_PATH/..

cd $WORKER_PATH
mkdir ./log
mkdir ./log/app
mkdir ./log/worker