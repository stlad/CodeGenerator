import json


class Code128:
    def __init__(self):
        self.msg = ''
        self.End =    [[int(i) for i in  '1100011101011'],106]
        self.StartA = [[int(i) for i in  '11010000100'],103]
        self.StartB = [[int(i) for i in  '11010010000'],104]
        self.StartC = [[int(i) for i in  '11010011100'],105]
        self.Empty = [0,0,0,0,0,0,0]

        with open("chartB.json", "r") as read_file:
            self.chartB = json.load(read_file)

        for index, key in enumerate(self.chartB):
            num = [int(i) for i in  self.chartB[key]]
            self.chartB[key] = [num, index]



    def Encode(self, msg):
        code = [] + self.Empty
        code += self.StartB[0]
        contrl_sum = self.StartB[1]
        for index, symb in enumerate(msg):
            code += self.chartB[symb][0]
            contrl_sum += (index+1) * self.chartB[symb][1]
        contrl_sum %= 103

        for key in self.chartB:
            if self.chartB[key][1] == contrl_sum:
                code+=self.chartB[key][0]
                break


        #for digit in str(contrl_sum):
        #   code+=self.chartB[digit][0]

        code += self.End[0]
        code += self.Empty
        return code


import numpy as np
from PIL import Image
from code128 import *
import copy


coder = Code128()
code = coder.Encode("Fly me to the moon")

def DrawCode128(code):
    code = np.array(code)
    height = 100
    new = np.ones((3, height, code.shape[0]))
    b = new * code
    bb = b.transpose(1, 2, 0)
    im = Image.fromarray(((bb-1) * (-255)).astype(np.uint8))
    img = im.resize((bb.shape[1]*2, bb.shape[0]*2))
    img.save('res.bmp')

DrawCode128(code)