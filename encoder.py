from main import *
import bitarray
import sys
import json


if len(sys.argv) > 2:
    print("You provided too many arguments.. ABORTING!")
else:

    if sys.argv[1][-4:] != '.tex':
        print(f"{sys.argv[1]} is not a Latex file.. ABORTING!")

    else:

        try:
            Preprocessing(sys.argv[1])
        except:
            print("Error opening file, are you sure your path is correct?.. ABORTING!")

        list_of_strings.append('ø')

        BitStreamLength = 0
        stored_dic = {}
        count = 0
        for x in PPM_Trie:
            if x in list_of_strings:
                freq = list_of_strings.count(x)
                count += freq
                stored_dic[x] = [freq, count]
                BitStreamLength += freq

        stored_dic['<esc>'] = BitStreamLength
        code = encode(list_of_strings, stored_dic, BitStreamLength)
        stored_dic['<len_code>'] = len(code)

        with open(f'./Models/{(sys.argv[1].split("/")[-1]).split(".")[0]}_model', "w") as modFile:
            modFile.write(json.dumps(stored_dic))
        modFile.close()

        bin = bitarray.bitarray(code)
        out_file = open(f'{(sys.argv[1].split("/")[-1]).split(".")[0]}.lz', "wb")
        out_file.write(bin)
        out_file.close()

        print(f'{len(code) / 8} Bytes used to encode {(sys.argv[1].split("/")[-1]).split(".")[0]}.tex')
