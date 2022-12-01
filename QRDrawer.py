import numpy as np
from PIL import Image
from QRTables import leveling_pattern_positions, version_codes
from QRCode import QRCodeL


def get_bigramms(arr):
    res= []
    for i in range(len(arr)):
        for j in range(len(arr)):
            res.append([arr[i], arr[j]])
    return res


def b():
    return np.zeros((1,3))


def w():
    return np.ones((1,3))

def grey():
    return np.ones((1,3)) * 0.5

class QRDrawer:
    def __init__(self, code, version, filename):

        canv = self._get_canvas_by_version(version)
        lvl = self.get_leveling_pattern()
        fnd = self.get_finding_pattern()

        self.place_finding_patterns(canv)
        self.place_leveling_patterns(canv, version)
        self.place_synch_lines(canv)

        if version >=7:
            self.place_and_parse_version_code(canv,version)

        self.place_mask_codes(canv)


        code = self.prep_msg(canv,code)

        self.traverse(canv,code)
        canv = self.add_padding(canv)
        self.save_image(canv, filename)
        return



    def prepare_data(self,canv):
        for i in range(canv.shape[0], 9,-1):
            for j in range (canv.shape[1]):
                return
        res = [[canv.shape[1]-1, canv.shape[0]-1, np.array([255,100,255])]]
        return res


    def place_leveling_patterns(self, canv, version):
        positions = leveling_pattern_positions[version]
        positions = get_bigramms(positions)

        for pos in positions:
            if  (pos[0]-3 in range(0,9) and pos[1]-3 in range(0,9)) or\
                (pos[0]+3 in range(canv.shape[0]-9, canv.shape[0]) and pos[1]-3 in range(0,9)) or \
                (pos[0] - 3 in range(0,9) and pos[1]+3 in range(canv.shape[1]-9, canv.shape[1])):
                continue

            lvl = self.get_leveling_pattern()
            self.place_at(canv, lvl, pos[0]-2,pos[1]-2)

        return canv

    def place_synch_lines(self,canv):
        i=8
        delta = 6
        while i< canv.shape[0]-7:
            if canv[delta,i][0]==0:
                i+=5
                continue
            canv[delta,i] = b() if i%2==0 else w()
            i+=1
        i=8
        while i< canv.shape[1]-7:
            if canv[i,delta][0]==0:
                i+=5
                continue
            canv[i,delta] = b() if i%2==0 else w()
            i+=1

        return canv

    def place_and_parse_version_code(self, canv, version):
        lines = version_codes[version]
        pattern1 = np.zeros((3,6,3))
        pattern2 = np.zeros((6,3,3))

        for i in range(len(lines)):
            for j in range(len(lines[i])):
                color = b if lines[i][j]=='1' else w
                pattern1[i, j] = color()
                pattern2[j, i] = color()

        self.place_at(canv,pattern1,canv.shape[1]-11,0)
        self.place_at(canv,pattern2, 0,canv.shape[0]-11)
        return canv

    def _get_canvas_by_version(self, version):
        start = 21
        size = 21+ 4*(version-1)
        canv = np.ones((size,size,3))*0.5
        ''''''
        self.canvas = canv
        return canv

    def place_mask_codes(self,canv):
        canv = self._place_mask_codes_first(canv)
        canv = self._place_mask_codes_sec(canv)
        return canv


    def _place_mask_codes_sec(self, canv):
        mask_id =0
        mask_code ='111011111000100'
        for i in range(0,7):
            col = b if mask_code[i]=='1' else w
            canv[canv.shape[1]-1-i,8] = col()

        canv[canv.shape[1]-1-7,8] = b()

        c = canv.shape[0] - 8
        for i in range(7,len(mask_code)):
            col = b if mask_code[i]=='1' else w
            canv[8,c] = col()
            c+=1
        return canv

    def _place_mask_codes_first(self,canv):

        mask_id =0
        mask_code = '111011111000100'
        for i in range(0,6):
            col = b if mask_code[i]=='1' else w
            canv[8,i] = col()

        col = b if mask_code[6] == '1' else w
        canv[8, 7] = col()
        col = b if mask_code[7] == '1' else w
        canv[8, 8] = col()
        col = b if mask_code[8] == '1' else w
        canv[7, 8] = col()

        for i in range(9,len(mask_code)):
            col = b if mask_code[i]=='1' else w
            canv[len(mask_code)-i-1,8] = col()
        return canv

    def place_at(self, canvas, pattern,x,y):
        canvas[x:x+pattern.shape[0], y:y+pattern.shape[1]] = pattern
        return canvas

    def get_leveling_pattern(self):
        pattern = np.zeros((5,5,3))
        pattern[1:4,1:4] = w()
        pattern[2,2] = b()
        return pattern

    def get_finding_pattern(self):
        pattern = np.zeros((7,7,3))
        pattern[1:6,1:6] = w()
        pattern[2:5,2:5] = b()
        return pattern
        #self.save_image(pattern)

    def place_finding_patterns(self, canv):
        pattern = self.get_finding_pattern()
        self.place_at(canv, pattern,0,0)
        self.place_at(canv, pattern, 0, canv.shape[1]-7)
        self.place_at(canv, pattern,canv.shape[1]-7,0)
        canv[:8,7] = w()
        canv[7,:8] = w()
        canv[canv.shape[0] -8, :8] = w()
        canv[7,canv.shape[1] -8:] = w()
        canv[:8,canv.shape[0] -8] = w()
        canv[canv.shape[0]-7:,7] = w()

    def save_image(self, canv, filname):
        im = Image.fromarray((canv*255).astype(np.uint8))
        im.save(filname)

    def prep_msg(self,canv,code):
        empty_cnt = 0
        #print(code)
        for i in range(canv.shape[0]):
            for j in range(canv.shape[1]):
                if canv[i,j][0]==0.5:
                    empty_cnt+=1
        code+='0'*(empty_cnt-len(code))
        #print(code)
        return code

    def traverse(self,canv,code):
        col_dir = True #true - up, false - down
        index=0
        for coll in range(canv.shape[1]-1, -1,-2):
            if coll<=7:
                col=coll-1
            else:
                col=coll
            if col_dir:
                for row in range(canv.shape[0]-1,-1,-1):
                    if canv[row,col][0]==0.5:
                        canv[row,col]=self.get_pix_color_with_mask(row,col,code[index])
                        index+=1
                    if canv[row,col-1][0]==0.5:
                        canv[row,col-1]=self.get_pix_color_with_mask(row,col-1,code[index])
                        index+=1
            else:
                for row in range(0,canv.shape[0]):
                    if canv[row,col][0]==0.5:
                        canv[row,col]=self.get_pix_color_with_mask(row,col,code[index])
                        index+=1
                    if canv[row,col-1][0]==0.5:
                        canv[row, col-1]=self.get_pix_color_with_mask(row,col-1,code[index])
                        index+=1
            col_dir = not col_dir

    def get_pix_color_with_mask(self,col,row, bit):
        mask = (col+row) %2 ==0
        color = 'b' if bit=='1' else 'w'
        if mask:
           color = 'w' if color=='b' else 'b'
        return b() if color=='b' else w()

    def add_padding(self,canv,pad_size=4):
        res = np.ones((canv.shape[0]+pad_size*2,canv.shape[1]+pad_size*2,3))
        #res[pad_size-1:canv.shape[0],pad_size-1:canv.shape[0] ] = canv
        canv = self.place_at(res,canv,pad_size,pad_size)
        return canv


