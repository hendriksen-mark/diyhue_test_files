#result = [0,0,0,0]
result = [(254*1),(254*0),(254*0),(0*1)]

bri = 0
lights_on = 0
for slot in result:
    print(slot)
    bri = bri + slot
    lights_on = lights_on + 1
if lights_on > 0:
    bri = (((bri/lights_on)/254)*100) if bri > 0 else 0
print(lights_on)
print(int(bri))