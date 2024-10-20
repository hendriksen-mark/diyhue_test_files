#sh owngithubInstall.sh 192.168.1.25 hendriksen-mark diyHue master hendriksen-mark
#   $0                  $1           $2              $3     $4     $5
curl -s $1/save

### installing dependencies
if type apt &> /dev/null; then
  # Debian-based distro
  apt-get update
  apt-get install -y python3-pip python3-setuptools python3-dev gcc
elif type pacman &> /dev/null; then
  # Arch linux
  pacman -Syq --noconfirm || exit 1
  pacman -Sq --noconfirm python3-pip python3-setuptools python3-dev gcc || exit 1
elif type opkg &> /dev/null; then
  # openwrt
  opkg update
  opkg install python3-pip python3-setuptools python3-dev gcc
else
  # Or assume that packages are already installed (possibly with user confirmation)?
  # Or check them?
  echo -e "\033[31mUnable to detect package manager, aborting\033[0m"
  exit 1
fi

cd /
#curl -sL -o diyhue.zip https://github.com/diyhue/diyhue/archive/master.zip
#curl -sL -o diyhue.zip https://github.com/hendriksen-mark/diyhue/archive/master.zip
#curl -sL -o diyhue.zip https://github.com/hendriksen-mark/diyhue/archive/test.zip
#curl -sL -o diyhue.zip https://github.com/Fisico/diyHue-fork/archive/master.zip

curl -sL -o diyhue.zip https://github.com/$2/$3/archive/$4.zip

unzip -qo diyhue.zip
rm diyhue.zip

pip3 install --upgrade pip
pip3 install -r $3-$4/requirements.txt --no-cache-dir --break-system-packages

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

echo "restart diyhue"
curl -s $1/restart
