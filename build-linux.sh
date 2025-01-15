#!/bin/bash

python -m venv ./venv-linux
source ./venv-linux/bin/activate
pip install -r requirements.txt

touch ./dummy
pyinstaller --name "WEBFISHING-Sync" --add-data "etc:etc" --add-data "dummy:download_cache" --add-data "styles:PyQt5/Qt5/plugins/styles" ./backup.py

echo " "
echo "Packaging Complete"
echo " "

ls -lh ./dist/
