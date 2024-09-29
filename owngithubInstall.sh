#sh owngithubInstall.sh 192.168.1.25 hendriksen-mark diyHue master hendriksen-mark
#   $0                  $1           $2              $3     $4     $5
curl -s $1/save
cd /
#curl -sL -o diyhue.zip https://github.com/diyhue/diyhue/archive/master.zip
#curl -sL -o diyhue.zip https://github.com/hendriksen-mark/diyhue/archive/master.zip
#curl -sL -o diyhue.zip https://github.com/hendriksen-mark/diyhue/archive/test.zip
#curl -sL -o diyhue.zip https://github.com/Fisico/diyHue-fork/archive/master.zip

curl -sL -o diyhue.zip https://github.com/$2/$3/archive/$4.zip

unzip -qo diyhue.zip
rm diyhue.zip
#cd diyhue
cp -r $3-$4/BridgeEmulator/flaskUI /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/functions /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/lights /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/sensors /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/HueObjects /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/services /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/configManager /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/logManager /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/HueEmulator3.py /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/genCert.sh /opt/hue-emulator/
cp -r $3-$4/BridgeEmulator/openssl.conf /opt/hue-emulator/
chmod +x /opt/hue-emulator/genCert.sh

#cd /
if [ -d diyhueUI ]; then
 rm -r diyhueUI
fi
mkdir diyhueUI
#curl -sL https://github.com/diyhue/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
#curl -sL https://github.com/hendriksen-mark/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
curl -sL https://github.com/$5/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
unzip -qo diyHueUI.zip -d diyhueUI
rm diyHueUI.zip
#cd diyhueUI
cp -r diyhueUI/index.html /opt/hue-emulator/flaskUI/templates/
cp -r diyhueUI/static /opt/hue-emulator/flaskUI/

curl -s $1/restart
