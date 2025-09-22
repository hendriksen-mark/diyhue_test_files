from threading import Thread
import ctypes
from ctypes import *
import ctypes.wintypes
import json
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
import sys,os
import base64
import time
import platform

if platform.system() == "Darwin":  # Check if the OS is macOS
    import Quartz.CoreGraphics as CG  # Add this import for macOS screen capture
else:
    raise ImportError("Quartz.CoreGraphics is only available on macOS.")
DeviceIP = ["192.168.1.94"] #INSERT YOUR DEVICE IP(S)

def GoveeLocalControl(Command,brightness=0,color=None,Loop=False,UDP_IP='',UDP_PORT=4003,printStatus=True,errorCount=0):
    lastColor = None
    global sock

    def SendCommand(message,individualIP,UDP_PORT):
        jsonResult = json.dumps(message)
        # jsonResult = jsonResult.replace("'",'"')
        print("Sending: {} to {} - {}".format(Command,individualIP,jsonResult))
        sock.sendto(bytes(jsonResult, "utf-8"), (individualIP, UDP_PORT))

    try:
        if Command == "Color":      
                message = {
                    "msg":{
                        "cmd":"colorwc",
                        "data":{
                            "color":{"r":color[0],"g":color[1],"b":color[2]},
                            "colorTemInKelvin":0
                        }    
                    }
                }    
        elif Command == "On":
            message = {
                "msg":{
                    "cmd":"turn",
                    "data":{
                        "value":1,
                    }    
                }
            }
        elif Command == "Off":
            message = {
                "msg":{
                    "cmd":"turn",
                    "data":{
                        "value":0,
                    }    
                }
            } 
        elif Command == "SegmentInit": 
            message = {
                "msg":{
                    "cmd":"status",
                    "data":{}    
                }
            }                      
            for individualIP in UDP_IP:
                SendCommand(message,individualIP,UDP_PORT)          
            message = {
                "msg":{
                    "cmd":"razer",
                    "data":{
                        'pt':'uwABsQEK',
                    }    
                }
            } 
            for individualIP in UDP_IP:
                SendCommand(message,individualIP,UDP_PORT)  
            message = {
                "msg":{
                    "cmd":"status",
                    "data":{}    
                }
            }                 
            time.sleep(2)
        elif Command == "SegmentTerm": 
            message = {
                "msg":{
                    "cmd":"status",
                    "data":{}    
                }
            }                      
            for individualIP in UDP_IP:
                SendCommand(message,individualIP,UDP_PORT)              
            message = {
                "msg":{
                    "cmd":"razer",
                    "data":{
                        'pt':'uwABsQAL',
                    }    
                }
            } 
            for individualIP in UDP_IP:
                SendCommand(message,individualIP,UDP_PORT)     
            message = {
                "msg":{
                    "cmd":"status",
                    "data":{}    
                }
            }
            time.sleep(2) 
        elif Command == "SegmentColor":
            gradientFlag = 1
            r=color[0][0]
            g=color[0][1]
            b=color[0][2]
            gradientFlag = 1
            # byteArray = [187,0,32,176,gradientFlag,10,r,g,b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,b,r,g,b]
            byteArray = [187,0,32,176,gradientFlag,10,color[0][0],color[0][1],color[0][2],color[0][0],color[0][1],color[0][2],color[0][0],color[0][1],color[0][2],color[0][0],color[0][1],color[0][2],color[0][0],color[0][1],color[0][2],color[1][0],color[1][1],color[1][2],color[1][0],color[1][1],color[1][2],color[1][0],color[1][1],color[1][2],color[1][0],color[1][1],color[1][2],color[1][0],color[1][1],color[1][2]]  
            num2 = 0
            for byte in byteArray:
                num2 ^= byte
            byteArray.append(num2)
            finalSendValue = (base64.b64encode(bytes(byteArray)).decode())            
            message = {
                "msg":{
                    "cmd":"razer",
                    "data":{
                        'pt':finalSendValue,
                    }    
                }
            }                          
        elif Command == "BrightLevel":
            message = {
                "msg":{
                    "cmd":"brightness",
                    "data":{
                        "value":brightness,
                    }    
                }
            }  
        else:
            raise ValueError("Bad Command: {}".format(Command))

        #To print or not to print
        if Loop == False and printStatus == True:
            print("Govee Internal Control: {}".format(Command)) 
        
        #Send command from above
        for individualIP in UDP_IP:
            SendCommand(message,individualIP,UDP_PORT)
    except Exception as E:        
        errorCount += 1
        if errorCount > 3:
            print("Govee Internal Control Error Recursion Exit: {}".format(str(E)))
            return
        else:
            print("Govee Internal Control Error: {}".format(str(E)))
            return GoveeLocalControl(Command,brightness,color,Loop,UDP_IP,UDP_PORT,printStatus,errorCount)

