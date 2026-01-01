import json
import os
import cv2
import time


def check():
    global option, listVideoAudio, listAudioLatino, listSubFull, listSubSign, listAttachments, optionAudio, optionSub, optionLat
    optionStringAudio = input("Elija su pista de Audio(Por defecto 1) ").rstrip().lstrip()
    optionAudio = int('1' if optionStringAudio == "" else optionStringAudio)
    optionStringSub = input("Elija su pista de Subtitulo(Por defecto 2) ").rstrip().lstrip()
    optionSub = int('2' if optionStringSub == "" else optionStringSub)
    optionStringLat = input("Elija su pista de AudioLat(Por defecto 1) ").rstrip().lstrip()
    optionLat = int('1' if optionStringLat == "" else optionStringLat)
    option = int(input(
        f'\nmkvextractor (MKVToolNix : mkvextract)\
        \n|TEN MUCHO CUIDADO CON LAS DIMENSIONES\
        \n|-- 1 : (Video-Audio-Subs)\
        \n|-- 2 : (Video-Audio) - (Video-Audio-Subs)\
        \n|-- 3 : (Video-Audio) - (Sub-Full) - (Attachments)\
        \n|-- 4 : (Video-Audio) - (Sub-Full) - (Audio_Lat)\
        \n|-- 5 : (Video-Audio) - (Sub-Full) - (Audio_Lat) - (Sub_Sign) - (Attachments)\
        \n|-- 6 : (Video-Audio-SubFull) - (Audio_Lat)\
        \n|-- 7 : (Video-AudioJap-AudioLat-SubFull)\
        \n|-- 8 : (Video-Audio-Subs-Attachments)\
        \n\
        \nextractMode: '
    ))

    match option:
        case 1:
            return True
        case 2:
            return len(listVideoAudio) == len(listSubFull)
        case 3:
            return len(listVideoAudio) == len(listSubFull) and len(listSubFull) == len(listAttachments)
        case 4:
            return len(listVideoAudio) == len(listSubFull) and len(listSubFull) == len(listAudioLatino)
        case 5:
            return len(listVideoAudio) == len(listSubFull) and len(listSubFull) == len(listAudioLatino) and len(listAudioLatino) == len(listSubSign) and len(listSubSign) == len(listAttachments)
        case 6:
            return len(listVideoAudio) == len(listAudioLatino)
        case 7:
            return True
        case 8:
            return True
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
            for fileVA in listVideoAudio:
                pathVA = roothVideoAudio + "\\" + fileVA
                vid = cv2.VideoCapture(pathVA)
                pathVA = pathVA.replace('\\','\\\\')
                pathResult = roothResult + "\\" + fileVA

                height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

                arr = json.load(open('options1X.json'))
                tamarr = len(arr)
                i = 0
                countFind = 1

                f = open("options1.json", "w", encoding="utf-8")
                f.write('[\n')
                for a in arr:
                    i = i + 1
                    if a.find(mark) >= 0:
                        if countFind == 2:
                            a = a.replace(mark,str(width) + "x" + str(height))
                        if countFind == 10:
                            a = a.replace(mark,pathVA)
                        if countFind == 1 or countFind == 6 or countFind == 7 or countFind == 8 or countFind == 9:
                            a = a.replace(mark,str(optionSub))
                        if countFind == 3 or countFind == 4 or countFind == 5:
                            a = a.replace(mark, str(optionAudio))
                        if countFind == 11:
                            a = "0:0,0:" + str(optionAudio) + ",0:" + str(optionSub)

                        countFind = countFind + 1
                    if tamarr == i:
                        line = '"' + a + '"\n'
                    else:
                        line = '"' + a + '",\n'
                    f.write(line)
                f.write(']')
                f.close()

                os.system(r'mkvmerge.exe @options1.json -o "' + pathResult + '"')
                time.sleep(30)
        case 2:
            j = 0
            for fileVA in listVideoAudio:
                pathVA = roothVideoAudio + "\\" + fileVA
                vid = cv2.VideoCapture(pathVA)
                pathVA = pathVA.replace('\\', '\\\\')
                pathResult = roothResult + "\\" + fileVA
                pathSub = (roothSubFull + "\\" + listSubFull[j]).replace('\\', '\\\\')
                height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

                arr = json.load(open('options2X.json'))
                tamarr = len(arr)
                i = 0
                countFind = 1

                f = open("options2.json", "w", encoding="utf-8")
                f.write('[\n')
                for a in arr:
                    i = i + 1
                    if a.find(mark) >= 0:
                        if countFind == 1 or countFind == 3 or countFind == 4 or countFind == 5:
                            a = a.replace(mark, str(optionAudio))
                        if countFind == 2:
                            a = a.replace(mark, str(width) + "x" + str(height))
                        if countFind == 6:
                            a = a.replace(mark, pathVA)
                        if countFind == 7 or countFind == 8 or countFind == 9 or countFind == 10 or countFind == 11:
                            a = a.replace(mark, str(optionSub))
                        if countFind == 12:
                            a = a.replace(mark, pathSub)
                        if countFind == 13:
                            a = "0:0,0:" + str(optionAudio) + ",1:" + str(optionSub)

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
                vid = cv2.VideoCapture(pathVA)
                pathVA = pathVA.replace('\\', '\\\\')
                pathResult = roothResult + "\\" + fileVA
                pathSub = (roothSubFull + "\\" + listSubFull[j]).replace('\\', '\\\\')
                pathAttachments = (roothAttachments + "\\" + listAttachments[j]).replace('\\', '\\\\')
                height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

                arr = json.load(open('options3X.json'))
                tamarr = len(arr)
                i = 0
                countFind = 1

                f = open("options3.json", "w", encoding="utf-8")
                f.write('[\n')
                for a in arr:
                    i = i + 1
                    if a.find(mark) >= 0:
                        if countFind == 2:
                            a = a.replace(mark, str(width) + "x" + str(height))
                        if countFind == 1 or countFind == 3 or countFind == 4 or countFind == 5:
                            a = a.replace(mark, str(optionAudio))
                        if countFind == 8 or countFind == 9 or countFind == 10 or countFind == 11:
                            a = a.replace(mark, str(optionSub))
                        if countFind == 6:
                            a = a.replace(mark, pathVA)
                        if countFind == 7:
                            a = a.replace(mark, pathAttachments)
                        if countFind == 12:
                            a = a.replace(mark, pathSub)
                        if countFind == 13:
                            a = "0:0,0:" + str(optionAudio) + ",2:" + str(optionSub)

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
        case 4:
                j = 0
                for fileVA in listVideoAudio:
                    pathVA = roothVideoAudio + "\\" + fileVA
                    vid = cv2.VideoCapture(pathVA)
                    pathVA = pathVA.replace('\\', '\\\\')
                    pathResult = roothResult + "\\" + fileVA
                    pathSub = (roothSubFull + "\\" + listSubFull[j]).replace('\\', '\\\\')
                    pathLat = (roothAudioLatino + "\\" + listAudioLatino[j]).replace('\\', '\\\\')
                    height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

                    arr = json.load(open('options4X.json'))
                    tamarr = len(arr)
                    i = 0
                    countFind = 1

                    f = open("options4.json", "w", encoding="utf-8")
                    f.write('[\n')
                    for a in arr:
                        i = i + 1
                        if a.find(mark) >= 0:
                            if countFind == 2:
                                a = a.replace(mark, str(width) + "x" + str(height))
                            if countFind == 1 or countFind == 3 or countFind == 4 or countFind == 5:
                                a = a.replace(mark, str(optionAudio))
                            if countFind == 7 or countFind == 8 or countFind == 9 or countFind == 10:
                                a = a.replace(mark, str(optionLat))
                            if countFind == 6:
                                a = a.replace(mark, pathVA)
                            if countFind == 11:
                                a = a.replace(mark, pathLat)
                            if (countFind == 12 or countFind == 13 or countFind == 14 or countFind == 15 or
                                    countFind == 16):
                                a = a.replace(mark, str(optionSub))
                            if countFind == 17:
                                a = a.replace(mark, pathSub)
                            if countFind == 18:
                                a = "0:0,0:" + str(optionAudio) + ",1:" + str(optionLat) + ",2:" + str(optionSub)

                            countFind = countFind + 1
                        if tamarr == i:
                            line = '"' + a + '"\n'
                        else:
                            line = '"' + a + '",\n'
                        f.write(line)
                    f.write(']')
                    f.close()

                    os.system(r'mkvmerge.exe @options4.json -o "' + pathResult + '"')
                    j = j + 1
                    time.sleep(30)
        case 5:
            return len(listVideoAudio) == len(listSubFull) and len(listSubFull) == len(listAudioLatino) and len(listAudioLatino) == len(listSubSign) and len(listSubSign) == len(listAttachments)
        case 6:
            return len(listVideoAudio) == len(listAudioLatino)
        case 7:
            for fileVA in listVideoAudio:
                pathVA = roothVideoAudio + "\\" + fileVA
                vid = cv2.VideoCapture(pathVA)
                pathVA = pathVA.replace('\\','\\\\')
                pathResult = roothResult + "\\" + fileVA

                height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

                arr = json.load(open('options7X.json'))
                tamarr = len(arr)
                i = 0
                countFind = 1

                f = open("options1.json", "w", encoding="utf-8")
                f.write('[\n')
                for a in arr:
                    i = i + 1
                    if a.find(mark) >= 0:
                        if countFind == 2:
                            a = a.replace(mark,str(width) + "x" + str(height))
                        if countFind == 10:
                            a = a.replace(mark,pathVA)
                        if countFind == 1 or countFind == 6 or countFind == 7 or countFind == 8 or countFind == 9:
                            a = a.replace(mark,str(optionSub))
                        if countFind == 3 or countFind == 4 or countFind == 5:
                            a = a.replace(mark, str(optionAudio))
                        if countFind == 11:
                            a = "0:0,0:" + str(optionAudio) + ",0:" + str(optionSub)

                        countFind = countFind + 1
                    if tamarr == i:
                        line = '"' + a + '"\n'
                    else:
                        line = '"' + a + '",\n'
                    f.write(line)
                f.write(']')
                f.close()

                os.system(r'mkvmerge.exe @options1.json -o "' + pathResult + '"')
                time.sleep(30)
        case 8:
            return True


option = 0
optionAudio = 0
optionSub = 0
optionLat = 0
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
