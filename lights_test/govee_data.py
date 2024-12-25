govee = {
  "code": 200,
  "message": "success",
  "data": [
    {
      "sku": "H6601",
      "device": "9D:FA:85:EB:D3:00:8B:FF",
      "capabilities": [
        {
          "type": "devices.capabilities.on_off",
          "instance": "powerSwitch",
          "parameters": {
            "dataType": "ENUM",
            "options": [
              {
                "name": "on",
                "value": 1
              },
              {
                "name": "off",
                "value": 0
              }
            ]
          }
        },
        {
          "type": "devices.capabilities.toggle",
          "instance": "gradientToggle",
          "parameters": {
            "dataType": "ENUM",
            "options": [
              {
                "name": "on",
                "value": 1
              },
              {
                "name": "off",
                "value": 0
              }
            ]
          }
        },
        {
          "type": "devices.capabilities.range",
          "instance": "brightness",
          "parameters": {
            "unit": "unit.percent",
            "dataType": "INTEGER",
            "range": {
              "min": 1,
              "max": 100,
              "precision": 1
            }
          }
        },
        {
          "type": "devices.capabilities.segment_color_setting",
          "instance": "segmentedColorRgb",
          "parameters": {
            "dataType": "STRUCT",
            "fields": [
              {
                "fieldName": "segment",
                "dataType": "Array",
                "options": [
                  {
                    "value": 0
                  },
                  {
                    "value": 1
                  },
                  {
                    "value": 2
                  },
                  {
                    "value": 3
                  },
                  {
                    "value": 4
                  },
                  {
                    "value": 5
                  },
                  {
                    "value": 6
                  },
                  {
                    "value": 7
                  },
                  {
                    "value": 8
                  },
                  {
                    "value": 9
                  },
                  {
                    "value": 10
                  },
                  {
                    "value": 11
                  },
                  {
                    "value": 12
                  },
                  {
                    "value": 13
                  },
                  {
                    "value": 14
                  }
                ],
                "required": True
              },
              {
                "fieldName": "rgb",
                "dataType": "INTEGER",
                "range": {
                  "min": 0,
                  "max": 16777215,
                  "precision": 1
                },
                "required": True
              }
            ]
          }
        },
        {
          "type": "devices.capabilities.color_setting",
          "instance": "colorRgb",
          "parameters": {
            "dataType": "INTEGER",
            "range": {
              "min": 0,
              "max": 16777215,
              "precision": 1
            }
          }
        },
        {
          "type": "devices.capabilities.color_setting",
          "instance": "colorTemperatureK",
          "parameters": {
            "dataType": "INTEGER",
            "range": {
              "min": 2000,
              "max": 9000,
              "precision": 1
            }
          }
        }
      ]
    },
    {
      "sku": "H6601",
      "device": "DD:FA:85:EB:D3:77:BB:FF",
      "capabilities": [
        {
          "type": "devices.capabilities.on_off",
          "instance": "powerSwitch",
          "parameters": {
            "dataType": "ENUM",
            "options": [
              {
                "name": "on",
                "value": 1
              },
              {
                "name": "off",
                "value": 0
              }
            ]
          }
        },
        {
          "type": "devices.capabilities.toggle",
          "instance": "gradientToggle",
          "parameters": {
            "dataType": "ENUM",
            "options": [
              {
                "name": "on",
                "value": 1
              },
              {
                "name": "off",
                "value": 0
              }
            ]
          }
        },
        {
          "type": "devices.capabilities.range",
          "instance": "brightness",
          "parameters": {
            "unit": "unit.percent",
            "dataType": "INTEGER",
            "range": {
              "min": 1,
              "max": 100,
              "precision": 1
            }
          }
        },
        {
          "type": "devices.capabilities.segment_color_setting",
          "instance": "segmentedColorRgb",
          "parameters": {
            "dataType": "STRUCT",
            "fields": [
              {
                "fieldName": "segment",
                "dataType": "Array",
                "options": [
                  {
                    "value": 0
                  },
                  {
                    "value": 1
                  },
                  {
                    "value": 2
                  },
                  {
                    "value": 3
                  },
                  {
                    "value": 4
                  },
                  {
                    "value": 5
                  },
                  {
                    "value": 6
                  },
                  {
                    "value": 7
                  },
                  {
                    "value": 8
                  },
                  {
                    "value": 9
                  },
                  {
                    "value": 10
                  },
                  {
                    "value": 11
                  },
                  {
                    "value": 12
                  },
                  {
                    "value": 13
                  },
                  {
                    "value": 14
                  }
                ],
                "required": True
              },
              {
                "fieldName": "rgb",
                "dataType": "INTEGER",
                "range": {
                  "min": 0,
                  "max": 16777215,
                  "precision": 1
                },
                "required": True
              }
            ]
          }
        },
        {
          "type": "devices.capabilities.color_setting",
          "instance": "colorRgb",
          "parameters": {
            "dataType": "INTEGER",
            "range": {
              "min": 0,
              "max": 16777215,
              "precision": 1
            }
          }
        },
        {
          "type": "devices.capabilities.color_setting",
          "instance": "colorTemperatureK",
          "parameters": {
            "dataType": "INTEGER",
            "range": {
              "min": 2000,
              "max": 9000,
              "precision": 1
            }
          }
        }
      ]
    }
  ]
}

return_state_govee = {
    "requestId": "uuid",
    "msg": "success",
    "code": 200,
    "payload": {
        "sku": "H7143",
        "device": "52:8B:D4:AD:FC:45:5D:FE",
        "capabilities": [
            {
                "type": "devices.capabilities.online",
                "instance": "online",
                "state": {
                    "value": False
                }
            },
            {
                "type": "devices.capabilities.on_off",
                "instance": "powerSwitch",
                "state": {
                    "value": 0
                }
            },
            {
                "type": "devices.capabilities.toggle",
                "instance": "warmMistToggle",
                "state": {
                    "value": 0
                }
            },
            {
                "type": "devices.capabilities.work_mode",
                "instance": "workMode",
                "state": {
                    "value": {
                        "workMode": 3,
                        "modeValue": 9
                    }
                }
            },
            {
                "type": "devices.capabilities.range",
                "instance": "humidity",
                "state": {
                    "value": ""
                }
            },
            {
                "type": "devices.capabilities.toggle",
                "instance": "nightlightToggle",
                "state": {
                    "value": 1
                }
            },
            {
                "type": "devices.capabilities.range",
                "instance": "brightness",
                "state": {
                    "value": 5
                }
            },
            {
                "type": "devices.capabilities.color_setting",
                "instance": "colorRgb",
                "state": {
                    "value": 16777215
                }
            },
            {
                "type": "devices.capabilities.mode",
                "instance": "nightlightScene",
                "state": {
                    "value": 5
                }
            }
        ]
    }
}