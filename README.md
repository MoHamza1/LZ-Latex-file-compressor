# Latex File compressor for L3 Codes and Cryptography
## 1. Uses Arithmetic encoding with Lempel-Ziv 
## 2. achieves compression rates of 9:1
## 3. Uses a novel pretrained language model, with inspiration from Google's BERT tokeniser used in State-of-the-art NLP tasks

# Running instructions
Do not delete the "Models" directory or any of its contents; the program will NOT WORK!

Your input file cannot contain this symbol "ø", the arithmetic decoder treats this as the end of file symbol.

Usage:

     python3 encoder.py <YOUR FILE PATH>
     python3 decoder.py <YOUR FILE PATH>

e.g. python3 encoder.py `./Example/long_Example.tex`


Any file is saved to the current directory, i.e. the one where these python scripts are.


Dependencies:

    import bitarray
    import json

I believe they are both in the python 3 standard library, if not definately pip instalable.
main.py is a dependency for encoder.py and decoder.py.



