from code128.code128 import Code128, DrawCode128
from qr.QRCode import  QRCodeL
from qr.QRDrawer import QRDrawer

texts =[
    'hello world',
    'fly me to the moon',
    'fly me to the moon and let me play along the stars',
    'https://www.youtube.com/watch?v=0SOyKENF5zg&ab_channel=TheodorBastard',
]


for index, text in enumerate(texts):
    coder = Code128()
    code = coder.Encode(text)
    DrawCode128(code, f'code128\{index}.jpg')


for index, text in enumerate(texts):
    coder = QRCodeL()
    code = coder.Encode(text)
    QRDrawer(code, coder.version,f'qr\{index}.bmp')
    print(f'Версия кода: {index}')