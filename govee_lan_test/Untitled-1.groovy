[
    {
        "sku": "H61C3",
        "device": "1C:C7:32:32:33:20:84:FF",
        "deviceName": "Schreibtischlicht 2",
        "type": "devices.types.light",
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
                "instance": "segmentedBrightness",
                "parameters": {
                    "dataType": "STRUCT",
                    "fields": [
                        {
                            "fieldName": "segment",
                            "size": {
                                "min": 1,
                                "max": 15
                            },
                            "dataType": "Array",
                            "elementRange": {
                                "min": 0,
                                "max": 14
                            },
                            "elementType": "INTEGER",
                            "required": True
                        },
                        {
                            "fieldName": "brightness",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 100,
                                "precision": 1
                            },
                            "required": True
                        }
                    ]
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
                            "size": {
                                "min": 1,
                                "max": 40
                            },
                            "dataType": "Array",
                            "elementRange": {
                                "min": 0,
                                "max": 39
                            },
                            "elementType": "INTEGER",
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
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "lightScene",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            },
            {
                "type": "devices.capabilities.music_setting",
                "instance": "musicMode",
                "parameters": {
                    "dataType": "STRUCT",
                    "fields": [
                        {
                            "fieldName": "musicMode",
                            "dataType": "ENUM",
                            "options": [
                                {
                                    "name": "Energic",
                                    "value": 1
                                },
                                {
                                    "name": "Rhythm",
                                    "value": 2
                                },
                                {
                                    "name": "Spectrum",
                                    "value": 3
                                },
                                {
                                    "name": "Rolling",
                                    "value": 4
                                },
                                {
                                    "name": "Separation",
                                    "value": 5
                                },
                                {
                                    "name": "Hopping",
                                    "value": 6
                                },
                                {
                                    "name": "PianoKeys",
                                    "value": 7
                                },
                                {
                                    "name": "Fountain",
                                    "value": 8
                                },
                                {
                                    "name": "DayAndNight",
                                    "value": 9
                                },
                                {
                                    "name": "Sprouting",
                                    "value": 10
                                },
                                {
                                    "name": "Shiny",
                                    "value": 11
                                }
                            ],
                            "required": True
                        },
                        {
                            "unit": "unit.percent",
                            "fieldName": "sensitivity",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 100,
                                "precision": 1
                            },
                            "required": True
                        },
                        {
                            "fieldName": "autoColor",
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
                            ],
                            "required": False
                        },
                        {
                            "fieldName": "rgb",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 16777215,
                                "precision": 1
                            },
                            "required": False
                        }
                    ]
                }
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "diyScene",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "snapshot",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            }
        ]
    },
    {
        "sku": "H61C3",
        "device": "1A:D9:35:33:33:0D:48:FF",
        "deviceName": "Schreibtisch Licht 1",
        "type": "devices.types.light",
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
                "instance": "segmentedBrightness",
                "parameters": {
                    "dataType": "STRUCT",
                    "fields": [
                        {
                            "fieldName": "segment",
                            "size": {
                                "min": 1,
                                "max": 15
                            },
                            "dataType": "Array",
                            "elementRange": {
                                "min": 0,
                                "max": 14
                            },
                            "elementType": "INTEGER",
                            "required": True
                        },
                        {
                            "fieldName": "brightness",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 100,
                                "precision": 1
                            },
                            "required": True
                        }
                    ]
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
                            "size": {
                                "min": 1,
                                "max": 40
                            },
                            "dataType": "Array",
                            "elementRange": {
                                "min": 0,
                                "max": 39
                            },
                            "elementType": "INTEGER",
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
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "lightScene",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            },
            {
                "type": "devices.capabilities.music_setting",
                "instance": "musicMode",
                "parameters": {
                    "dataType": "STRUCT",
                    "fields": [
                        {
                            "fieldName": "musicMode",
                            "dataType": "ENUM",
                            "options": [
                                {
                                    "name": "Energic",
                                    "value": 1
                                },
                                {
                                    "name": "Rhythm",
                                    "value": 2
                                },
                                {
                                    "name": "Spectrum",
                                    "value": 3
                                },
                                {
                                    "name": "Rolling",
                                    "value": 4
                                },
                                {
                                    "name": "Separation",
                                    "value": 5
                                },
                                {
                                    "name": "Hopping",
                                    "value": 6
                                },
                                {
                                    "name": "PianoKeys",
                                    "value": 7
                                },
                                {
                                    "name": "Fountain",
                                    "value": 8
                                },
                                {
                                    "name": "DayAndNight",
                                    "value": 9
                                },
                                {
                                    "name": "Sprouting",
                                    "value": 10
                                },
                                {
                                    "name": "Shiny",
                                    "value": 11
                                }
                            ],
                            "required": True
                        },
                        {
                            "unit": "unit.percent",
                            "fieldName": "sensitivity",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 100,
                                "precision": 1
                            },
                            "required": True
                        },
                        {
                            "fieldName": "autoColor",
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
                            ],
                            "required": False
                        },
                        {
                            "fieldName": "rgb",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 16777215,
                                "precision": 1
                            },
                            "required": False
                        }
                    ]
                }
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "diyScene",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "snapshot",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            }
        ]
    },
    {
        "sku": "H608A",
        "device": "0B:EC:CC:39:32:35:67:8B",
        "deviceName": "String Downlights",
        "type": "devices.types.light",
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
                "instance": "segmentedBrightness",
                "parameters": {
                    "dataType": "STRUCT",
                    "fields": [
                        {
                            "fieldName": "segment",
                            "size": {
                                "min": 1,
                                "max": 5
                            },
                            "dataType": "Array",
                            "elementRange": {
                                "min": 0,
                                "max": 14
                            },
                            "elementType": "INTEGER",
                            "required": True
                        },
                        {
                            "fieldName": "brightness",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 100,
                                "precision": 1
                            },
                            "required": True
                        }
                    ]
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
                            "size": {
                                "min": 1,
                                "max": 5
                            },
                            "dataType": "Array",
                            "elementRange": {
                                "min": 0,
                                "max": 14
                            },
                            "elementType": "INTEGER",
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
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "lightScene",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            },
            {
                "type": "devices.capabilities.music_setting",
                "instance": "musicMode",
                "parameters": {
                    "dataType": "STRUCT",
                    "fields": [
                        {
                            "fieldName": "musicMode",
                            "dataType": "ENUM",
                            "options": [
                                {
                                    "name": "Energic",
                                    "value": 1
                                },
                                {
                                    "name": "Starlight",
                                    "value": 2
                                },
                                {
                                    "name": "Rhythm",
                                    "value": 3
                                },
                                {
                                    "name": "HeartBeating",
                                    "value": 4
                                },
                                {
                                    "name": "Hopping",
                                    "value": 5
                                },
                                {
                                    "name": "Luminous",
                                    "value": 6
                                },
                                {
                                    "name": "Rolling",
                                    "value": 7
                                },
                                {
                                    "name": "Shiny",
                                    "value": 8
                                }
                            ],
                            "required": True
                        },
                        {
                            "unit": "unit.percent",
                            "fieldName": "sensitivity",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 100,
                                "precision": 1
                            },
                            "required": True
                        },
                        {
                            "fieldName": "autoColor",
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
                            ],
                            "required": False
                        },
                        {
                            "fieldName": "rgb",
                            "dataType": "INTEGER",
                            "range": {
                                "min": 0,
                                "max": 16777215,
                                "precision": 1
                            },
                            "required": False
                        }
                    ]
                }
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "diyScene",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            },
            {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "snapshot",
                "parameters": {
                    "dataType": "ENUM",
                    "options": []
                }
            },
            {
                "type": "devices.capabilities.toggle",
                "instance": "dreamViewToggle",
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
            }
        ]
    }
]