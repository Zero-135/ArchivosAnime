import json
import os
import time


def check():
    global option, listVideoAudio, listAudioLatino, listSubFull, listSubSign, listAttachments, \
            optionAudio, optionSub, optionLat, optionSubSign
    optionStringAudio = input("Elija su pista de Audio(Por defecto 1) ").rstrip().lstrip()
    optionAudio = int('1' if optionStringAudio == "" else optionStringAudio)
    optionStringSub = input("Elija su pista de Subtitulo(Por defecto 2) ").rstrip().lstrip()
    optionSub = int('2' if optionStringSub == "" else optionStringSub)
    optionStringLat = input("Elija su pista de AudioLat(Por defecto 1) ").rstrip().lstrip()
    optionLat = int('1' if optionStringLat == "" else optionStringLat)
    optionStringSubSign = input("Elija su pista de SubtituloSign(Por defecto 1) ").rstrip().lstrip()
    optionSubSign = int('1' if optionStringSubSign == "" else optionStringSubSign)
    option = int(input(
        f'\nmkvextractor (MKVToolNix : mkvextract)\
        \n|-- 1 : (Video-Audio) - (Sub-Full) - (Attachments)\
        \n|-- 2 : (Video-Audio) - (Sub-Full) - (Audio_Lat) - (Attachments)\
        \n|-- 3 : (Video-Audio) - (Sub-Full) - (Audio_Lat) - (Sub_Sign) - (Attachments)\
        \n\
        \nextractMode: '
    ))

    match option:
        case 1:
            return len(listVideoAudio) == len(listSubFull) and len(listSubFull) == len(listAttachments)
        case 2:
            return (len(listVideoAudio) == len(listSubFull) and len(listSubFull) == len(listAttachments)
                    and len(listAttachments) == len(listAudioLatino))
        case 3:
            return (len(listVideoAudio) == len(listSubFull) and len(listSubFull) == len(listAttachments)
                    and len(listAttachments) == len(listAudioLatino) and len(listAudioLatino) == len(listSubSign))
        case _:
            print("Error: Opcion No encontrada")
            return False