def capture_pixel_color(x, y):
    """Capture the color of a pixel at (x, y) using Quartz."""
    region = CG.CGRectMake(x, y, 1, 1)
    image = CG.CGWindowListCreateImage(region, CG.kCGWindowListOptionOnScreenOnly, CG.kCGNullWindowID, CG.kCGWindowImageDefault)
    if image is None:
        raise ValueError("Unable to capture screen region.")
    bitmap = CG.CGImageGetBitmap(image)
    data = CG.CGDataProviderCopyData(CG.CGImageGetDataProvider(bitmap))
    pixel = bytearray(data)
    red, green, blue = pixel[2], pixel[1], pixel[0]  # Quartz uses BGRA format
    return red, green, blue

def main(DeviceIP):
    global boxSize
    global sock
    errorNotified = False
    lastColor = None

    screen_width = CG.CGDisplayPixelsWide(CG.CGMainDisplayID())
    screen_height = CG.CGDisplayPixelsHigh(CG.CGMainDisplayID())
    print("Using Screen Dimensions: {} {}".format(screen_width, screen_height))
    middle_x = screen_width // 2
    middle_y = screen_height // 2
    chunk = int(screen_width / 4)

    try:
        print("Game Time Function: Turning Lights On")
        while True:
            try:
                # Capture pixel colors from two screen regions
                pixelColor1 = capture_pixel_color(middle_x - chunk, middle_y)
                pixelColor2 = capture_pixel_color(middle_x + chunk, middle_y)

                # Send colors
                if "Error" in pixelColor1 or "Error" in pixelColor2:
                    if errorNotified == False:
                        print(f"Error In Colors Loop: {pixelColor1} {pixelColor2}")
                    errorNotified = True
                    time.sleep(5)
                    continue
                else:
                    lastColor = pixelColor1
                    errorNotified = False
                    GoveeLocalControl(Command="SegmentColor", UDP_IP=DeviceIP, color=(pixelColor1, pixelColor2))
            except Exception as E:
                print(f"Govee Game Time Inner Loop Error: {str(E)}")
        # If for some reason we break from loop and we return from this thread, we want to power down lights.
        print("Game Time Function: Turning Lights Off. Thread Is Dead.")
        GoveeLocalControl(Command="Off", UDP_IP=DeviceIP)
        raise NameError("NormalReturn")
    except Exception as E:
        if "NormalReturn" in str(E):
            print("Game Time Function: Turning Lights Off. Thread Is Dead.")
            return "NormalExit"
        else:
            print("Govee Game Time Loop Error: {}".format(str(E)))
            GoveeLocalControl(Command="Off", UDP_IP=DeviceIP)
            return "Error"        

try:
    print("Press Ctrl + C To Quit (Lights Should Turn Off)\n\n")
    GoveeLocalControl(Command="SegmentTerm",UDP_IP=DeviceIP)
    GoveeLocalControl(Command="Off",UDP_IP=DeviceIP) 
    time.sleep(2)
    GoveeLocalControl(Command="On",UDP_IP=DeviceIP) 
    GoveeLocalControl(Command="BrightLevel",UDP_IP=DeviceIP,brightness=100)
    time.sleep(2)
    GoveeLocalControl(Command="SegmentInit",UDP_IP=DeviceIP)
    time.sleep(5)
    GoveeLocalControl(Command="SegmentColor",color=(255,0,0),UDP_IP=DeviceIP)
    main(DeviceIP)
except KeyboardInterrupt:
    GoveeLocalControl(Command="SegmentTerm",UDP_IP=DeviceIP)
    GoveeLocalControl(Command="Off",UDP_IP=DeviceIP) 
    try:
        sys.exit(130)
    except SystemExit:
        os._exit(130)