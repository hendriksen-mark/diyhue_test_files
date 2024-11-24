//#include <EthernetWebServer.h>  //https://github.com/khoih-prog/EthernetWebServer
#include <WebServer_ESP32_W5500.h> //https://github.com/khoih-prog/WebServer_ESP32_W5500
//#include <Ethernet.h>
#define INT_GPIO 3

#include <LittleFS.h>
#include <ArduinoJson.h>
#include <EEPROM.h>
//#define DEBUGLOG_ENABLE_FILE_LOGGER
#include <DebugLog.h>
#include <HTTPUpdateServer.h>
HTTPUpdateServer httpUpdateServer;

#include <NeoPixelBus.h>

RgbColor red = RgbColor(255, 0, 0);
RgbColor green = RgbColor(0, 255, 0);
RgbColor white = RgbColor(255);
RgbColor black = RgbColor(0);

#define INFO_DATA_PIN 12

int debug_light, light_rec, rec, debug_code;

byte mac[] = { 0xDA, 0xAD, 0xEB, 0xFF, 0xEF, 0xDE };

NeoPixelBus<NeoRgbFeature, NeoEsp32Rmt0Ws2812xMethod>* strip_info = NULL;

#include <Wire.h>

#define light_name_i2c "Dimmable Hue Light ESP32"  //default light name
#define LIGHT_VERSION_i2c 2.1

//define pins
#define LIGHTS_COUNT_i2c 7
//                            kamer    woonkamer      keuken    slaapkamer      gang    badkamer
//                            nummer   1    2   3     4         5               6       7
//                            array    0    1   2     3         4               5       6
int lightadress_i2c[LIGHTS_COUNT_i2c] {9,   10, 11,   12,       13,             14,     15};

unsigned long previousMillis = 0;
#define LIGHT_interval 60000


bool light_state_i2c[LIGHTS_COUNT_i2c], in_transition_i2c, alert = false;
int transitiontime_i2c, bri_i2c[LIGHTS_COUNT_i2c], error_code;
float step_level_i2c[LIGHTS_COUNT_i2c], current_bri_i2c[LIGHTS_COUNT_i2c];

byte hb, lb;

WebServer server_i2c(80);

#include "painlessMesh.h"
#include <Arduino_JSON.h>

int subip = 25;
IPAddress bridgeIp(192, 168, 1, subip);

#define   MESH_PREFIX     "HomeMesh"
#define   MESH_PASSWORD   "Qwertyuiop1"
#define   MESH_PORT       5555
#define   connectMode     WIFI_AP_STA
#define   channel         1
#define   hidden          true
painlessMesh  mesh;

int value;
String room_mac;
bool change = false;
uint32_t curtain_id = 0;

byte target;//0-100%
byte current;//0-100%

byte target_ont;//0-100%
byte current_ont;//0-100%

bool fout = false;

int state_ont;//0 1 2

int ishome;

#define RES 2

#define ESP_SW_RX            "A0"
#define ESP_SW_TX            "A1"

#define DEBUG "false"

#define totalrond 123

#define DIR 8
#define STEP 7
#define ENABLE 4
#define DRIVER_ADDRESS "0b00"  // Set by MS1/MS2. LOW/LOW in this case
#define R_SENSE "0.11f"
#define SW_RX            6
#define SW_TX            5

#define MOTOR_STEPS 200
#define MICROSTEPS 16// fixed
#define motorSpeed 625//*16=10000 // speed voor full step
#define motorAcc 400//*16=3200 // Acceleration voor full step

#define UART_STEALTH_MODE 1
#define GUIDE_MICROSTEPPING       MICROSTEPS
#define R_current "1500mA"

#define home_switch 2

unsigned long lastreq = 0;

WebServer server_gordijn(82);
WebServer server_mesh(83);

WiFiClient client;

//const char* bridgeIp = "192.168.1.25";
//IPAddress bridgeIp(192, 168, 1, 25);
//const char* switchType = "ZLLSwitch";
#define switchType "ZLLSwitch"
#define motionType "ZLLPresence"

#define LIGHT_VERSION 4.1
#define LIGHT_NAME_MAX_LENGTH 32 // Longer name will get stripped
#define ENTERTAINMENT_TIMEOUT 1500 // millis
//#define POWER_MOSFET_PIN 35 // WS2812 consume ~1mA/led when off. By installing a MOSFET it will cut the power to the leds when lights ore off.
#define DATA_PIN 4

struct state {
  uint8_t colors[3], bri = 100, sat = 254, colorMode = 2;
  bool lightState;
  int ct = 200, hue;
  float stepLevel[3], currentColors[3], x, y;
};

state lights[10];
bool inTransition, entertainmentRun, mosftetState, useDhcp = true;
byte packetBuffer[46];
unsigned long lastEPMillis, lastWiFiCheck;

//settings
char lightName[LIGHT_NAME_MAX_LENGTH] = "Hue WS2811 strip";
uint8_t effect, scene, startup, onPin = 8, offPin = 9 ;
bool hwSwitch = false;
uint8_t rgb_multiplier[] = {100, 100, 100}; // light multiplier in percentage /R, G, B/

uint16_t dividedLightsArray[30];

uint8_t lightsCount = 9;
uint16_t pixelCount = 9;
uint8_t transitionLeds = 0; // pixelCount must be divisible by this value

WebServer server_ws(81);
WiFiUDP Udp;

NeoPixelBus<NeoRgbFeature, NeoEsp32Rmt1Ws2812xMethod>* strip = NULL;

void blinkLed(uint8_t count, uint16_t interval = 200) {
  RgbColor color = strip_info->GetPixelColor(0);
  for (uint8_t i = 0; i < count; i++) {
    strip_info->SetPixelColor(0, black);
    strip_info->Show();
    delay(interval);
    strip_info->SetPixelColor(0, color);
    strip_info->Show();
    delay(interval);
  }
}

void convertHue(uint8_t light) // convert hue / sat values from HUE API to RGB
{
  double      hh, p, q, t, ff, s, v;
  long        i;

  s = lights[light].sat / 255.0;
  v = lights[light].bri / 255.0;

  if (s <= 0.0) {      // < is bogus, just shuts up warnings
    lights[light].colors[0] = v;
    lights[light].colors[1] = v;
    lights[light].colors[2] = v;
    return;
  }
  hh = lights[light].hue;
  if (hh >= 65535.0) hh = 0.0;
  hh /= 11850, 0;
  i = (long)hh;
  ff = hh - i;
  p = v * (1.0 - s);
  q = v * (1.0 - (s * ff));
  t = v * (1.0 - (s * (1.0 - ff)));

  switch (i) {
    case 0:
      lights[light].colors[0] = v * 255.0;
      lights[light].colors[1] = t * 255.0;
      lights[light].colors[2] = p * 255.0;
      break;
    case 1:
      lights[light].colors[0] = q * 255.0;
      lights[light].colors[1] = v * 255.0;
      lights[light].colors[2] = p * 255.0;
      break;
    case 2:
      lights[light].colors[0] = p * 255.0;
      lights[light].colors[1] = v * 255.0;
      lights[light].colors[2] = t * 255.0;
      break;

    case 3:
      lights[light].colors[0] = p * 255.0;
      lights[light].colors[1] = q * 255.0;
      lights[light].colors[2] = v * 255.0;
      break;
    case 4:
      lights[light].colors[0] = t * 255.0;
      lights[light].colors[1] = p * 255.0;
      lights[light].colors[2] = v * 255.0;
      break;
    case 5:
    default:
      lights[light].colors[0] = v * 255.0;
      lights[light].colors[1] = p * 255.0;
      lights[light].colors[2] = q * 255.0;
      break;
  }

}

void convertXy(uint8_t light) // convert CIE xy values from HUE API to RGB
{
  int optimal_bri = lights[light].bri;
  if (optimal_bri < 5) {
    optimal_bri = 5;
  }
  float Y = lights[light].y;
  float X = lights[light].x;
  float Z = 1.0f - lights[light].x - lights[light].y;

  // sRGB D65 conversion
  float r =  X * 3.2406f - Y * 1.5372f - Z * 0.4986f;
  float g = -X * 0.9689f + Y * 1.8758f + Z * 0.0415f;
  float b =  X * 0.0557f - Y * 0.2040f + Z * 1.0570f;


  // Apply gamma correction
  r = r <= 0.0031308f ? 12.92f * r : (1.0f + 0.055f) * pow(r, (1.0f / 2.4f)) - 0.055f;
  g = g <= 0.0031308f ? 12.92f * g : (1.0f + 0.055f) * pow(g, (1.0f / 2.4f)) - 0.055f;
  b = b <= 0.0031308f ? 12.92f * b : (1.0f + 0.055f) * pow(b, (1.0f / 2.4f)) - 0.055f;

  // Apply multiplier for white correction
  r = r * rgb_multiplier[0] / 100;
  g = g * rgb_multiplier[1] / 100;
  b = b * rgb_multiplier[2] / 100;

  if (r > b && r > g) {
    // red is biggest
    if (r > 1.0f) {
      g = g / r;
      b = b / r;
      r = 1.0f;
    }
  }
  else if (g > b && g > r) {
    // green is biggest
    if (g > 1.0f) {
      r = r / g;
      b = b / g;
      g = 1.0f;
    }
  }
  else if (b > r && b > g) {
    // blue is biggest
    if (b > 1.0f) {
      r = r / b;
      g = g / b;
      b = 1.0f;
    }
  }

  r = r < 0 ? 0 : r;
  g = g < 0 ? 0 : g;
  b = b < 0 ? 0 : b;

  lights[light].colors[0] = (int) (r * optimal_bri); lights[light].colors[1] = (int) (g * optimal_bri); lights[light].colors[2] = (int) (b * optimal_bri);
}

void convertCt(uint8_t light) // convert ct (color temperature) value from HUE API to RGB
{
  int hectemp = 10000 / lights[light].ct;
  int r, g, b;
  if (hectemp <= 66) {
    r = 255;
    g = 99.4708025861 * log(hectemp) - 161.1195681661;
    b = hectemp <= 19 ? 0 : (138.5177312231 * log(hectemp - 10) - 305.0447927307);
  } else {
    r = 329.698727446 * pow(hectemp - 60, -0.1332047592);
    g = 288.1221695283 * pow(hectemp - 60, -0.0755148492);
    b = 255;
  }

  r = r > 255 ? 255 : r;
  g = g > 255 ? 255 : g;
  b = b > 255 ? 255 : b;

  // Apply multiplier for white correction
  r = r * rgb_multiplier[0] / 100;
  g = g * rgb_multiplier[1] / 100;
  b = b * rgb_multiplier[2] / 100;

  lights[light].colors[0] = r * (lights[light].bri / 255.0f); lights[light].colors[1] = g * (lights[light].bri / 255.0f); lights[light].colors[2] = b * (lights[light].bri / 255.0f);
}

