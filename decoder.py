from main import *
import sys
import bitarray
import json

z = bitarray.bitarray()
stored_dic = True

if len(sys.argv) > 2:
    print("You provided too many arguments.. ABORTING!")
else:
    if sys.argv[1][-3:] != '.lz':
        print(f"{sys.argv[1]} is not an lz file.. ABORTING!")
    else:
        try:
            in_file = open(f"{sys.argv[1]}", "rb")
            z.fromfile(in_file)
            in_file.close()
        except:
            print("Error reading the file, are you sure this is the right path?.. ABORTING!")

        try:
            with open(f'./Models/{(sys.argv[1].split("/")[-1]).split(".")[0]}_model', "r") as modFile:
                stored_dic = json.loads(modFile.read())
            modFile.close()
        except:
            print("Error Occurred while loading the model for this file, please encode it again and try to decode; do not mess with the Models directory.")

        BitStreamLength = stored_dic.pop('<esc>')
        codesize = stored_dic.pop('<len_code>')
        code = []
        for x in z[0:codesize - len(z)]:
            code.append(1 if x else 0)

        message = decode(code, stored_dic, BitStreamLength)

        outPut = ""
        for m in message:
            outPut += m

        with open(f'./{(sys.argv[1].split("/")[-1]).split(".")[0]}-decoded.tex', "w") as modFile:
            modFile.write(outPut)
        modFile.close()
