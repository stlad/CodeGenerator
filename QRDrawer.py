import numpy as np
from PIL import Image
from QRTables import leveling_pattern_positions, version_codes



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

class QRDrawer:
    def __init__(self):
        version = 7
        canv = self._get_canvas_by_version(version)
        lvl = self.get_leveling_pattern()
        fnd = self.get_finding_pattern()

        #self.place_at(canv, lvl, 0,0)
        #self.place_at(canv, fnd, 10,10)
        self.place_finding_patterns(canv)
        self.place_leveling_patterns(canv, version)
        self.place_synch_lines(canv)

        if version >=7:
            self.place_and_parse_version_code(canv,version)

        self.place_mask_codes(canv)
        self.save_image(canv)
        return

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
                i+=6
                continue
            canv[delta,i] = b() if i%2==0 else w()
            i+=1
        i=8
        while i< canv.shape[1]-7:
            if canv[i,delta][0]==0:
                i+=6
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
        canv = np.ones((size,size,3))
        ''''''
        self.canvas = canv
        return canv

    def place_mask_codes(self,canv):
        canv = self._place_mask_codes_first(canv)
        canv = self._place_mask_codes_sec(canv)
        return canv


    def _place_mask_codes_sec(self, canv):
        mask_id =0
        mask_code = '111011111000100'
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
        #self.place_at(canv, pattern, 0, 0)



    def save_image(self, canv):
        im = Image.fromarray((canv*255).astype(np.uint8))
        print(canv.size)
        im.save('canv.jpg')


d  =QRDrawer()
#d.get_finding_pattern()