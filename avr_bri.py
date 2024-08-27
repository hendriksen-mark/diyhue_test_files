#result = [0,0,0,0]
result = [(254*1),(254*0.09),(254*0.5),(0*1)]

bri = 0
lights_on = 0
for slot in result:
    if slot > 0:
        bri = bri + slot
        lights_on = lights_on + 1
if lights_on > 0:
    bri = (((bri/lights_on)/254)*100)
print(int(bri))