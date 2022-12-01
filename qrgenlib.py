import qrcode
from PIL import Image
import numpy as np

from QRCode import QRCodeL
qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    mask_pattern=0
)

s = 'https://github.com/hangj/qrcode/blob/master/MyQR/mylibs/data.py'
qr.add_data(s)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
print(qr.data_cache)
img.save('example.bmp')


d = QRCodeL()
r = d.Encode(s)
#print(d.raw_code)
res = []
for i in range(0,len(d.raw_code),8):
    res.append(int(d.raw_code[i:i+8], 2))
print(d.byteline)
#print(r)
#print(d.byteline)

#print([bin(i)[2:] for i in qr.data_cache])
print(''.join([ '0'*(8-len(bin(num)[2:]))+bin(num)[2:]   for num in qr.data_cache]))
print(''.join(d.str_byte_line))