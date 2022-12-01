import qrcode
from PIL import Image
import numpy as np
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    mask_pattern=0
)


qr.add_data('fly me to the moon')
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")


img.save('canvaaaaaa.bmp')