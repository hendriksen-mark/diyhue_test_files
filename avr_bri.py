#result = [0,0,0,0]
result = [(254*1),(254*0),(254*0),(0*1)]

bri = 0
lights_on = 0
for slot in result:
    #print(slot)
    bri = bri + slot
    lights_on = lights_on + 1
if lights_on > 0:
    bri = (((bri/lights_on)/254)*100) if bri > 0 else 0
#print(lights_on)
#print(int(bri))

def map_value(value, b_min, b_max):
    # Calculate the ratio of the value within the range a
    ratio = ((value) / (255))
    print(ratio)
    # Map the ratio to the range b
    mapped_value = b_min + (((value) / (255)) * (b_max - b_min))
    return mapped_value

# Example usage
a_min, a_max = 1, 255
b_min, b_max = 1, 100
value = 255
mapped_value = map_value(value, b_min, b_max)
print(mapped_value)  # Output: 50.0