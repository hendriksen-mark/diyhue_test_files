curl -s 192.168.1.25/save
cd /
if [ -d diyhueUI ]; then
 rm -r diyhueUI
fi
mkdir diyhueUI
#curl -sL https://github.com/diyhue/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
unzip -qo /opt/hue-emulator/build.zip -d /diyhueUI
#rm /opt/hue-emulator/build.zip
#cd diyhueUI
cp -r /diyhueUI/build/index.html /opt/hue-emulator/flaskUI/templates/
cp -r /diyhueUI/build/static /opt/hue-emulator/flaskUI/

#cp -r /diyhueUI/index.html /opt/hue-emulator/flaskUI/templates/
#cp -r /diyhueUI/static /opt/hue-emulator/flaskUI/

curl -s 192.168.1.25/restart