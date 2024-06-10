#!/usr/bin/env bash
cache_uname() {
    # Cache the output of uname so we don't
    # have to spawn it multiple times.
    IFS=" " read -ra uname <<< "$(uname -srm)"

    kernel_name="${uname[0]}"
    kernel_version="${uname[1]}"
    kernel_machine="${uname[2]}"

    if [[ "$kernel_name" == "Darwin" ]]; then
        # macOS can report incorrect versions unless this is 0.
        # https://github.com/dylanaraps/neofetch/issues/1607
        export SYSTEM_VERSION_COMPAT=0

        IFS=$'\n' read -d "" -ra sw_vers <<< "$(awk -F'<|>' '/key|string/ {print $3}' \
                            "/System/Library/CoreServices/SystemVersion.plist")"
        for ((i=0;i<${#sw_vers[@]};i+=2)) {
            case ${sw_vers[i]} in
                ProductName)          darwin_name=${sw_vers[i+1]} ;;
                ProductVersion)       osx_version=${sw_vers[i+1]} ;;
                ProductBuildVersion)  osx_build=${sw_vers[i+1]}   ;;
            esac
        }
    fi
}

get_os() {
    # $kernel_name is set in a function called cache_uname and is
    # just the output of "uname -s".
    case $kernel_name in
    Darwin) os=$darwin_name ;;
    SunOS) os=Solaris ;;
    Haiku) os=Haiku ;;
    MINIX) os=MINIX ;;
    AIX) os=AIX ;;
    IRIX*) os=IRIX ;;
    FreeMiNT) os=FreeMiNT ;;

    Linux | GNU*)
        os=Linux
        ;;

    *BSD | DragonFly | Bitrig)
        os=BSD
        ;;

    CYGWIN* | MSYS* | MINGW*)
        os=Windows
        ;;
    esac
}

get_model() {
    case $os in
    Linux)
        if [[ -d /system/app/ && -d /system/priv-app ]]; then
            model="$(getprop ro.product.brand) $(getprop ro.product.model)"

        elif [[ -f /sys/devices/virtual/dmi/id/board_vendor ||
            -f /sys/devices/virtual/dmi/id/board_name ]]; then
            model=$(</sys/devices/virtual/dmi/id/board_vendor)
            model+=" $(</sys/devices/virtual/dmi/id/board_name)"

        elif [[ -f /sys/devices/virtual/dmi/id/product_name ||
            -f /sys/devices/virtual/dmi/id/product_version ]]; then
            model=$(</sys/devices/virtual/dmi/id/product_name)
            model+=" $(</sys/devices/virtual/dmi/id/product_version)"

        elif [[ -f /sys/firmware/devicetree/base/model ]]; then
            model=$(</sys/firmware/devicetree/base/model)

        elif [[ -f /tmp/sysinfo/model ]]; then
            model=$(</tmp/sysinfo/model)
        fi
        ;;

    "Mac OS X" | "macOS")
        if [[ $(kextstat | grep -F -e "FakeSMC" -e "VirtualSMC") != "" ]]; then
            model="Hackintosh (SMBIOS: $(sysctl -n hw.model))"
        else
            model=$(sysctl -n hw.model)
        fi
        ;;

    BSD | MINIX)
        model=$(sysctl -n hw.vendor hw.product)
        ;;

    Windows)
        model=$(wmic computersystem get manufacturer,model)
        model=${model/Manufacturer/}
        model=${model/Model/}
        ;;

    Solaris)
        model=$(prtconf -b | awk -F':' '/banner-name/ {printf $2}')
        ;;

    AIX)
        model=$(/usr/bin/uname -M)
        ;;

    FreeMiNT)
        model=$(sysctl -n hw.model)
        model=${model/ (_MCH *)/}
        ;;
    esac

    # Remove dummy OEM info.
    model=${model//To be filled by O.E.M./}
    model=${model//To Be Filled*/}
    model=${model//OEM*/}
    model=${model//Not Applicable/}
    model=${model//System Product Name/}
    model=${model//System Version/}
    model=${model//Undefined/}
    model=${model//Default string/}
    model=${model//Not Specified/}
    model=${model//Type1ProductConfigId/}
    model=${model//INVALID/}
    model=${model//All Series/}
    model=${model//�/}

    case $model in
    "Standard PC"*) model="KVM/QEMU (${model})" ;;
    OpenBSD*) model="vmm ($model)" ;;
    esac
}

print_info() {
    echo "OS" $os
    echo "Host" $model
}

main() {
    cache_uname
    get_os
    get_model
    print_info
}

main "$@"
