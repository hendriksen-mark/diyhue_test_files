import random

arr = b'HueStream' #Protocol name Field1
msg = bytes([
        2, 0,     #Api version Field2
        0,        #Sequence number, not needed Field3
        0, 0,     #Zeroes Reserved Field4
        0,        #0: RGB Color space, 1: XY Brightness Field5
        0,        #Zero Reserved Field6
        ])
msg += b'96a51e21-20db-562d-b565-13bb59c1a6a1' #entertainment configuration id Field7
r = 0#random.randrange(0, 65535)
g = 0#random.randrange(0, 65535)
b = 0#random.randrange(0, 65535)
id = 0
msg += id.to_bytes(1,"big")
#msg.extend([    id,      #Light id
                #r.to_bytes(2,"big"),   #Red (or X) as 16 (2 * 8) bit value
                #g.to_bytes(2,"big"),   #Green (or Y) as 16 (2 * 8) bit value
                #b.to_bytes(2,"big"),   #Blue (or Brightness) as 16 (2 * 8) bit value
#                ])
msg += r.to_bytes(2,"big")
msg += g.to_bytes(2,"big")
msg += g.to_bytes(2,"big")
arr += msg

print(arr)
print(b'HueStream\x02\x00\x00\x00\x00\x00\x0096a51e21-20db-562d-b565-13bb59c1a6a1\x00\x00\x00\x00\x00\x00\x00')
