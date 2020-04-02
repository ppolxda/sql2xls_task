set BAT_PATH=%~sdp0
python3 -m pyfuncs.genconf.logger_conf_maker --input=%BAT_PATH%/worker/logging.json --output=%BAT_PATH%/worker --tmpl=%BAT_PATH%/logging.tmpl --count=10
python3 -m pyfuncs.genconf.logger_conf_maker --input=%BAT_PATH%/app/logging.json --output=%BAT_PATH%/app --tmpl=%BAT_PATH%/logging.tmpl --count=10
