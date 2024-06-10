curl -s localhost/save
cd /
#curl -s -J -L -o diyhue.tar.gz "https://github.com/diyhue/diyHue/archive/refs/heads/master.tar.gz"
#curl -s -J -L -o diyhue.tar.gz "https://github.com/hendriksen-mark/diyhue/archive/refs/heads/master.tar.gz"
#curl -sL -o diyhue.zip https://github.com/diyhue/diyhue/archive/master.zip
#curl -sL -o diyhue.zip https://github.com/hendriksen-mark/diyhue/archive/master.zip
curl -sL -o diyhue.zip https://github.com/Fisico/diyHue-fork/archive/master.zip
#tar xzf diyhue.tar.gz --strip-components=1 -C diyhue
unzip -qo diyhue.zip
rm diyhue.zip
#cd diyhue
cp -r diyHue-fork-master/BridgeEmulator/flaskUI /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/functions /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/lights /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/sensors /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/HueObjects /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/services /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/configManager /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/logManager /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/HueEmulator3.py /opt/hue-emulator/
#cp -r diyHue-fork-master/BridgeEmulator/githubInstall.sh /opt/hue-emulator/
#cp -r diyHue-fork-master/BridgeEmulator/githubUIInstall.sh /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/genCert.sh /opt/hue-emulator/
cp -r diyHue-fork-master/BridgeEmulator/openssl.conf /opt/hue-emulator/
chmod +x /opt/hue-emulator/genCert.sh

#cd /
if [ -d diyhueUI ]; then
 rm -r diyhueUI
fi
mkdir diyhueUI
curl -sL https://github.com/diyhue/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
#curl -sL https://github.com/hendriksen-mark/diyHueUI/releases/latest/download/DiyHueUI-release.zip -o diyHueUI.zip
unzip -qo diyHueUI.zip -d diyhueUI
rm diyHueUI.zip
#cd diyhueUI
cp -r diyhueUI/index.html /opt/hue-emulator/flaskUI/templates/
cp -r diyhueUI/static /opt/hue-emulator/flaskUI/

curl -s localhost/restart
