wled = {
  "state": {
    "on": True,
    "bri": 36,
    "transition": 7,
    "ps": -1,
    "pl": -1,
    "ledmap": 0,
    "AudioReactive": {
      "on": False
    },
    "nl": {
      "on": False,
      "dur": 60,
      "mode": 1,
      "tbri": 0,
      "rem": -1
    },
    "udpn": {
      "send": False,
      "recv": True,
      "sgrp": 1,
      "rgrp": 1
    },
    "lor": 0,
    "mainseg": 0,
    "seg": [
      {
        "id": 0,
        "start": 0,
        "stop": 40,
        "len": 40,
        "grp": 1,
        "spc": 0,
        "of": 0,
        "on": True,
        "frz": False,
        "bri": 255,
        "cct": 127,
        "set": 0,
        "col": [
          [255, 113, 0, 0],
          [0, 0, 0, 0],
          [0, 0, 0, 0]
        ],
        "fx": 115,
        "sx": 128,
        "ix": 128,
        "pal": 50,
        "c1": 128,
        "c2": 128,
        "c3": 16,
        "sel": False,
        "rev": False,
        "mi": False,
        "o1": False,
        "o2": False,
        "o3": False,
        "si": 0,
        "m12": 0
      },
      {
        "id": 1,
        "start": 40,
        "stop": 80,
        "len": 40,
        "grp": 1,
        "spc": 0,
        "of": 0,
        "on": True,
        "frz": False,
        "bri": 255,
        "cct": 127,
        "set": 0,
        "col": [
          [255, 113, 0, 0],
          [0, 0, 0, 0],
          [0, 0, 0, 0]
        ],
        "fx": 115,
        "sx": 128,
        "ix": 128,
        "pal": 50,
        "c1": 128,
        "c2": 128,
        "c3": 16,
        "sel": True,
        "rev": False,
        "mi": False,
        "o1": False,
        "o2": False,
        "o3": False,
        "si": 0,
        "m12": 0
      },
      {
        "id": 2,
        "start": 80,
        "stop": 120,
        "len": 40,
        "grp": 1,
        "spc": 0,
        "of": 0,
        "on": True,
        "frz": False,
        "bri": 255,
        "cct": 127,
        "set": 0,
        "col": [
          [255, 113, 0, 0],
          [0, 0, 0, 0],
          [0, 0, 0, 0]
        ],
        "fx": 115,
        "sx": 128,
        "ix": 128,
        "pal": 50,
        "c1": 128,
        "c2": 128,
        "c3": 16,
        "sel": False,
        "rev": False,
        "mi": False,
        "o1": False,
        "o2": False,
        "o3": False,
        "si": 0,
        "m12": 0
      }
    ]
  },
  "info": {
    "ver": "0.15.0-b7",
    "vid": 2410270,
    "cn": "Kōsen",
    "release": "1",
    "leds": {
      "count": 120,
      "pwr": 0,
      "fps": 24,
      "maxpwr": 0,
      "maxseg": 32,
      "bootps": 0,
      "seglc": [3, 3, 3],
      "lc": 3,
      "rgbw": True,
      "wv": 2,
      "cct": 0
    },
    "str": False,
    "name": "WLED",
    "udpport": 21324,
    "simplifiedui": False,
    "live": True,
    "liveseg": -1,
    "lm": "UDP",
    "lip": "192.168.100.156",
    "ws": 1,
    "fxcount": 187,
    "palcount": 71,
    "cpalcount": 0,
    "maps": [
      {
        "id": 0
      }
    ],
    "wifi": {
      "bssid": "9C:53:22:37:FE:61",
      "rssi": -67,
      "signal": 66,
      "channel": 6,
      "ap": False
    },
    "fs": {
      "u": 12,
      "t": 983,
      "pmt": 1732882498
    },
    "ndc": 3,
    "arch": "esp32",
    "core": "v3.3.6-16-gcc5440f6a2",
    "clock": 240,
    "flash": 4,
    "lwip": 0,
    "freeheap": 174024,
    "uptime": 1286,
    "time": "2024-11-29, 12:33:22",
    "u": {
      "AudioReactive": [
        "\u003Cbutton class=\"btn btn-xs\" onclick=\"requestJson({AudioReactive:{enabled:True}});\"\u003E\u003Ci class=\"icons off\"\u003E&#xe08f;\u003C/i\u003E\u003C/button\u003E"
      ]
    },
    "opt": 79,
    "brand": "WLED",
    "product": "FOSS",
    "mac": "4091518a935c",
    "ip": "192.168.100.182"
  },
  "effects": [
    "Solid",
    "Blink",
    "Breathe",
    "Wipe",
    "Wipe Random",
    "Random Colors",
    "Sweep",
    "Dynamic",
    "Colorloop",
    "Rainbow",
    "Scan",
    "Scan Dual",
    "Fade",
    "Theater",
    "Theater Rainbow",
    "Running",
    "Saw",
    "Twinkle",
    "Dissolve",
    "Dissolve Rnd",
    "Sparkle",
    "Sparkle Dark",
    "Sparkle+",
    "Strobe",
    "Strobe Rainbow",
    "Strobe Mega",
    "Blink Rainbow",
    "Android",
    "Chase",
    "Chase Random",
    "Chase Rainbow",
    "Chase Flash",
    "Chase Flash Rnd",
    "Rainbow Runner",
    "Colorful",
    "Traffic Light",
    "Sweep Random",
    "Chase 2",
    "Aurora",
    "Stream",
    "Scanner",
    "Lighthouse",
    "Fireworks",
    "Rain",
    "Tetrix",
    "Fire Flicker",
    "Gradient",
    "Loading",
    "Rolling Balls",
    "Fairy",
    "Two Dots",
    "Fairytwinkle",
    "Running Dual",
    "RSVD",
    "Chase 3",
    "Tri Wipe",
    "Tri Fade",
    "Lightning",
    "ICU",
    "Multi Comet",
    "Scanner Dual",
    "Stream 2",
    "Oscillate",
    "Pride 2015",
    "Juggle",
    "Palette",
    "Fire 2012",
    "Colorwaves",
    "Bpm",
    "Fill Noise",
    "Noise 1",
    "Noise 2",
    "Noise 3",
    "Noise 4",
    "Colortwinkles",
    "Lake",
    "Meteor",
    "Meteor Smooth",
    "Railway",
    "Ripple",
    "Twinklefox",
    "Twinklecat",
    "Halloween Eyes",
    "Solid Pattern",
    "Solid Pattern Tri",
    "Spots",
    "Spots Fade",
    "Glitter",
    "Candle",
    "Fireworks Starburst",
    "Fireworks 1D",
    "Bouncing Balls",
    "Sinelon",
    "Sinelon Dual",
    "Sinelon Rainbow",
    "Popcorn",
    "Drip",
    "Plasma",
    "Percent",
    "Ripple Rainbow",
    "Heartbeat",
    "Pacifica",
    "Candle Multi",
    "Solid Glitter",
    "Sunrise",
    "Phased",
    "Twinkleup",
    "Noise Pal",
    "Sine",
    "Phased Noise",
    "Flow",
    "Chunchun",
    "Dancing Shadows",
    "Washing Machine",
    "Rotozoomer",
    "Blends",
    "TV Simulator",
    "Dynamic Smooth",
    "Spaceships",
    "Crazy Bees",
    "Ghost Rider",
    "Blobs",
    "Scrolling Text",
    "Drift Rose",
    "Distortion Waves",
    "Soap",
    "Octopus",
    "Waving Cell",
    "Pixels",
    "Pixelwave",
    "Juggles",
    "Matripix",
    "Gravimeter",
    "Plasmoid",
    "Puddles",
    "Midnoise",
    "Noisemeter",
    "Freqwave",
    "Freqmatrix",
    "GEQ",
    "Waterfall",
    "Freqpixels",
    "RSVD",
    "Noisefire",
    "Puddlepeak",
    "Noisemove",
    "Noise2D",
    "Perlin Move",
    "Ripple Peak",
    "Firenoise",
    "Squared Swirl",
    "RSVD",
    "DNA",
    "Matrix",
    "Metaballs",
    "Freqmap",
    "Gravcenter",
    "Gravcentric",
    "Gravfreq",
    "DJ Light",
    "Funky Plank",
    "RSVD",
    "Pulser",
    "Blurz",
    "Drift",
    "Waverly",
    "Sun Radiation",
    "Colored Bursts",
    "Julia",
    "RSVD",
    "RSVD",
    "RSVD",
    "Game Of Life",
    "Tartan",
    "Polar Lights",
    "Swirl",
    "Lissajous",
    "Frizzles",
    "Plasma Ball",
    "Flow Stripe",
    "Hiphotic",
    "Sindots",
    "DNA Spiral",
    "Black Hole",
    "Wavesins",
    "Rocktaves",
    "Akemi"
  ],
  "palettes": [
    "Default",
    "* Random Cycle",
    "* Color 1",
    "* Colors 1&2",
    "* Color Gradient",
    "* Colors Only",
    "Party",
    "Cloud",
    "Lava",
    "Ocean",
    "Forest",
    "Rainbow",
    "Rainbow Bands",
    "Sunset",
    "Rivendell",
    "Breeze",
    "Red & Blue",
    "Yellowout",
    "Analogous",
    "Splash",
    "Pastel",
    "Sunset 2",
    "Beach",
    "Vintage",
    "Departure",
    "Landscape",
    "Beech",
    "Sherbet",
    "Hult",
    "Hult 64",
    "Drywet",
    "Jul",
    "Grintage",
    "Rewhi",
    "Tertiary",
    "Fire",
    "Icefire",
    "Cyane",
    "Light Pink",
    "Autumn",
    "Magenta",
    "Magred",
    "Yelmag",
    "Yelblu",
    "Orange & Teal",
    "Tiamat",
    "April Night",
    "Orangery",
    "C9",
    "Sakura",
    "Aurora",
    "Atlantica",
    "C9 2",
    "C9 New",
    "Temperature",
    "Aurora 2",
    "Retro Clown",
    "Candy",
    "Toxy Reaf",
    "Fairy Reaf",
    "Semi Blue",
    "Pink Candy",
    "Red Reaf",
    "Aqua Flash",
    "Yelblu Hot",
    "Lite Light",
    "Red Flash",
    "Blink Red",
    "Red Shift",
    "Red Tide",
    "Candy2"
  ]
}