void handleNotFound_ws() { // default webserver response for unknow requests
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server_ws.uri();
  message += "\nMethod: ";
  message += (server_ws.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server_ws.args();
  message += "\n";
  for (uint8_t i = 0; i < server_ws.args(); i++) {
    message += " " + server_ws.argName(i) + ": " + server_ws.arg(i) + "\n";
  }
  server_ws.send(404, "text/plain", message);
}

void apply_scene_ws(uint8_t new_scene) { // these are internal scenes store in light firmware that can be applied on boot and manually from light web interface
  for (uint8_t light = 0; light < lightsCount; light++) {
    if ( new_scene == 1) {
      lights[light].bri = 254; lights[light].ct = 346; lights[light].colorMode = 2; convertCt(light);
    } else if ( new_scene == 2) {
      lights[light].bri = 254; lights[light].ct = 233; lights[light].colorMode = 2; convertCt(light);
    }  else if ( new_scene == 3) {
      lights[light].bri = 254; lights[light].ct = 156; lights[light].colorMode = 2; convertCt(light);
    }  else if ( new_scene == 4) {
      lights[light].bri = 77; lights[light].ct = 367; lights[light].colorMode = 2; convertCt(light);
    }  else if ( new_scene == 5) {
      lights[light].bri = 254; lights[light].ct = 447; lights[light].colorMode = 2; convertCt(light);
    }  else if ( new_scene == 6) {
      lights[light].bri = 1; lights[light].x = 0.561; lights[light].y = 0.4042; lights[light].colorMode = 1; convertXy(light);
    }  else if ( new_scene == 7) {
      lights[light].bri = 203; lights[light].x = 0.380328; lights[light].y = 0.39986; lights[light].colorMode = 1; convertXy(light);
    }  else if ( new_scene == 8) {
      lights[light].bri = 112; lights[light].x = 0.359168; lights[light].y = 0.28807; lights[light].colorMode = 1; convertXy(light);
    }  else if ( new_scene == 9) {
      lights[light].bri = 142; lights[light].x = 0.267102; lights[light].y = 0.23755; lights[light].colorMode = 1; convertXy(light);
    }  else if ( new_scene == 10) {
      lights[light].bri = 216; lights[light].x = 0.393209; lights[light].y = 0.29961; lights[light].colorMode = 1; convertXy(light);
    } else {
      lights[light].bri = 144; lights[light].ct = 447; lights[light].colorMode = 2; convertCt(light);
    }
  }
}

void processLightdata(uint8_t light, float transitiontime = 4) { // calculate the step level of every RGB channel for a smooth transition in requested transition time
  transitiontime *= 14 - (pixelCount / 70); //every extra led add a small delay that need to be counted for transition time match
  if (lights[light].colorMode == 1 && lights[light].lightState == true) {
    convertXy(light);
  } else if (lights[light].colorMode == 2 && lights[light].lightState == true) {
    convertCt(light);
  } else if (lights[light].colorMode == 3 && lights[light].lightState == true) {
    convertHue(light);
  }
  for (uint8_t i = 0; i < 3; i++) {
    if (lights[light].lightState) {
      lights[light].stepLevel[i] = ((float)lights[light].colors[i] - lights[light].currentColors[i]) / transitiontime;
    } else {
      lights[light].stepLevel[i] = lights[light].currentColors[i] / transitiontime;
    }
  }
}

RgbColor blending(float left[3], float right[3], uint8_t pixel) { // return RgbColor based on neighbour leds
  uint8_t result[3];
  for (uint8_t i = 0; i < 3; i++) {
    float percent = (float) pixel / (float) (transitionLeds + 1);
    result[i] = (left[i] * (1.0f - percent) + right[i] * percent);
  }
  return RgbColor((uint8_t)result[0], (uint8_t)result[1], (uint8_t)result[2]);
}

void candleEffect() {
  for (uint8_t light = 0; light < lightsCount; light++) {
    lights[light].colors[0] = random(170, 254);
    lights[light].colors[1] = random(37, 62);
    lights[light].colors[2] = 0;
    for (uint8_t i = 0; i < 3; i++) {
      lights[light].stepLevel[i] = ((float)lights[light].colors[i] - lights[light].currentColors[i]) / random(5, 15);
    }
  }
}

void firePlaceEffect() {
    for (uint8_t light = 0; light < lightsCount; light++) {
    lights[light].colors[0] = random(100, 254);
    lights[light].colors[1] = random(10, 35);
    lights[light].colors[2] = 0;
    for (uint8_t i = 0; i < 3; i++) {
      lights[light].stepLevel[i] = ((float)lights[light].colors[i] - lights[light].currentColors[i]) / random(5, 15);
    }
  }
}

RgbColor convFloat(float color[3]) { // return RgbColor from float
  return RgbColor((uint8_t)color[0], (uint8_t)color[1], (uint8_t)color[2]);
}


void cutPower() {
  bool any_on = false;
  for (int light = 0; light < lightsCount; light++) {
    if (lights[light].lightState) {
      any_on = true;
    }
  }
  if (!any_on && !inTransition && mosftetState) {
    //digitalWrite(POWER_MOSFET_PIN, LOW);
    mosftetState = false;
  } else if (any_on && !mosftetState) {
    //digitalWrite(POWER_MOSFET_PIN, HIGH);
    mosftetState = true;
  }
}

void lightEngine() {  // core function executed in loop()
  for (int light = 0; light < lightsCount; light++) { // loop with every virtual light
    if (lights[light].lightState) { // if light in on
      if (lights[light].colors[0] != lights[light].currentColors[0] || lights[light].colors[1] != lights[light].currentColors[1] || lights[light].colors[2] != lights[light].currentColors[2]) { // if not all RGB channels of the light are at desired level
        inTransition = true;
        for (uint8_t k = 0; k < 3; k++) { // loop with every RGB channel of the light
          if (lights[light].colors[k] != lights[light].currentColors[k]) lights[light].currentColors[k] += lights[light].stepLevel[k]; // move RGB channel on step closer to desired level
          if ((lights[light].stepLevel[k] > 0.0 && lights[light].currentColors[k] > lights[light].colors[k]) || (lights[light].stepLevel[k] < 0.0 && lights[light].currentColors[k] < lights[light].colors[k])) lights[light].currentColors[k] = lights[light].colors[k]; // if the current level go below desired level apply directly the desired level.
        }
        if (lightsCount > 1) { // if are more then 1 virtual light we need to apply transition leds (set in the web interface)
          if (light == 0) { // if is the first light we must not have transition leds at the beginning
            for (int pixel = 0; pixel < dividedLightsArray[0]; pixel++) // loop with all leds of the light (declared in web interface)
            {
              if (pixel < dividedLightsArray[0] - transitionLeds / 2) { // apply raw color if we are outside transition leds
                strip->SetPixelColor(pixel, convFloat(lights[light].currentColors));
              } else {
                strip->SetPixelColor(pixel, blending(lights[0].currentColors, lights[1].currentColors, pixel + 1 - (dividedLightsArray[0] - transitionLeds / 2 ))); // calculate the transition led color
              }
            }
          }
          else { // is not the first virtual light
            for (int pixel = 0; pixel < dividedLightsArray[light]; pixel++) // loop with all leds of the light
            {
              long pixelSum;
              for (int value = 0; value < light; value++)
              {
                if (value + 1 == light) {
                  pixelSum += dividedLightsArray[value] - transitionLeds;
                }
                else {
                  pixelSum += dividedLightsArray[value];
                }
              }

              if (pixel < transitionLeds / 2) { // beginning transition leds
                strip->SetPixelColor(pixel + pixelSum + transitionLeds, blending( lights[light - 1].currentColors, lights[light].currentColors, pixel + 1));
              }
              else if (pixel > dividedLightsArray[light] - transitionLeds / 2 - 1) {  // end of transition leds
                //Serial.println(String(pixel));
                strip->SetPixelColor(pixel + pixelSum + transitionLeds, blending( lights[light].currentColors, lights[light + 1].currentColors, pixel + transitionLeds / 2 - dividedLightsArray[light]));
              }
              else  { // outside transition leds (apply raw color)
                strip->SetPixelColor(pixel + pixelSum + transitionLeds, convFloat(lights[light].currentColors));
              }
              pixelSum = 0;
            }
          }
        } else { // strip has only one virtual light so apply raw color to entire strip
          strip->ClearTo(convFloat(lights[light].currentColors), 0, pixelCount - 1);
        }
        strip->Show(); //show what was calculated previously
      }
    } else { // if light in off, calculate the dimming effect only
      if (lights[light].currentColors[0] != 0 || lights[light].currentColors[1] != 0 || lights[light].currentColors[2] != 0) { // proceed forward only in case not all RGB channels are zero
        inTransition = true;
        for (uint8_t k = 0; k < 3; k++) { //loop with every RGB channel
          if (lights[light].currentColors[k] != 0) lights[light].currentColors[k] -= lights[light].stepLevel[k]; // remove one step level
          if (lights[light].currentColors[k] < 0) lights[light].currentColors[k] = 0; // save condition, if level go below zero set it to zero
        }
        if (lightsCount > 1) { // if the strip has more than one light
          if (light == 0) { // if is the first light of the strip
            for (int pixel = 0; pixel < dividedLightsArray[0]; pixel++) // loop with every led of the virtual light
            {
              if (pixel < dividedLightsArray[0] - transitionLeds / 2) { // leds until transition zone apply raw color
                strip->SetPixelColor(pixel, convFloat(lights[light].currentColors));
              } else { // leds in transition zone apply the transition color
                strip->SetPixelColor(pixel, blending(lights[0].currentColors, lights[1].currentColors, pixel + 1 - (dividedLightsArray[0] - transitionLeds / 2 )));
              }
            }
          }
          else { // is not the first light
            for (int pixel = 0; pixel < dividedLightsArray[light]; pixel++) // loop with every led
            {
              long pixelSum;
              for (int value = 0; value < light; value++)
              {
                if (value + 1 == light) {
                  pixelSum += dividedLightsArray[value] - transitionLeds;
                }
                else {
                  pixelSum += dividedLightsArray[value];
                }
              }

              if (pixel < transitionLeds / 2) { // leds in beginning of transition zone must apply blending
                strip->SetPixelColor(pixel + pixelSum + transitionLeds, blending( lights[light - 1].currentColors, lights[light].currentColors, pixel + 1));
              }
              else if (pixel > dividedLightsArray[light] - transitionLeds / 2 - 1) { // leds in the end of transition zone must apply blending
                //Serial.println(String(pixel));
                strip->SetPixelColor(pixel + pixelSum + transitionLeds, blending( lights[light].currentColors, lights[light + 1].currentColors, pixel + transitionLeds / 2 - dividedLightsArray[light]));
              }
              else  { // leds outside transition zone apply raw color
                strip->SetPixelColor(pixel + pixelSum + transitionLeds, convFloat(lights[light].currentColors));
              }
              pixelSum = 0;
            }
          }
        } else { // is just one virtual light declared, apply raw color to all leds
          strip->ClearTo(convFloat(lights[light].currentColors), 0, pixelCount - 1);
        }
        strip->Show();
      }
    }
  }
  cutPower(); // if all lights are off GPIO12 can cut the power to the strip using a powerful P-Channel MOSFET
  if (inTransition) { // wait 6ms for a nice transition effect
    delay(6);
    inTransition = false; // set inTransition bash to false (will be set bach to true on next level execution if desired state is not reached)
  } else {
    if (effect == 1) { // candle effect
        candleEffect();
      } else if (effect == 2) { // fireplace effect
        firePlaceEffect();
    }
    if (hwSwitch == true) { // if you want to use some GPIO's for on/off and brightness controll
      if (digitalRead(onPin) == LOW) { // on button pressed
        int i = 0;
        while (digitalRead(onPin) == LOW && i < 30) { // count how log is the button pressed
          delay(20);
          i++;
        }
        for (int light = 0; light < lightsCount; light++) {
          if (i < 30) { // there was a short press
            lights[light].lightState = true;
          }
          else { // there was a long press
            if (lights[light].bri < 198) {
              lights[light].bri += 56;
            } else {
              lights[light].bri = 254;
            }
            processLightdata(light);
          }
        }
      } else if (digitalRead(offPin) == LOW) { // off button pressed
        int i = 0;
        while (digitalRead(offPin) == LOW && i < 30) {
          delay(20);
          i++;
        }
        for (int light = 0; light < lightsCount; light++) {
          if (i < 30) {
            // there was a short press
            lights[light].lightState = false;
          }
          else {
            // there was a long press
            if (lights[light].bri > 57) {
              lights[light].bri -= 56;
            } else {
              lights[light].bri = 1;
            }
            processLightdata(light);
          }
        }
      }
    }
  }
}

void saveState() { // save the lights state on LittleFS partition in JSON format
  LOG_DEBUG("save state");
  DynamicJsonDocument json(1024);
  for (uint8_t i = 0; i < lightsCount; i++) {
    JsonObject light = json.createNestedObject((String)i);
    light["on"] = lights[i].lightState;
    light["bri"] = lights[i].bri;
    if (lights[i].colorMode == 1) {
      light["x"] = lights[i].x;
      light["y"] = lights[i].y;
    } else if (lights[i].colorMode == 2) {
      light["ct"] = lights[i].ct;
    } else if (lights[i].colorMode == 3) {
      light["hue"] = lights[i].hue;
      light["sat"] = lights[i].sat;
    }
  }
  File stateFile = LittleFS.open("/state.json", "w");
  serializeJson(json, stateFile);

}

void restoreState() { // restore the lights state from LittleFS partition
  LOG_DEBUG("restore state");
  File stateFile = LittleFS.open("/state.json", "r");
  if (!stateFile) {
    saveState();
    return;
  }

  DynamicJsonDocument json(1024);
  DeserializationError error = deserializeJson(json, stateFile.readString());
  if (error) {
    LOG_DEBUG("Failed to parse config file");
    return;
  }
  for (JsonPair state : json.as<JsonObject>()) {
    const char* key = state.key().c_str();
    int lightId = atoi(key);
    JsonObject values = state.value();
    lights[lightId].lightState = values["on"];
    lights[lightId].bri = (uint8_t)values["bri"];
    if (values.containsKey("x")) {
      lights[lightId].x = values["x"];
      lights[lightId].y = values["y"];
      lights[lightId].colorMode = 1;
    } else if (values.containsKey("ct")) {
      lights[lightId].ct = values["ct"];
      lights[lightId].colorMode = 2;
    } else {
      if (values.containsKey("hue")) {
        lights[lightId].hue = values["hue"];
        lights[lightId].colorMode = 3;
      }
      if (values.containsKey("sat")) {
        lights[lightId].sat = (uint8_t) values["sat"];
        lights[lightId].colorMode = 3;
      }
    }
  }
}


bool saveConfig() { // save config in LittleFS partition in JSON file
  DynamicJsonDocument json(1024);
  json["name"] = lightName;
  json["startup"] = startup;
  json["scene"] = scene;
  json["on"] = onPin;
  json["off"] = offPin;
  json["hw"] = hwSwitch;
  json["dhcp"] = useDhcp;
  json["lightsCount"] = lightsCount;
  for (uint16_t i = 0; i < lightsCount; i++) {
    json["dividedLight_" + String(i)] = dividedLightsArray[i];
  }
  json["pixelCount"] = pixelCount;
  json["transLeds"] = transitionLeds;
  json["rpct"] = rgb_multiplier[0];
  json["gpct"] = rgb_multiplier[1];
  json["bpct"] = rgb_multiplier[2];
  File configFile = LittleFS.open("/config.json", "w");
  if (!configFile) {
    LOG_DEBUG("Failed to open config file for writing");
    return false;
  }

  serializeJson(json, configFile);
  return true;
}

bool loadConfig() { // load the configuration from LittleFS partition
  LOG_DEBUG("loadConfig file");
  File configFile = LittleFS.open("/config.json", "r");
  if (!configFile) {
    LOG_DEBUG("Create new file with default values");
    return saveConfig();
  }

  size_t size = configFile.size();
  if (size > 1024) {
    LOG_DEBUG("Config file size is too large");
    return false;
  }

  DynamicJsonDocument json(1024);
  DeserializationError error = deserializeJson(json, configFile.readString());
  if (error) {
    LOG_DEBUG("Failed to parse config file");
    return false;
  }

  strcpy(lightName, json["name"]);
  startup = (uint8_t) json["startup"];
  scene  = (uint8_t) json["scene"];
  onPin = (uint8_t) json["on"];
  offPin = (uint8_t) json["off"];
  hwSwitch = json["hw"];
  lightsCount = (uint16_t) json["lightsCount"];
  for (uint16_t i = 0; i < lightsCount; i++) {
    dividedLightsArray[i] = (uint16_t) json["dividedLight_" + String(i)];
  }
  pixelCount = (uint16_t) json["pixelCount"];
  transitionLeds = (uint8_t) json["transLeds"];
  if (json.containsKey("rpct")) {
    rgb_multiplier[0] = (uint8_t) json["rpct"];
    rgb_multiplier[1] = (uint8_t) json["gpct"];
    rgb_multiplier[2] = (uint8_t) json["bpct"];
  }
  useDhcp = json["dhcp"];
  return true;
}

void ChangeNeoPixels(uint16_t newCount) // this set the number of leds of the strip based on web configuration
{
  if (strip != NULL) {
    delete strip; // delete the previous dynamically created strip
  }
  strip = new NeoPixelBus<NeoRgbFeature, NeoEsp32Rmt1Ws2812xMethod>(newCount, DATA_PIN); // and recreate with new count
  strip->Begin();
}

void ws_setup() {
  LOG_DEBUG("Setup WS2811");
  //pinMode(POWER_MOSFET_PIN, OUTPUT);
  blinkLed(2);
  //digitalWrite(POWER_MOSFET_PIN, HIGH); mosftetState = true; // reuired if HIGH logic power the strip, otherwise must be commented.

  /*if (!LittleFS.begin()) {
    LOG_DEBUG("Failed to mount file system");
    //Serial.println("Failed to mount file system");
    LittleFS.format();
    }*/

  if (!loadConfig()) {
    LOG_DEBUG("Failed to load config");
  } else {
    LOG_DEBUG("Config loaded");
  }

  dividedLightsArray[lightsCount];
  if (dividedLightsArray[0] == 0) {
    for (uint8_t light = 0; light < lightsCount; light++) {
      dividedLightsArray[light] = pixelCount / lightsCount;
    }
    saveConfig();
  }

  ChangeNeoPixels(pixelCount);

  if (startup == 1) {
    for (uint8_t i = 0; i < lightsCount; i++) {
      lights[i].lightState = true;
    }
  }
  if (startup == 0) {
    restoreState();
  } else {
    apply_scene_ws(scene);
  }
  for (uint8_t i = 0; i < lightsCount; i++) {
    processLightdata(i);
  }
  if (lights[0].lightState) {
    for (uint8_t i = 0; i < 200; i++) {
      lightEngine();
    }
  }

  Udp.begin(2100); // start entertainment UDP server

  server_ws.on("/state", HTTP_PUT, []() { // HTTP PUT request used to set a new light state
    bool stateSave = false;
    DynamicJsonDocument root(1024);
    DeserializationError error = deserializeJson(root, server_ws.arg("plain"));

    if (error) {
      server_ws.send(404, "text/plain", "FAIL. " + server_ws.arg("plain"));
    } else {
      for (JsonPair state : root.as<JsonObject>()) {
        const char* key = state.key().c_str();
        int light = atoi(key) - 1;
        JsonObject values = state.value();
        int transitiontime = 4;

        if (values.containsKey("effect")) {
          if (values["effect"] == "no_effect") {
            effect = 0;
          } else if (values["effect"] == "candle") {
            effect = 1;
          } else if (values["effect"] == "fire") {
            effect = 2;
          }
        }

        if (values.containsKey("xy")) {
          lights[light].x = values["xy"][0];
          lights[light].y = values["xy"][1];
          lights[light].colorMode = 1;
        } else if (values.containsKey("ct")) {
          lights[light].ct = values["ct"];
          lights[light].colorMode = 2;
        } else {
          if (values.containsKey("hue")) {
            lights[light].hue = values["hue"];
            lights[light].colorMode = 3;
          }
          if (values.containsKey("sat")) {
            lights[light].sat = values["sat"];
            lights[light].colorMode = 3;
          }
        }

        if (values.containsKey("on")) {
          if (values["on"]) {
            lights[light].lightState = true;
          } else {
            lights[light].lightState = false;
          }
          if (startup == 0) {
            stateSave = true;
          }
        }

        if (values.containsKey("bri")) {
          lights[light].bri = values["bri"];
        }

        if (values.containsKey("bri_inc")) {
          if (values["bri_inc"] > 0) {
            if (lights[light].bri + (int) values["bri_inc"] > 254) {
              lights[light].bri = 254;
            } else {
              lights[light].bri += (int) values["bri_inc"];
            }
          } else {
            if (lights[light].bri - (int) values["bri_inc"] < 1) {
              lights[light].bri = 1;
            } else {
              lights[light].bri += (int) values["bri_inc"];
            }
          }
        }

        if (values.containsKey("transitiontime")) {
          transitiontime = values["transitiontime"];
        }

        if (values.containsKey("alert") && values["alert"] == "select") {
          if (lights[light].lightState) {
            lights[light].currentColors[0] = 0; lights[light].currentColors[1] = 0; lights[light].currentColors[2] = 0;
          } else {
            lights[light].currentColors[1] = 126; lights[light].currentColors[2] = 126;
          }
        }
        processLightdata(light, transitiontime);
      }
      String output;
      serializeJson(root, output);
      server_ws.send(200, "text/plain", output);
      if (stateSave) {
        saveState();
      }
    }
  });

  server_ws.on("/state", HTTP_GET, []() { // HTTP GET request used to fetch current light state
    uint8_t light = server_ws.arg("light").toInt() - 1;
    DynamicJsonDocument root(1024);
    root["on"] = lights[light].lightState;
    root["bri"] = lights[light].bri;
    JsonArray xy = root.createNestedArray("xy");
    xy.add(lights[light].x);
    xy.add(lights[light].y);
    root["ct"] = lights[light].ct;
    root["hue"] = lights[light].hue;
    root["sat"] = lights[light].sat;
    if (lights[light].colorMode == 1)
      root["colormode"] = "xy";
    else if (lights[light].colorMode == 2)
      root["colormode"] = "ct";
    else if (lights[light].colorMode == 3)
      root["colormode"] = "hs";
    String output;
    serializeJson(root, output);
    server_ws.send(200, "text/plain", output);
  });

  server_ws.on("/detect", []() { // HTTP GET request used to discover the light type
    char macString[32] = {0};
    sprintf(macString, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    DynamicJsonDocument root(1024);
    root["name"] = lightName;
    root["lights"] = lightsCount;
    root["protocol"] = "native_multi";
    root["modelid"] = "LST002";
    root["type"] = "ws2812_strip";
    root["mac"] = String(macString);
    root["version"] = LIGHT_VERSION;
    String output;
    serializeJson(root, output);
    server_ws.send(200, "text/plain", output);
  });

  server_ws.on("/config", []() { // used by light web interface to get current configuration
    DynamicJsonDocument root(1024);
    root["name"] = lightName;
    root["scene"] = scene;
    root["startup"] = startup;
    root["hw"] = hwSwitch;
    root["on"] = onPin;
    root["off"] = offPin;
    root["hwswitch"] = (int)hwSwitch;
    root["lightscount"] = lightsCount;
    for (uint8_t i = 0; i < lightsCount; i++) {
      root["dividedLight_" + String(i)] = (int)dividedLightsArray[i];
    }
    root["pixelcount"] = pixelCount;
    root["transitionleds"] = transitionLeds;
    root["rpct"] = rgb_multiplier[0];
    root["gpct"] = rgb_multiplier[1];
    root["bpct"] = rgb_multiplier[2];
    root["disdhcp"] = (int)!useDhcp;
    String output;
    serializeJson(root, output);
    server_ws.send(200, "text/plain", output);
  });

  server_ws.on("/", []() { // light http web interface
    if (server_ws.arg("section").toInt() == 1) {
      server_ws.arg("name").toCharArray(lightName, LIGHT_NAME_MAX_LENGTH);
      startup = server_ws.arg("startup").toInt();
      scene = server_ws.arg("scene").toInt();
      lightsCount = server_ws.arg("lightscount").toInt();
      pixelCount = server_ws.arg("pixelcount").toInt();
      transitionLeds = server_ws.arg("transitionleds").toInt();
      rgb_multiplier[0] = server_ws.arg("rpct").toInt();
      rgb_multiplier[1] = server_ws.arg("gpct").toInt();
      rgb_multiplier[2] = server_ws.arg("bpct").toInt();
      for (uint16_t i = 0; i < lightsCount; i++) {
        dividedLightsArray[i] = server_ws.arg("dividedLight_" + String(i)).toInt();
      }
      hwSwitch = server_ws.hasArg("hwswitch") ? server_ws.arg("hwswitch").toInt() : 0;
      if (server_ws.hasArg("hwswitch")) {
        onPin = server_ws.arg("on").toInt();
        offPin = server_ws.arg("off").toInt();
      }
      saveConfig();
    } else if (server_ws.arg("section").toInt() == 2) {
      useDhcp = (!server_ws.hasArg("disdhcp")) ? 1 : server_ws.arg("disdhcp").toInt();
      saveConfig();
    }

    String htmlContent = "<!DOCTYPE html> <html> <head> <meta charset=\"UTF-8\"> <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> <title>" + String(lightName) + " - DiyHue</title> <link rel=\"icon\" type=\"image/png\" href=\"https://diyhue.org/wp-content/uploads/2019/11/cropped-Zeichenfl%C3%A4che-4-1-32x32.png\" sizes=\"32x32\"> <link href=\"https://fonts.googleapis.com/icon?family=Material+Icons\" rel=\"stylesheet\"> <link rel=\"stylesheet\" href=\"https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css\"> <link rel=\"stylesheet\" href=\"https://diyhue.org/cdn/nouislider.css\" /> </head> <body> <div class=\"wrapper\"> <nav class=\"nav-extended row\" style=\"background-color: #26a69a !important;\"> <div class=\"nav-wrapper col s12\"> <a href=\"#\" class=\"brand-logo\">DiyHue</a> <ul id=\"nav-mobile\" class=\"right hide-on-med-and-down\" style=\"position: relative;z-index: 10;\"> <li><a target=\"_blank\" href=\"https://github.com/diyhue\"><i class=\"material-icons left\">language</i>GitHub</a></li> <li><a target=\"_blank\" href=\"https://diyhue.readthedocs.io/en/latest/\"><i class=\"material-icons left\">description</i>Documentation</a></li> <li><a target=\"_blank\" href=\"https://diyhue.slack.com/\"><i class=\"material-icons left\">question_answer</i>Slack channel</a></li> </ul> </div> <div class=\"nav-content\"> <ul class=\"tabs tabs-transparent\"> <li class=\"tab\" title=\"#home\"><a class=\"active\" href=\"#home\">Home</a></li> <li class=\"tab\" title=\"#preferences\"><a href=\"#preferences\">Preferences</a></li> <li class=\"tab\" title=\"#network\"><a href=\"#network\">Network settings</a></li> <li class=\"tab\" title=\"/update\"><a href=\"/update\">Updater</a></li> </ul> </div> </nav> <ul class=\"sidenav\" id=\"mobile-demo\"> <li><a target=\"_blank\" href=\"https://github.com/diyhue\">GitHub</a></li> <li><a target=\"_blank\" href=\"https://diyhue.readthedocs.io/en/latest/\">Documentation</a></li> <li><a target=\"_blank\" href=\"https://diyhue.slack.com/\">Slack channel</a></li> </ul> <div class=\"container\"> <div class=\"section\"> <div id=\"home\" class=\"col s12\"> <form> <input type=\"hidden\" name=\"section\" value=\"1\"> <div class=\"row\"> <div class=\"col s10\"> <label for=\"power\">Power</label> <div id=\"power\" class=\"switch section\"> <label> Off <input type=\"checkbox\" name=\"pow\" id=\"pow\" value=\"1\"> <span class=\"lever\"></span> On </label> </div> </div> </div> <div class=\"row\"> <div class=\"col s12 m10\"> <label for=\"bri\">Brightness</label> <input type=\"text\" id=\"bri\" class=\"js-range-slider\" name=\"bri\" value=\"\" /> </div> </div> <div class=\"row\"> <div class=\"col s12\"> <label for=\"hue\">Color</label> <div> <canvas id=\"hue\" width=\"320px\" height=\"320px\" style=\"border:1px solid #d3d3d3;\"></canvas> </div> </div> </div> <div class=\"row\"> <div class=\"col s12\"> <label for=\"ct\">Color Temp</label> <div> <canvas id=\"ct\" width=\"320px\" height=\"50px\" style=\"border:1px solid #d3d3d3;\"></canvas> </div> </div> </div> </form> </div> <div id=\"preferences\" class=\"col s12\"> <form method=\"POST\" action=\"/\"> <input type=\"hidden\" name=\"section\" value=\"1\"> <div class=\"row\"> <div class=\"col s12\"> <label for=\"name\">Light Name</label> <input type=\"text\" id=\"name\" name=\"name\"> </div> </div> <div class=\"row\"> <div class=\"col s12 m6\"> <label for=\"startup\">Default Power:</label> <select name=\"startup\" id=\"startup\"> <option value=\"0\">Last State</option> <option value=\"1\">On</option> <option value=\"2\">Off</option> </select> </div> </div> <div class=\"row\"> <div class=\"col s12 m6\"> <label for=\"scene\">Default Scene:</label> <select name=\"scene\" id=\"scene\"> <option value=\"0\">Relax</option> <option value=\"1\">Read</option> <option value=\"2\">Concentrate</option> <option value=\"3\">Energize</option> <option value=\"4\">Bright</option> <option value=\"5\">Dimmed</option> <option value=\"6\">Nightlight</option> <option value=\"7\">Savanna sunset</option> <option value=\"8\">Tropical twilight</option> <option value=\"9\">Arctic aurora</option> <option value=\"10\">Spring blossom</option> </select> </div> </div> <div class=\"row\"> <div class=\"col s4 m3\"> <label for=\"pixelcount\" class=\"col-form-label\">Pixel count</label> <input type=\"number\" id=\"pixelcount\" name=\"pixelcount\"> </div> </div> <div class=\"row\"> <div class=\"col s4 m3\"> <label for=\"lightscount\" class=\"col-form-label\">Lights count</label> <input type=\"number\" id=\"lightscount\" name=\"lightscount\"> </div> </div> <label class=\"form-label\">Light division</label> </br> <label>Available Pixels:</label> <label class=\"availablepixels\"><b>null</b></label> <div class=\"row dividedLights\"> </div> <div class=\"row\"> <div class=\"col s4 m3\"> <label for=\"transitionleds\">Transition leds:</label> <select name=\"transitionleds\" id=\"transitionleds\"> <option value=\"0\">0</option> <option value=\"2\">2</option> <option value=\"4\">4</option> <option value=\"6\">6</option> <option value=\"8\">8</option> <option value=\"10\">10</option> </select> </div> </div> <div class=\"row\"> <div class=\"col s4 m3\"> <label for=\"rpct\" class=\"form-label\">Red multiplier</label> <input type=\"number\" id=\"rpct\" class=\"js-range-slider\" data-skin=\"round\" name=\"rpct\" value=\"\" /> </div> <div class=\"col s4 m3\"> <label for=\"gpct\" class=\"form-label\">Green multiplier</label> <input type=\"number\" id=\"gpct\" class=\"js-range-slider\" data-skin=\"round\" name=\"gpct\" value=\"\" /> </div> <div class=\"col s4 m3\"> <label for=\"bpct\" class=\"form-label\">Blue multiplier</label> <input type=\"number\" id=\"bpct\" class=\"js-range-slider\" data-skin=\"round\" name=\"bpct\" value=\"\" /> </div> </div> <div class=\"row\"> <label class=\"control-label col s10\">HW buttons:</label> <div class=\"col s10\"> <div class=\"switch section\"> <label> Disable <input type=\"checkbox\" name=\"hwswitch\" id=\"hwswitch\" value=\"1\"> <span class=\"lever\"></span> Enable </label> </div> </div> </div> <div class=\"switchable\"> <div class=\"row\"> <div class=\"col s4 m3\"> <label for=\"on\">On Pin</label> <input type=\"number\" id=\"on\" name=\"on\"> </div> <div class=\"col s4 m3\"> <label for=\"off\">Off Pin</label> <input type=\"number\" id=\"off\" name=\"off\"> </div> </div> </div> <div class=\"row\"> <div class=\"col s10\"> <button type=\"submit\" class=\"waves-effect waves-light btn teal\">Save</button> <!--<button type=\"submit\" name=\"reboot\" class=\"waves-effect waves-light btn grey lighten-1\">Reboot</button>--> </div> </div> </form> </div> <div id=\"network\" class=\"col s12\"> <form method=\"POST\" action=\"/\"> <input type=\"hidden\" name=\"section\" value=\"2\"> <div class=\"row\"> <div class=\"col s12\"> <label class=\"control-label\">Manual IP assignment:</label> <div class=\"switch section\"> <label> Disable <input type=\"checkbox\" name=\"disdhcp\" id=\"disdhcp\" value=\"0\"> <span class=\"lever\"></span> Enable </label> </div> </div> </div> <div class=\"switchable\"> <div class=\"row\"> <div class=\"col s12 m3\"> <label for=\"addr\">Ip</label> <input type=\"text\" id=\"addr\" name=\"addr\"> </div> <div class=\"col s12 m3\"> <label for=\"sm\">Submask</label> <input type=\"text\" id=\"sm\" name=\"sm\"> </div> <div class=\"col s12 m3\"> <label for=\"gw\">Gateway</label> <input type=\"text\" id=\"gw\" name=\"gw\"> </div> </div> </div> <div class=\"row\"> <div class=\"col s10\"> <button type=\"submit\" class=\"waves-effect waves-light btn teal\">Save</button> <!--<button type=\"submit\" name=\"reboot\" class=\"waves-effect waves-light btn grey lighten-1\">Reboot</button>--> <!--<button type=\"submit\" name=\"reboot\" class=\"waves-effect waves-light btn grey lighten-1\">Reboot</button>--> </div> </div> </form> </div> </div> </div> </div> <script src=\"https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js\"></script> <script src=\"https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js\"></script> <script src=\"https://diyhue.org/cdn/nouislider.js\"></script> <script src=\"https://diyhue.org/cdn/diyhue.js\"></script> </body> </html>";

    server_ws.send(200, "text/html", htmlContent);
    if (server_ws.args()) {
      delay(1000); // needs to wait until response is received by browser. If ESP restarts too soon, browser will think there was an error.
      ESP.restart();
    }

  });

  server_ws.on("/reset", []() { // trigger manual reset
    server_ws.send(200, "text/html", "reset");
    delay(1000);
    ESP.restart();
  });

  server_ws.onNotFound(handleNotFound_ws);

  server_ws.begin();

  httpUpdateServer.setup(&server_ws); // start http server

}

RgbColor blendingEntert(float left[3], float right[3], float pixel) {
  uint8_t result[3];
  for (uint8_t i = 0; i < 3; i++) {
    float percent = (float) pixel / (float) (transitionLeds + 1);
    result[i] = (left[i] * (1.0f - percent) + right[i] * percent) / 2;
  }
  return RgbColor((uint8_t)result[0], (uint8_t)result[1], (uint8_t)result[2]);
}

void entertainment() { // entertainment function
  uint8_t packetSize = Udp.parsePacket(); // check if UDP received some bytes
  if (packetSize) { // if nr of bytes is more than zero
    if (!entertainmentRun) { // announce entertainment is running
      entertainmentRun = true;
    }
    lastEPMillis = millis(); // update variable with last received package timestamp
    Udp.read(packetBuffer, packetSize);
    for (uint8_t i = 0; i < packetSize / 4; i++) { // loop with every light. There are 4 bytes for every light (light number, red, green, blue)
      lights[packetBuffer[i * 4]].currentColors[0] = packetBuffer[i * 4 + 1] * rgb_multiplier[0] / 100;
      lights[packetBuffer[i * 4]].currentColors[1] = packetBuffer[i * 4 + 2] * rgb_multiplier[1] / 100;
      lights[packetBuffer[i * 4]].currentColors[2] = packetBuffer[i * 4 + 3] * rgb_multiplier[2] / 100;
    }
    for (uint8_t light = 0; light < lightsCount; light++) {
      if (lightsCount > 1) {
        if (light == 0) {
          for (int pixel = 0; pixel < dividedLightsArray[0]; pixel++)
          {
            if (pixel < dividedLightsArray[0] - transitionLeds / 2) {
              strip->SetPixelColor(pixel, convFloat(lights[light].currentColors));
            } else {
              strip->SetPixelColor(pixel, blendingEntert(lights[0].currentColors, lights[1].currentColors, pixel + 1 - (dividedLightsArray[0] - transitionLeds / 2 )));
            }
          }
        }
        else {
          for (int pixel = 0; pixel < dividedLightsArray[light]; pixel++)
          {
            long pixelSum;
            for (int value = 0; value < light; value++)
            {
              if (value + 1 == light) {
                pixelSum += dividedLightsArray[value] - transitionLeds;
              }
              else {
                pixelSum += dividedLightsArray[value];
              }
            }
            if (pixel < transitionLeds / 2) {
              strip->SetPixelColor(pixel + pixelSum + transitionLeds, blendingEntert( lights[light - 1].currentColors, lights[light].currentColors, pixel + 1));
            }
            else if (pixel > dividedLightsArray[light] - transitionLeds / 2 - 1) {
              //Serial.println(String(pixel));
              strip->SetPixelColor(pixel + pixelSum + transitionLeds, blendingEntert( lights[light].currentColors, lights[light + 1].currentColors, pixel + transitionLeds / 2 - dividedLightsArray[light]));
            }
            else  {
              strip->SetPixelColor(pixel + pixelSum + transitionLeds, convFloat(lights[light].currentColors));
            }
            pixelSum = 0;
          }
        }
      } else {
        strip->ClearTo(convFloat(lights[light].currentColors), 0, pixelCount - 1);
      }
    }
    strip->Show();
  }
}


void ws_loop() {
  server_ws.handleClient();
  if (!entertainmentRun) {
    lightEngine(); // process lights data set on http server
  } else {
    if ((millis() - lastEPMillis) >= ENTERTAINMENT_TIMEOUT) { // entertainment stream stop (timeout)
      entertainmentRun = false;
      for (uint8_t i = 0; i < lightsCount; i++) {
        processLightdata(i); //return to original colors with 0.4 sec transition
      }
    }
  }
  entertainment(); // process entertainment data on UDP server
}


String sendHttpRequest(int button, String mac, IPAddress bridgeIp) {
  String msg = "";
  int val = true;

  while (val) {
    if (!client.connect(bridgeIp, 80)) {
      //LOG_ERROR("Connection failed");
      return "Connection failed";
    }
    LOG_INFO("Connected!");
    LOG_DEBUG("msg:", msg);
    String url = "/switch";
    //url += "?mac=";
    //url += mac;

    if (msg == "device not found" || msg == "no mac in list") {
      //url = "/switch";
      url += "?devicetype=";
      if (button >= 1000) {
        url += (String)switchType;
      } else {
        url += (String)motionType;
      }
      url += "&mac=";
      url += mac;
    } else if (msg == "command applied") {
      client.stop();
      val = false;
      return msg;
    } else if (msg == "unknown device" || msg == "missing mac address") {
      client.stop();
      val = false;
      return msg;
    } else {
      int batteryPercent = 100;
      //url = "/switch?mac=";
      url += "?mac=";
      url += mac;
      url += "&button=";
      url += button;
      url += "&presence=true";
      url += "&battery=";
      url += batteryPercent;
    }
    LOG_DEBUG("url:", url);

    String message = String("GET ");
    message += url;
    message += " HTTP/1.1\r\n";
    message += "Host: ";
    message += bridgeIp;
    message += "\r\n";
    message += "Connection: close\r\n\r\n";

    client.println(message);


    if (client.println() == 0) {
      //LOG_ERROR("Failed to send request");
      client.stop();
      return "Failed to send request";
    }

    // Check HTTP status
    char status[32] = {0};
    client.readBytesUntil('\r', status, sizeof(status));
    if (strcmp(status, "HTTP/1.1 200 OK") != 0) {
      //LOG_ERROR("Unexpected response:", status);
      client.stop();
      return "Unexpected response: ";
    }

    // Skip HTTP headers
    char endOfHeaders[] = "\r\n\r\n";
    if (!client.find(endOfHeaders)) {
      //LOG_ERROR("Invalid response");
      client.stop();
      return "Invalid response";
    }

    // Allocate the JSON document
    // Use arduinojson.org/v6/assistant to compute the capacity.
    const size_t capacity = JSON_OBJECT_SIZE(3) + JSON_ARRAY_SIZE(2) + 60;
    DynamicJsonDocument doc(capacity);

    // Parse JSON object
    DeserializationError error = deserializeJson(doc, client);
    if (error) {
      //LOG_ERROR("deserializeJson() failed:", error.f_str());
      client.stop();
      return "deserializeJson() failed: ";
    }
    JsonObject obj = doc.as<JsonObject>();
    if (obj.containsKey("success")) {
      msg = doc["success"].as<String>();
    }
    if (obj.containsKey("fail")) {
      msg = doc["fail"].as<String>();
    }
  }
  client.stop();
  return msg;
}



void mesh_setup() {
  //mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | SYNC | COMMUNICATION | GENERAL | MSG_TYPES | REMOTE | DEBUG ); // all types on
  //mesh.setDebugMsgTypes( ERROR | CONNECTION | SYNC | S_TIME );  // set before init() so that you can see startup messages
  //mesh.setDebugMsgTypes( ERROR | CONNECTION | S_TIME );  // set before init() so that you can see startup messages
  mesh.setDebugMsgTypes( ERROR | MESH_STATUS | CONNECTION | COMMUNICATION );
  //mesh.init(MESH_PREFIX, MESH_PASSWORD, MESH_PORT);
  mesh.init (MESH_PREFIX, MESH_PASSWORD, MESH_PORT, connectMode, hidden);
  mesh.onReceive(&receivedCallback);
  mesh.onNewConnection(&newConnectionCallback);
  newConnectionCallback(0);
  
  server_gordijn.on(F("/"), handleRoot);
  server_gordijn.on("/setTargetPosTest/", set_Target_Pos_test);
  server_gordijn.on("/CurrentPosTest", get_current_pos_test);
  server_gordijn.on("/getTargetPosTest", get_target_pos_test);
  server_gordijn.on("/StateTest", get_state_test);
  server_gordijn.on("/Home", homeing);
  server_gordijn.on("/setTargetPos/", set_Target_Pos);
  server_gordijn.on("/CurrentPos", get_current_pos);
  server_gordijn.on("/getTargetPos", get_target_pos);
  server_gordijn.on("/State", get_state);

  server_gordijn.on("/info", handleinfo);
  
  server_gordijn.on("/reset", []() {
    server_gordijn.send(200, "text/html", "reset");
    digitalWrite(RES, HIGH);
    delay(1000);
    ESP.restart();
  });

  server_gordijn.onNotFound(handleNotFound);

  server_gordijn.begin();

  server_mesh.on(F("/"), mesh_handleRoot);
  server_mesh.on("/setIP/", set_IP);
  server_mesh.onNotFound(mesh_handleNotFound);
  server_mesh.begin();

}

void mesh_loop() {
  server_gordijn.handleClient();
  server_mesh.handleClient();
  mesh.update();
  send_change();
}

void send_change() {
  if (change == true) {
    LOG_DEBUG("value:", value);
    LOG_DEBUG("room_mac:", room_mac);
    LOG_ERROR(sendHttpRequest(value, room_mac, bridgeIp));
    change = false;
  }
}

void newConnectionCallback(uint32_t nodeId) {

  DynamicJsonDocument doc(260);
  doc["master"] = uint32_t(mesh.getNodeId());
  String msg;
  serializeJson(doc, msg);

  LOG_DEBUG("newConnection nodeId:", nodeId);
  LOG_DEBUG("newConnection msg:", msg);

  if (nodeId > 0) {
    mesh.sendSingle(nodeId, msg);
  } else {
    mesh.sendBroadcast(msg);
  }
}

void receivedCallback( uint32_t from, String &msg ) {
  DynamicJsonDocument root(1024);
  DeserializationError error = deserializeJson(root, msg);

  if (error) {
    LOG_ERROR("deserializeJson() failed:", error.f_str());
    return;
  }
  LOG_DEBUG("nodeId:", from);
  LOG_DEBUG("msg:", msg);
  if (bool(root["got_master"]) == true) {
    if (root["device"] == "switch") {
      room_mac = (const char*)root["room_mac"];
      value = (int)root["value"];
      change = true;
    }
    if(root["device"] == "curtain"){
      curtain_id = uint32_t(root["curtain_id"]);
      target_ont = (int)root["target"];
      current_ont = (int)root["current"];
      state_ont = (int)root["state"];
    }
  } else {
    if(root["device"] == "curtain"){
      curtain_id = uint32_t(root["curtain_id"]);
    }
    newConnectionCallback(from);
  }
}

void handleRoot() {
  String message = "<!DOCTYPE HTML>";
  message += "<html>";
  message += "<h1 align=center>Curtain control over ethernet+mesh</h1><br><br>";
  message += "set Target Pos  = ";
  message += target;
  message += "<br>";
  message += "rep Target Pos  = ";
  message += target_ont;
  message += "<br>";
  message += "rep Current Pos  = ";
  message += current_ont;
  message += "<br>";
  message += "rep State  = ";
  message += state_ont;
  message += "<br>";
  message += "rep Home  = ";
  message += ishome;
  message += "<br>";
  message += "error  = ";
  message += fout;
  message += "<br><br>";


  message += "<form action=\"/setTargetPosTest/\">";
  message += "SET Target";
  message += "<input type=\"range\" name=\"Pos\" min=\"0\" max=\"100\" value=\"" + (String)target + "\" step=\"1\" class=\"slider\">";
  //message += "<input type=\"text\"  name=\"Pos\" value=\"" + (String)target + "\">";
  message += "<input type=\"submit\" value=\"Submit\">";
  message += "</form>";
  message += "Current Target  = ";
  message += target;

  //message += "<a href=\"//setTargetPosTEST\"\"><button>SET Target Pos TEST</button></a>"; //aanpassen voor invullen

  message += "<br><br>";


  message += "<a href=\"/CurrentPosTest\"\"><button>GET Current Pos TEST</button></a>";
  message += "<a href=\"/getTargetPosTest\"\"><button>GET Target Pos TEST</button></a>";
  message += "<a href=\"/StateTest\"\"><button>GET State TEST</button></a>";

  message += "<a href=\"/Home\"\"><button>Home curtain</button></a>";

  message += "<br><br>";
  message += "Links voor Homebridge";
  message += "<br><br>";

  message += "<a href=\"/setTargetPos/?Pos=50\"\"><button>SET Target Pos 50%</button></a>";
  message += "<a href=\"/CurrentPos\"\"><button>GET Current Pos</button></a>";
  message += "<a href=\"/getTargetPos\"\"><button>GET Target Pos</button></a>";
  message += "<a href=\"/State\"\"><button>GET State</button></a>";

  message += "<br><br>";
  message += "<a href=\"/info\"\"><button>Info</button></a>";
  message += "<a href=\"/\"\"><button>RELOAD PAGE</button></a><br/>";
  message += "<br><br>";
  message += "<a href=\"/reset\"\"><button>RESET</button></a><br/>";

  message += "</html>";
  server_gordijn.send(200, "text/html", message);
}

void sendData(String msg){
  if(curtain_id > 0){
    mesh.sendSingle(curtain_id, msg);
  }else{
    mesh.sendBroadcast(msg);
  }
}

void set_Target_Pos_test() {
  for (uint8_t i = 0; i < server_gordijn.args(); i++) {
    if (server_gordijn.argName(i) == F("Pos")) {
      target = server_gordijn.arg(i).toInt();
    }
  }
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = false;
  doc["request"] = true;
  doc["target"] = target;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.sendHeader("Location", "/", true); //Redirect to our html web page
  server_gordijn.send(302, "text/plane", "");
}

void set_Target_Pos() {
  for (uint8_t i = 0; i < server_gordijn.args(); i++) {
    if (server_gordijn.argName(i) == F("Pos")) {
      target = server_gordijn.arg(i).toInt();
    }
  }
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = false;
  doc["request"] = true;
  doc["target"] = target;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.send(200, F("text/plain"),   F("OK"));
}

void homeing() {
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = true;
  doc["request"] = false;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.sendHeader("Location", "/", true); //Redirect to our html web page
  server_gordijn.send(302, "text/plane", "");
}

void get_current_pos_test() {
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = false;
  doc["request"] = true;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.sendHeader("Location", "/", true); //Redirect to our html web page
  server_gordijn.send(302, "text/plane", "");
}

void get_current_pos() {
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = false;
  doc["request"] = true;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.send(200, F("text/plain"),   (String)current_ont  );
}

void get_target_pos_test() {
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = false;
  doc["request"] = true;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.sendHeader("Location", "/", true); //Redirect to our html web page
  server_gordijn.send(302, "text/plane", "");
}

void get_target_pos() {
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = false;
  doc["request"] = true;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.send(200, F("text/plain"),   (String)target_ont  );
}

void get_state_test() {
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = false;
  doc["request"] = true;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.sendHeader("Location", "/", true); //Redirect to our html web page
  server_gordijn.send(302, "text/plane", "");
}

void get_state() {
  DynamicJsonDocument doc(260);
  doc["device"] = "curtain";
  doc["homing"] = false;
  doc["request"] = true;
  String msg;
  serializeJson(doc, msg);
  sendData(msg);
  server_gordijn.send(200, F("text/plain"),   (String)state_ont  );
}

void handleinfo() {


  float totaal_step = totalrond * MOTOR_STEPS * MICROSTEPS;
  float microspeed = motorSpeed * MICROSTEPS;
  float microacc = motorAcc * MICROSTEPS;
  float acc_tijd = microspeed / microacc;
  float acc_step = 0.5 * microacc * pow(acc_tijd, 2);
  float deccel_tijd = microspeed / microacc;
  float deccel_step = 0.5 * microacc * pow(deccel_tijd, 2);
  float cruise_step = totaal_step - acc_step - deccel_step;
  float cruise_tijd = cruise_step / microspeed;
  float totaal_tijd = cruise_tijd + deccel_tijd + acc_tijd;

  String message = "<!DOCTYPE HTML>";
  message += "<html>";
  message += "info<br><br>";
  message += "IP: ";
  message += WiFi.localIP().toString();
  message += "<br>motor steps per omwenteling: ";
  message += MOTOR_STEPS;
  message += "<br>motor snelheid: ";
  message += motorSpeed;
  message += "<br>motor acceleratie: ";
  message += motorAcc;
  message += "<br>microstep: ";
  message += MICROSTEPS;
  message += "<br>aantal rondjes: ";
  message += totalrond;
  message += "<br>DIR pin: ";
  message += DIR;
  message += "<br>STEP pin: ";
  message += STEP;
  message += "<br>ENABLE pin: ";
  message += ENABLE;
  message += "<br>Driver Adress: ";
  message += DRIVER_ADDRESS;
  message += "<br>R_SENSE: ";
  message += R_SENSE;
  message += "<br>SW_RX pin: ";
  message += SW_RX;
  message += "<br>SW_TX pin: ";
  message += SW_TX;
  message += "<br>home_switch pin: ";
  message += home_switch;
  message += "<br>";

  message += "<br>ESP_SW_RX pin: ";
  message += ESP_SW_RX;
  message += "<br>ESP_SW_TX pin: ";
  message += ESP_SW_TX;
  message += "<br>";

  message += "<br>DEBUG: ";
  message += DEBUG;
  message += "<br>";

  message += "<br>totaal tijd : ";
  message += totaal_tijd;
  message += "<br><br>";
  message += "<a href=\"/\"\"><button>HOME PAGE</button></a><br/>";
  server_gordijn.send(200, "text/html", message);
}

void handleNotFound() {
  String message = "<!DOCTYPE HTML>";
  message = "File Not Found<br><br>";
  message += "URI: ";
  message += server_gordijn.uri();
  message += "<br>Method: ";
  message += (server_gordijn.method() == HTTP_GET) ? "GET" : "POST";
  message += "<br>Arguments: ";
  message += server_gordijn.args();
  message += "<br>";
  for (uint8_t i = 0; i < server_gordijn.args(); i++) {
    message += " " + server_gordijn.argName(i) + ": " + server_gordijn.arg(i) + "\n";
  }
  message += "<br><br>";
  message += "<a href=\"/\"\"><button>HOME PAGE</button></a><br/>";
  server_gordijn.send(404, "text/html", message);
}

void mesh_handleNotFound() {
  String message = "<!DOCTYPE HTML>";
  message = "File Not Found<br><br>";
  message += "URI: ";
  message += server_mesh.uri();
  message += "<br>Method: ";
  message += (server_mesh.method() == HTTP_GET) ? "GET" : "POST";
  message += "<br>Arguments: ";
  message += server_mesh.args();
  message += "<br>";
  for (uint8_t i = 0; i < server_mesh.args(); i++) {
    message += " " + server_mesh.argName(i) + ": " + server_mesh.arg(i) + "\n";
  }
  message += "<br><br>";
  message += "<a href=\"/\"\"><button>HOME PAGE</button></a><br/>";
  server_mesh.send(404, "text/html", message);
}

void mesh_handleRoot() {
  String message = "<!DOCTYPE HTML>";
  message += "<html>";
  message += "<h1 align=center>Set IP for mesh command</h1><br><br>";


  message += "<form action=\"/setIP/\">";
  message += "SET IP";
  message += "<input type=\"text\"  name=\"subip\" value=\"" + (String)subip + "\">";
  message += "<input type=\"submit\" value=\"Submit\">";
  message += "</form>";
  message += "Current IP = ";
  message += "192.168.1." + (String)subip;

  message += "<br><br>";
  message += "<a href=\"/\"\"><button>RELOAD PAGE</button></a><br/>";

  message += "</html>";
  server_mesh.send(200, "text/html", message);
}

void set_IP() {
  for (uint8_t i = 0; i < server_mesh.args(); i++) {
    if (server_mesh.argName(i) == F("subip")) {
      subip = server_mesh.arg(i).toInt();
    }
  }
  bridgeIp = IPAddress(192, 168, 1, subip);
  server_mesh.sendHeader("Location", "/", true); //Redirect to our html web page
  server_mesh.send(302, "text/plane", "");
}


void handleNotFound_i2c() {
  String message = "File Not Found\n\n";
  message += "URI: ";
  message += server_i2c.uri();
  message += "\nMethod: ";
  message += (server_i2c.method() == HTTP_GET) ? "GET" : "POST";
  message += "\nArguments: ";
  message += server_i2c.args();
  message += "\n";
  for (uint8_t i = 0; i < server_i2c.args(); i++) {
    message += " " + server_i2c.argName(i) + ": " + server_i2c.arg(i) + "\n";
  }
  server_i2c.send(404, "text/plain", message);
}


void apply_scene_i2c(uint8_t new_scene,  uint8_t light) {
  if ( new_scene == 0) {
    bri_i2c[light] = 144;
  } else if ( new_scene == 1) {
    bri_i2c[light] = 254;
  } else if ( new_scene == 2) {
    bri_i2c[light] = 1;
  }
}

void send_alert(uint8_t light) {
  bool prev_light_state_i2c = light_state_i2c[light];
  int prev_bri_i2c = bri_i2c[light];
  int prev_transitiontime_i2c = transitiontime_i2c;

  light_state_i2c[light] = false;
  transitiontime_i2c = 1;
  bri_i2c[light] = 255;

  process_lightdata_i2c(light);

  delay(10);

  light_state_i2c[light] = true;

  process_lightdata_i2c(light);
  delay(10);

  light_state_i2c[light] = false;

  process_lightdata_i2c(light);
  delay(10);

  light_state_i2c[light] = prev_light_state_i2c;
  bri_i2c[light] = prev_bri_i2c;
  transitiontime_i2c = prev_transitiontime_i2c;

  process_lightdata_i2c(light);

}

void process_lightdata_i2c(uint8_t light) {
  Wire.beginTransmission(lightadress_i2c[light]);
  Wire.write(bri_i2c[light]);
  Wire.write(light_state_i2c[light]);
  Wire.write(highByte(transitiontime_i2c));
  Wire.write(lowByte(transitiontime_i2c));
  error_code = Wire.endTransmission(true);

  if (error_code) {
    debug_light = light;
    debug_code = error_code;
  } else {
    if (debug_light == light && error_code == 0) {
      debug_light = 0x7F;
      debug_code = 0x7F;
    }
  }
  LOG_DEBUG("Light:", light);
  LOG_DEBUG("bri:", bri_i2c[light]);
  LOG_DEBUG("state:", light_state_i2c[light]);
  LOG_DEBUG("transitiontime:", transitiontime_i2c);
  if (error_code == 0) LOG_DEBUG("wire code:", "success");
  if (error_code == 1) LOG_DEBUG("wire code:", "data too long to fit in transmit buffer");
  if (error_code == 2) LOG_DEBUG("wire code:", "received NO ACK on transmit of address");
  if (error_code == 3) LOG_DEBUG("wire code:", "received NO ACK on transmit of data");
  if (error_code == 4) LOG_DEBUG("wire code:", "other error");
  if (error_code == 5) LOG_DEBUG("wire code:", "timeout");
}

void lightEngine_i2c() {
  for (int i = 0; i < LIGHTS_COUNT_i2c; i++) {
    if (light_state_i2c[i]) {
      if (bri_i2c[i] != current_bri_i2c[i]) {
        process_lightdata_i2c(i);
        current_bri_i2c[i] = bri_i2c[i];
      }
    } else {
      if (current_bri_i2c[i] != 0) {
        process_lightdata_i2c(i);
        current_bri_i2c[i] = 0;
      }
    }
  }
}

void request_lightdata(uint8_t light) {
  light_rec = Wire.requestFrom(lightadress_i2c[light], 2, 1);
  byte buff[2];
  Wire.readBytes(buff, 2);
  if (light_rec > 0) {
    bri_i2c[light] = buff[0];
    light_state_i2c[light] = buff[1];
    //current_bri_i2c[light] = bri_i2c[light];

    rec = light_rec;

    if (debug_light == light) {
      debug_light = 0x7F;
      debug_code = 0x7F;
    }

    LOG_DEBUG("Light:", light);
    LOG_DEBUG("bri:", bri_i2c[light]);
    LOG_DEBUG("state:", light_state_i2c[light]);
  } else {
    rec = 0;
    debug_light = light;
    LOG_ERROR("Light:", light, "no response");
  }
}

void ChangeNeoPixels_info() // this set the number of leds of the strip based on web configuration
{
  if (strip_info != NULL) {
    delete strip_info; // delete the previous dynamically created strip
  }
  strip_info = new NeoPixelBus<NeoRgbFeature, NeoEsp32Rmt0Ws2812xMethod>(1, INFO_DATA_PIN); // and recreate with new count
  strip_info->Begin();
}

void factoryReset() {
  LittleFS.format();
  //WiFi.disconnect(false, true);
  blinkLed(8, 100);
  ESP.restart();
}

void infoLight(RgbColor color) { // boot animation for leds count and wifi test
  // Flash the strip in the selected color. White = booted, green = WLAN connected, red = WLAN could not connect
  strip_info->SetPixelColor(0, color);
  strip_info->Show();
}

void setup() {
  Serial.begin(115200);
  LOG_SET_LEVEL(DebugLogLevel::LVL_TRACE);
  //LOG_FILE_SET_LEVEL(DebugLogLevel::LVL_TRACE);
  if (!LittleFS.begin()) {
    LOG_DEBUG("Failed to mount file system");
    //Serial.println("Failed to mount file system");
    LittleFS.format();
  } else {
    //LOG_ATTACH_FS_AUTO(LittleFS, "/log.txt", FILE_WRITE);
  }
  LOG_DEBUG("Start ESP32");
  EEPROM.begin(512);
  ChangeNeoPixels_info();
  infoLight(white);
  blinkLed(1);

  LOG_DEBUG("start W5500");
  ESP32_W5500_onEvent();

  ETH.begin( MISO_GPIO, MOSI_GPIO, SCK_GPIO, CS_GPIO, INT_GPIO, SPI_CLOCK_MHZ, ETH_SPI_HOST, mac);

  infoLight(white); // play white anymation
  while (!ESP32_W5500_isConnected()) { // connection to wifi still not ready
    LOG_DEBUG("W5500_isConnected: ", ESP32_W5500_isConnected());
    infoLight(red); // play red animation
    delay(500);
  }
  // Show that we are connected
  LOG_DEBUG("W5500_isConnected: ", ESP32_W5500_isConnected(), " IP Address: ", ETH.localIP());
  infoLight(green); // connected, play green animation

  i2c_setup();
  ws_setup();
  mesh_setup();
}

void loop() {
  i2c_loop();
  ws_loop();
  mesh_loop();
}


void i2c_setup() {
  Wire.begin();
  LOG_DEBUG("Setup I2C");

  for (int i = 0; i < LIGHTS_COUNT_i2c; i++) {
    request_lightdata(i);
  }

  server_i2c.on("/state", HTTP_PUT, []() { // HTTP PUT request used to set a new light state
    DynamicJsonDocument root(1024);
    DeserializationError error = deserializeJson(root, server_i2c.arg("plain"));

    if (error) {
      server_i2c.send(404, "text/plain", "FAIL. " + server_i2c.arg("plain"));
    } else {
      for (JsonPair state : root.as<JsonObject>()) {
        const char* key = state.key().c_str();
        int light = atoi(key) - 1;
        JsonObject values = state.value();
        transitiontime_i2c = 4;

        if (values.containsKey("on")) {
          if (values["on"]) {
            light_state_i2c[light] = true;
            if (EEPROM.read(1) == 0 && EEPROM.read(0) == 0) {
              EEPROM.write(0, 1);
            }
          } else {
            light_state_i2c[light] = false;
            if (EEPROM.read(1) == 0 && EEPROM.read(0) == 1) {
              EEPROM.write(0, 0);
            }
          }
        }

        if (values.containsKey("bri")) {
          bri_i2c[light] = values["bri"];
        }

        if (values.containsKey("bri_inc")) {
          bri_i2c[light] += (int) values["bri_inc"];
          if (bri_i2c[light] > 255) bri_i2c[light] = 255;
          else if (bri_i2c[light] < 1) bri_i2c[light] = 1;
        }

        if (values.containsKey("alert") && values["alert"] == "select") {
          send_alert(light);
        }

        if (values.containsKey("transitiontime")) {
          transitiontime_i2c = values["transitiontime"];
        }
        //process_lightdata_i2c(light, transitiontime);
      }
      String output;
      serializeJson(root, output);
      LOG_DEBUG("/state put", output);
      server_i2c.send(200, "text/plain", output);
    }
  });

  server_i2c.on("/state", HTTP_GET, []() { // HTTP GET request used to fetch current light state
    uint8_t light = server_i2c.arg("light").toInt() - 1;
    DynamicJsonDocument root(1024);
    root["on"] = light_state_i2c[light];
    root["bri"] = bri_i2c[light];
    String output;
    serializeJson(root, output);
    LOG_DEBUG("/state get", output);
    LOG_DEBUG("light :", light);
    server_i2c.send(200, "text/plain", output);
  });


  server_i2c.on("/detect", []() { // HTTP GET request used to discover the light type
    char macString[32] = {0};
    sprintf(macString, "%02X:%02X:%02X:%02X:%02X:%02X", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    DynamicJsonDocument root(1024);
    root["name"] = light_name_i2c;
    root["lights"] = LIGHTS_COUNT_i2c;
    root["protocol"] = "native_multi";
    root["modelid"] = "LWB010";
    root["type"] = "dimmable_light";
    root["mac"] = String(macString);
    root["version"] = LIGHT_VERSION_i2c;
    String output;
    serializeJson(root, output);
    server_i2c.send(200, "text/plain", output);
  });

  server_i2c.on("/", []() {
    transitiontime_i2c = 4;
    if (server_i2c.hasArg("startup")) {
      if (  EEPROM.read(1) != server_i2c.arg("startup").toInt()) {
        EEPROM.write(1, server_i2c.arg("startup").toInt());
        EEPROM.commit();
      }
    }

    for (int light = 0; light < LIGHTS_COUNT_i2c; light++) {
      if (server_i2c.hasArg("scene")) {
        if (server_i2c.arg("bri") == "" && server_i2c.arg("hue") == "" && server_i2c.arg("ct") == "" && server_i2c.arg("sat") == "") {
          if (  EEPROM.read(2) != server_i2c.arg("scene").toInt()) {
            EEPROM.write(2, server_i2c.arg("scene").toInt());
            EEPROM.commit();
          }
          apply_scene_i2c(server_i2c.arg("scene").toInt(), light);
        } else {
          if (server_i2c.arg("bri") != "") {
            bri_i2c[light] = server_i2c.arg("bri").toInt();
          }
        }
      } else if (server_i2c.hasArg("on")) {
        if (server_i2c.arg("on") == "true") {
          light_state_i2c[light] = true; {
            if (EEPROM.read(1) == 0 && EEPROM.read(0) == 0) {
              EEPROM.write(0, 1);
            }
          }
        } else {
          light_state_i2c[light] = false;
          if (EEPROM.read(1) == 0 && EEPROM.read(0) == 1) {
            EEPROM.write(0, 0);
          }
        }
        EEPROM.commit();
      } else if (server_i2c.hasArg("alert")) {
        send_alert(light);
      }
      if (light_state_i2c[light]) {
        step_level_i2c[light] = ((float)bri_i2c[light] - current_bri_i2c[light]) / transitiontime_i2c;
      } else {
        step_level_i2c[light] = current_bri_i2c[light] / transitiontime_i2c;
      }
    }
    if (server_i2c.hasArg("reset")) {
      ESP.restart();
    }


    String http_content = "<!doctype html>";
    http_content += "<html>";
    http_content += "<head>";
    http_content += "<meta charset=\"utf-8\">";
    http_content += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">";
    http_content += "<title>Light Setup</title>";
    http_content += "<link rel=\"stylesheet\" href=\"https://unpkg.com/purecss@0.6.2/build/pure-min.css\">";
    http_content += "</head>";
    http_content += "<body>";
    http_content += "<fieldset>";
    http_content += "<h3>Light Setup</h3>";
    http_content += "<form class=\"pure-form pure-form-aligned\" action=\"/\" method=\"post\">";
    http_content += "<div class=\"pure-control-group\">";
    http_content += "<label for=\"power\"><strong>Power</strong></label>";
    http_content += "<a class=\"pure-button"; if (light_state_i2c[0]) http_content += "  pure-button-primary"; http_content += "\" href=\"/?on=true\">ON</a>";
    http_content += "<a class=\"pure-button"; if (!light_state_i2c[0]) http_content += "  pure-button-primary"; http_content += "\" href=\"/?on=false\">OFF</a>";
    http_content += "</div>";
    http_content += "<div class=\"pure-control-group\">";
    http_content += "<label for=\"startup\">Startup</label>";
    http_content += "<select onchange=\"this.form.submit()\" id=\"startup\" name=\"startup\">";
    http_content += "<option "; if (EEPROM.read(1) == 0) http_content += "selected=\"selected\""; http_content += " value=\"0\">Last state</option>";
    http_content += "<option "; if (EEPROM.read(1) == 1) http_content += "selected=\"selected\""; http_content += " value=\"1\">On</option>";
    http_content += "<option "; if (EEPROM.read(1) == 2) http_content += "selected=\"selected\""; http_content += " value=\"2\">Off</option>";
    http_content += "</select>";
    http_content += "</div>";
    http_content += "<div class=\"pure-control-group\">";
    http_content += "<label for=\"scene\">Scene</label>";
    http_content += "<select onchange = \"this.form.submit()\" id=\"scene\" name=\"scene\">";
    http_content += "<option "; if (EEPROM.read(2) == 0) http_content += "selected=\"selected\""; http_content += " value=\"0\">Relax</option>";
    http_content += "<option "; if (EEPROM.read(2) == 1) http_content += "selected=\"selected\""; http_content += " value=\"1\">Bright</option>";
    http_content += "<option "; if (EEPROM.read(2) == 2) http_content += "selected=\"selected\""; http_content += " value=\"2\">Nightly</option>";
    http_content += "</select>";
    http_content += "</div>";
    http_content += "<br>";
    http_content += "<div class=\"pure-control-group\">";
    http_content += "<label for=\"state\"><strong>State</strong></label>";
    http_content += "</div>";
    http_content += "<div class=\"pure-control-group\">";
    http_content += "<label for=\"bri\">Bri</label>";
    http_content += "<input id=\"bri\" name=\"bri\" type=\"text\" placeholder=\"" + (String)bri_i2c[0] + "\">";
    http_content += "</div>";

    http_content += "<div class=\"pure-controls\">";
    http_content += "<span class=\"pure-form-message\"><a href=\"/?alert=1\">alert</a> or <a href=\"/?reset=1\">reset</a></span>";
    http_content += "<label for=\"cb\" class=\"pure-checkbox\">";
    http_content += "</label>";
    http_content += "<button type=\"submit\" class=\"pure-button pure-button-primary\">Save</button>";
    http_content += "</div>";
    http_content += "</fieldset>";
    http_content += "</form>";
    http_content += "</body>";
    http_content += "</html>";


    server_i2c.send(200, "text/html", http_content);

  });

  server_i2c.on("/reset", []() { // trigger manual reset
    server_i2c.send(200, "text/html", "reset");
    delay(1000);
    ESP.restart();
  });


  server_i2c.on("/factory", []() { // trigger manual reset
    server_i2c.send(200, "text/html", "factory reset");
    factoryReset();
  });

  server_i2c.onNotFound(handleNotFound_i2c);

  server_i2c.begin();
}

void i2c_loop() {
  server_i2c.handleClient();
  lightEngine_i2c();
  //i2c_http_loop();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= LIGHT_interval) {
    previousMillis = currentMillis;
    for (int i = 0; i < LIGHTS_COUNT_i2c; i++) {
      request_lightdata(i);
    }
  }
}