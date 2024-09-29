#sh response_check.sh 2aedac846d0d11ef8e97acde48001122 192.168.1.25
#   $0                $1                               $2

curl -s -k -H"hue-application-key: $1" https://$2/clip/v2/resource > raw.json
cat raw.json | jq -S -c '.data[]' > linedump.json        
cat linedump.json | cargo run --example=normalize-hue-get