def main():
    global option
    if not check():
        print("La cantidad de archivos no coincide")
        return

    mark = "XXXXXXXXXXXXXXXX"
    match option:
        case 1:
            j = 0
            for fileVA in listVideoAudio:
                pathVA = roothVideoAudio + "\\" + fileVA
                pathVA = pathVA.replace('\\', '\\\\')
                pathResult = roothResult + "\\" + fileVA
                pathSub = (roothSubFull + "\\" + listSubFull[j]).replace('\\', '\\\\')
                pathAttachments = (roothAttachments + "\\" + listAttachments[j]).replace('\\', '\\\\')

                arr = json.load(open('options1Y.json'))
                tamarr = len(arr)
                i = 0
                countFind = 1

                f = open("options1.json", "w", encoding="utf-8")
                f.write('[\n')
                for a in arr:
                    i = i + 1
                    if a.find(mark) >= 0:
                        if countFind == 1 or countFind == 2:
                            a = a.replace(mark, str(optionAudio))
                        if countFind == 5 or countFind == 6:
                            a = a.replace(mark, str(optionSub))
                        if countFind == 3:
                            a = a.replace(mark, pathVA)
                        if countFind == 4:
                            a = a.replace(mark, pathAttachments)
                        if countFind == 7:
                            a = a.replace(mark, pathSub)
                        if countFind == 8:
                            a = "0:0,0:" + str(optionAudio) + ",2:" + str(optionSub)

                        countFind = countFind + 1
                    if tamarr == i:
                        line = '"' + a + '"\n'
                    else:
                        line = '"' + a + '",\n'
                    f.write(line)
                f.write(']')
                f.close()

                os.system(r'mkvmerge.exe @options1.json -o "' + pathResult + '"')
                j = j + 1
                time.sleep(30)
        case 2:
            j = 0
            for fileVA in listVideoAudio:
                pathVA = roothVideoAudio + "\\" + fileVA
                pathVA = pathVA.replace('\\', '\\\\')
                pathResult = roothResult + "\\" + fileVA
                pathSub = (roothSubFull + "\\" + listSubFull[j]).replace('\\', '\\\\')
                pathAttachments = (roothAttachments + "\\" + listAttachments[j]).replace('\\', '\\\\')
                pathAudioLat = (roothAudioLatino + "\\" + listAudioLatino[j]).replace('\\', '\\\\')

                arr = json.load(open('options2Y.json'))
                tamarr = len(arr)
                i = 0
                countFind = 1

                f = open("options2.json", "w", encoding="utf-8")
                f.write('[\n')
                for a in arr:
                    i = i + 1
                    if a.find(mark) >= 0:
                        if countFind == 1 or countFind == 2:
                            a = a.replace(mark, str(optionAudio))
                        if countFind == 3:
                            a = a.replace(mark, pathVA)
                        if countFind == 4 or countFind == 5:
                            a = a.replace(mark, str(optionLat))
                        if countFind == 6:
                            a = a.replace(mark, pathAudioLat)
                        if countFind == 7 or countFind == 8:
                            a = a.replace(mark, str(optionSub))
                        if countFind == 9:
                            a = a.replace(mark, pathSub)
                        if countFind == 10:
                            a = a.replace(mark, pathAttachments)
                        if countFind == 11:
                            a = "0:0,0:" + str(optionAudio) + ",1:" + str(optionLat) + ",2:" + str(optionSub)

                        countFind = countFind + 1
                    if tamarr == i:
                        line = '"' + a + '"\n'
                    else:
                        line = '"' + a + '",\n'
                    f.write(line)
                f.write(']')
                f.close()

                os.system(r'mkvmerge.exe @options2.json -o "' + pathResult + '"')
                j = j + 1
                time.sleep(30)
        case 3:
            j = 0
            for fileVA in listVideoAudio:
                pathVA = roothVideoAudio + "\\" + fileVA
                pathVA = pathVA.replace('\\', '\\\\')
                pathResult = roothResult + "\\" + fileVA
                pathSub = (roothSubFull + "\\" + listSubFull[j]).replace('\\', '\\\\')
                pathAttachments = (roothAttachments + "\\" + listAttachments[j]).replace('\\', '\\\\')
                pathAudioLat = (roothAudioLatino + "\\" + listAudioLatino[j]).replace('\\', '\\\\')
                pathSubSign = (roothSubSign + "\\" + listSubSign[j]).replace('\\', '\\\\')

                arr = json.load(open('options3Y.json'))
                tamarr = len(arr)
                i = 0
                countFind = 1

                f = open("options3.json", "w", encoding="utf-8")
                f.write('[\n')
                for a in arr:
                    i = i + 1
                    if a.find(mark) >= 0:
                        if countFind == 1 or countFind == 2:
                            a = a.replace(mark, str(optionAudio))
                        if countFind == 3:
                            a = a.replace(mark, pathVA)
                        if countFind == 4 or countFind == 5:
                            a = a.replace(mark, str(optionLat))
                        if countFind == 6:
                            a = a.replace(mark, pathAudioLat)
                        if countFind == 7 or countFind == 8:
                            a = a.replace(mark, str(optionSub))
                        if countFind == 9:
                            a = a.replace(mark, pathSub)
                        if countFind == 10 or countFind == 11:
                            a = a.replace(mark, str(optionSubSign))
                        if countFind == 12:
                            a = a.replace(mark, pathSubSign)
                        if countFind == 13:
                            a = a.replace(mark, pathAttachments)
                        if countFind == 14:
                            a = ("0:0,0:" + str(optionAudio) + ",1:" + str(optionLat) +
                                 ",2:" + str(optionSub) + ",3:" + str(optionSubSign))

                        countFind = countFind + 1
                    if tamarr == i:
                        line = '"' + a + '"\n'
                    else:
                        line = '"' + a + '",\n'
                    f.write(line)
                f.write(']')
                f.close()

                os.system(r'mkvmerge.exe @options3.json -o "' + pathResult + '"')
                j = j + 1
                time.sleep(30)


option = 0
optionAudio = 0
optionSub = 0
optionLat = 0
optionSubSign = 0
rooth = r"C:\Users\Walter Rivas\Documents\FilesTransform"
roothVideoAudio = rooth + r"\1.-Video-Audio"
roothAudioLatino = rooth + r"\2.-Audio-Latino"
roothSubFull = rooth + r"\3.-Sub-Full"
roothSubSign = rooth + r"\4.-Sub Sign"
roothAttachments = rooth + r"\5.-Attachments"
roothResult = rooth + r"\6.-Result"
listVideoAudio = sorted(os.listdir(roothVideoAudio))
listAudioLatino = sorted(os.listdir(roothAudioLatino))
listSubFull = sorted(os.listdir(roothSubFull))
listSubSign = sorted(os.listdir(roothSubSign))
listAttachments = sorted(os.listdir(roothAttachments))
main()
