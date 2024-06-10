sensorTypes = {}
sensorTypes[
    "RDM002"
] = {
    "ZLLSwitch": {
        "state": {
            "buttonevent": 3002,
            "lastupdated": "2023-05-13T09:34:38"
        },
        "config": {
            "on": True,
            "battery": 100,
            "reachable": True,
            "pending": []
        },
        "static": {
            "swupdate": {
                "state": "noupdates",
                "lastinstall": "2022-07-01T14:38:51"
            },
            "manufacturername": "Signify Netherlands B.V.",
            "productname": "Hue tap dial switch",
            "swversion": "2.59.25",
            "capabilities": {
                "certified": True,
                "primary": False,
                "inputs": [
                    {
                        "repeatintervals": [
                            800
                        ],
                        "events": [
                            {
                                "buttonevent": 1000,
                                "eventtype": "initial_press"
                            },
                            {
                                "buttonevent": 1001,
                                "eventtype": "repeat"
                            },
                            {
                                "buttonevent": 1002,
                                "eventtype": "short_release"
                            },
                            {
                                "buttonevent": 1003,
                                "eventtype": "long_release"
                            },
                            {
                                "buttonevent": 1010,
                                "eventtype": "long_press"
                            }
                        ]
                    },
                    {
                        "repeatintervals": [
                            800
                        ],
                        "events": [
                            {
                                "buttonevent": 2000,
                                "eventtype": "initial_press"
                            },
                            {
                                "buttonevent": 2001,
                                "eventtype": "repeat"
                            },
                            {
                                "buttonevent": 2002,
                                "eventtype": "short_release"
                            },
                            {
                                "buttonevent": 2003,
                                "eventtype": "long_release"
                            },
                            {
                                "buttonevent": 2010,
                                "eventtype": "long_press"
                            }
                        ]
                    },
                    {
                        "repeatintervals": [
                            800
                        ],
                        "events": [
                            {
                                "buttonevent": 3000,
                                "eventtype": "initial_press"
                            },
                            {
                                "buttonevent": 3001,
                                "eventtype": "repeat"
                            },
                            {
                                "buttonevent": 3002,
                                "eventtype": "short_release"
                            },
                            {
                                "buttonevent": 3003,
                                "eventtype": "long_release"
                            },
                            {
                                "buttonevent": 3010,
                                "eventtype": "long_press"
                            }
                        ]
                    },
                    {
                        "repeatintervals": [
                            800
                        ],
                        "events": [
                            {
                                "buttonevent": 4000,
                                "eventtype": "initial_press"
                            },
                            {
                                "buttonevent": 4001,
                                "eventtype": "repeat"
                            },
                            {
                                "buttonevent": 4002,
                                "eventtype": "short_release"
                            },
                            {
                                "buttonevent": 4003,
                                "eventtype": "long_release"
                            },
                            {
                                "buttonevent": 4010,
                                "eventtype": "long_press"
                            }
                        ]
                    }
                ]
            }
        }
    },
    "ZLLRelativeRotary": {
        "state": {
            "rotaryevent": 2,
            "expectedrotation": 90,
            "expectedeventduration": 400,
            "lastupdated": "2023-05-13T09:34:38"
        },
        "config": {
            "on": True,
            "battery": 100,
            "reachable": True,
            "pending": []
        },
        "static": {
            "swupdate": {
                "state": "noupdates",
                "lastinstall": "2022-07-01T14:38:51"
            },
            "manufacturername": "Signify Netherlands B.V.",
            "productname": "Hue tap dial switch",
            "swversion": "2.59.25",
            "capabilities": {
                "certified": True,
                "primary": False,
                "inputs": [
                    {
                        "repeatintervals": [
                            400
                        ],
                        "events": [
                            {
                                "rotaryevent": 1,
                                "eventtype": "start"
                            },
                            {
                                "rotaryevent": 2,
                                "eventtype": "repeat"
                            }
                        ]
                    }
                ]
            }
        }
    }
}




sensor_type = list(sensorTypes[key["model_id"]].keys())[0]