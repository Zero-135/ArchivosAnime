import os
from deep_translator import GoogleTranslator
import pysubs2

def main():
    optionStringSub = input("Elija la cantidad de segundos en adelantar o retroceder ").rstrip().lstrip()
    optionSub = float('0' if optionStringSub == "" else optionStringSub)
    option = int(input(
        f'\nPysubs2\
            \n|-- 1 : Traducir\
            \n|-- 2 : Adelantar-Avanzar\
            \n\
            \nextractMode: '
    ))

    match option:
        case 1:
            translator = GoogleTranslator(source='auto', target='es')
            for fileSub in os.scandir(roothSubFull):
                lines = pysubs2.load(fileSub.path, encoding="utf-8")
                for line in lines:
                    line.text = translator.translate(line.text)
                lines.save(roothResult + "\\" + fileSub.name)
        case 2:
            for fileSub in os.scandir(roothSubFull):
                lines = pysubs2.load(fileSub.path, encoding="utf-8")
                lines.shift(s=optionSub)
                lines.sort()
                lines.save(roothResult + "\\" + fileSub.name)


rooth = r"C:\Users\Walter Rivas\Documents\FilesTransform"
roothSubFull = rooth + r"\3.-Sub-Full"
roothResult = rooth + r"\6.-Result"
listSub = sorted(os.listdir(roothSubFull))

main()