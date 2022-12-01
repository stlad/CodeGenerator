from QRTables import polinoms, Gauls_Pole,ReverseGaulsField
from copy import copy

class QRCodeL:
    '''QR код уровня коррекции L (допускает до 7% потерь)'''
    def __init__(self):
        self.codetabe = [s for s in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"]
        self.L_version_size = [152,272,440,640,864,1088,1248,1550,1856,2192,
                               2592,2960,3424,3688,4184,4712,5176,5768,6360,6888,7456,8048,8752,
                               9392,10208,10960,11744,12248,13048,13880,
                               14744,15640,16568,17528,18448,19472,20528,21616,22496,23648] # [количество бит] индекс+1 - версия

    def Encode(self, msg):
        size = len(msg)
        #code = self._get_code_by_bigramms(msg)
        code= self._byte_coding(msg)
        self.version = self._get_qrversion(code)
        if self.version>40:
            print('НЕ поддерживается версия больше 40овой')
            return
        code = self._add_encoding_method(code, size)
        code = self._fill_to_mod_8(code)
        www = len(code)

        code = self._fill_to_version_req(code)
        self.raw_code = copy(code)
        block_cnt = self._get_block_count(self.version)
        block_sizes = self._get_block_sizes(code, block_cnt)
        blocks = self._fill_blocks(code, block_sizes)
        cor_bytes_cnt, correction_polinom = self._get_correction_polinom(self.version)
        byte_blocks = self._blocks_to_byte_arrays(blocks)
        inf_bytes, cor_bytes = self._get_corrected_blocks(byte_blocks, correction_polinom, cor_bytes_cnt)
        self.byteline = self._blocks_to_byte_line(inf_bytes,cor_bytes)


        self.str_byte_line = [ '0'*(8-len(bin(num)[2:]))+bin(num)[2:]   for num in self.byteline]
        res = ''.join(self.str_byte_line)
        return res

    def _byte_coding(self,msg):
        res = []

        msg= bytes(msg, encoding="utf8")
        for i in msg:
            res.append('0'*(8-len(bin(i)[2:])) + bin(i)[2:])
        return ''.join(res)


    def _get_code_by_bigramms(self, msg):
        res = []
        for i in range(0,len(msg),2):
            if i+1 <  len(msg):
                code =self.codetabe.index(msg[i]) * 45 + self.codetabe.index(msg[i+1])
            else:
                code = self.codetabe.index(msg[i])

            strcode = '0'*(11-len(bin(code)[2:]))+bin(code)[2:] if  i+1<len(msg) else '0'*(6-len(bin(code)[2:]))+bin(code)[2:]
            res.append(strcode)
        return ''.join(res)

    def _get_qrversion(self,binmsg):
        size = len(binmsg)
        for i in range(len(self.L_version_size)):
            if self.L_version_size[i] > size:
                return i+1

    def _add_encoding_method(self, binmsg, size):
        oldmsg = copy(binmsg)
        bit_window = self._get_bit_window_by_version()
        s = len(binmsg)
        binbytesize = bin(size)[2:]
        binbytesize = '0'*(bit_window-len(binbytesize))+binbytesize
        result = '0100'+ binbytesize + str(binmsg)  #Так как использую побайтовое кодирование
        s=len(result)
        if len(result) <= self.L_version_size[self.version-1]:
            return result
        self.version+=1
        bit_window = self._get_bit_window_by_version()
        binbytesize = bin(size)[2:]
        binbytesize = '0' * (bit_window - len(binbytesize)) + binbytesize
        return '0100'+ binbytesize + str(binmsg)


    def _get_bit_window_by_version(self):
        if self.version in range(1,9):
            bit_window = 8
        elif self.version in range(10,27):
            bit_window = 16
        else:
            bit_window = 16
        return bit_window

    def _fill_to_mod_8(self, binmsg):
        s = len(binmsg)
        if len(binmsg)%8==0:
            return binmsg
        left_bit_count = 8-(len(binmsg)%8)
        return binmsg+'0'*left_bit_count

    def _fill_to_version_req(self,binmsg):
        fill_bytes = ['11101100', '00010001']
        size = len(binmsg)
        size_needed = self.L_version_size[self.version-1]
        for i in range(0, int((size_needed-size)/8)):
            binmsg += fill_bytes[i%2]
            s=len(binmsg)

        return binmsg

    def _get_block_count(self, version):
        '''Выделяем нужное количество блоков'''
       # print(version)
        table = [1,1,1,1,1,2,2,2,2,4,4,4,4,4,6,6,6,6,7,8,8,9,9,10,12,12,12,13,14,15,16,17,18,19,19,20,21,22,24,25]
        #print(table[version-1])
        return table[version-1]

    def _get_block_sizes(self, msg, block_count):
        bit_size = len(msg)
        byte_size = bit_size / 8
        bytes_per_block = int(byte_size / block_count)
        added_blocks_cnt = byte_size % block_count
        block_sizes = [bytes_per_block for i in range(block_count)]
        for i in range(int(added_blocks_cnt)):
            block_sizes[-1-i]+=1
        return block_sizes

    def _fill_blocks(self,code, block_sizes):
        res = []
        code_copy = code

        for i in range(len(block_sizes)):
            a = block_sizes[i]*8-1
            res.append(code_copy[0:block_sizes[i]*8]) # убрал отсюда -1
            code_copy = code_copy[block_sizes[i]*8:]

        return res

    def _get_correction_polinom(self, version):
        correction_bytes_from_version = [7,10,15,20,26,18,20,24,30,18,20,24,26,30,22,24,28,30,28,28,28,28,30,30,26,28,30,30,30,30,30,30,30,30,30,30,30,30,30,30]
        correction_bytes = correction_bytes_from_version[version-1]
        return correction_bytes,polinoms[correction_bytes]

    def _blocks_to_byte_arrays(self, blocks):
        res = []
        for block in blocks:
            byte_block=[]
            for i in range(0,len(block),8):
                s = len(block)
                byte = block[i:i+8]
                byte = int(byte,base=2)
                byte_block.append(byte)
            res.append(byte_block)
        return res

    def _get_corrected_blocks(self, blocks, polinom, cor_bytes_cnt):
        inf_blocks_in_line = []
        cor_blocks_in_line = []
        for block in blocks:
            prep_block = copy(block)
            inf_byte_cnt = len(prep_block)

            prep_block+=[0]*(max(len(prep_block), cor_bytes_cnt)-len(prep_block))
            inf_blocks_in_line.append(copy(prep_block))

            for i in range(inf_byte_cnt):
                if cor_bytes_cnt != len(prep_block): #ДОБИТЬ БЛОК НУЛЯМИ, если он слишком мал для байтов коррекции
                    prep_block+=[0]*(cor_bytes_cnt-len(prep_block))

                a = prep_block[0]
                prep_block= prep_block[1:]
                prep_block+=[0]
                if a==0:
                    continue
                b = ReverseGaulsField[a]
                for j in range(cor_bytes_cnt):
                    v = (polinom[j]+b)%255
                    prep_block[j]= prep_block[j] ^ Gauls_Pole[v]
            cor_blocks_in_line.append(copy(prep_block))
        return inf_blocks_in_line, cor_blocks_in_line


    def _blocks_to_byte_line(self, inf, cor):
        resline = []
        for i in range(len(inf[0])):
            for j in range(len(inf)):
                resline.append(inf[j][i])

        for i in range(len(cor[0])):
            for j in range(len(cor)):
                if cor[j][i]==0:
                    continue
                resline.append(cor[j][i])
        return resline
