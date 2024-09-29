#sh docker_cp.sh file location/ restart 192.168.1.25
#   $0           $1   $2        $3      $4
sudo docker cp $1 diyHue:/opt/hue-emulator/$2$1

if [ $# -eq 4 ]; then
    if [ $3 = true ]; then
        curl -s $4/save
        curl -s $4/restart
    fi
fi
