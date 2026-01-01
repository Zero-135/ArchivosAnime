import os
from pathlib import Path
import subprocess
from openpyxl import Workbook
import json


def check():
    global option, optionSub
    optionStringSub = input("Elija su pista de Extraccion(Por defecto 2) ").rstrip().lstrip()
    optionSub = int('2' if optionStringSub == "" else optionStringSub)
    option = int(input(
        f'\nmkvextractor (MKVToolNix : mkvextract)\
        \n|-- 1 : Extraer Tracks\
        \n|-- 2 : Listar Tracks con Nombres\
        \n\
        \nextractMode: '
    ))


def Options(roothVideoAudio):
    global option, optionSub, listaArchivosTotal

    match option:
        case 1:
            for fileVA in os.scandir(roothVideoAudio):
                name = fileVA.name
                path = fileVA.path

                if (name.find(".mkv") == -1 and name.find(".mp4") == -1 and name.find(".avi") == -1
                        and not os.path.isdir(path)):
                    continue

                if os.path.isdir(path):
                    if intoFolders:
                        Options(path)
                    else:
                        continue
                else:
                    pathVA = roothVideoAudio + "\\" + fileVA.name
                    pathVA = pathVA.replace('\\', '\\\\')
                    fileResult = roothSubFull + "\\" + Path(fileVA).stem
                    fileResult = fileResult.replace('\\', '\\\\')

                    resultado = subprocess.run(
                        r'mkvmerge.exe -J "' + pathVA + '" ',
                        capture_output=True,  # Captura la salida estándar (stdout)
                        text=True,  # Decodifica la salida a texto (en lugar de bytes)
                        check=True,  # Lanza una excepción si el proceso retorna un código de error
                        encoding='utf-8'
                    )

                    json_object = json.loads(resultado.stdout)
                    codec = checkTrackProperties(json_object, ["tracks", optionSub, "codec"])
                    extension = ""

                    match codec:
                        case "SubStationAlpha":
                            extension = ".ass"
                        case "SubRip/SRT":
                            extension = ".srt"
                        case "HDMV PGS":
                            extension = ".sup"

                    resultado = subprocess.run(
                        r'mkvextract.exe tracks "' + pathVA + '" ' +
                        str(optionSub) + ':"' + fileResult + '_track_' + str(optionSub) + extension + '"',
                        capture_output=True,  # Captura la salida estándar (stdout)
                        text=True,  # Decodifica la salida a texto (en lugar de bytes)
                        check=True,  # Lanza una excepción si el proceso retorna un código de error
                        encoding='utf-8'
                    )

        case 2:
            try:
                for fileVA in os.scandir(roothVideoAudio):
                    name = fileVA.name
                    path = fileVA.path

                    if (name.find(".mkv") == -1 and name.find(".mp4") == -1 and name.find(".avi") == -1
                            and not os.path.isdir(path)):
                        continue

                    if os.path.isdir(path):
                        if intoFolders:
                            Options(path)
                        else:
                            continue
                    else:
                        pathVA = roothVideoAudio + "\\" + name
                        pathVA = pathVA.replace('\\', '\\\\')

                        resultado = subprocess.run(
                            r'mkvmerge.exe -J "' + pathVA + '" ',
                            capture_output=True,  # Captura la salida estándar (stdout)
                            text=True,  # Decodifica la salida a texto (en lugar de bytes)
                            check=True,  # Lanza una excepción si el proceso retorna un código de error
                            encoding='utf-8'
                        )

                        json_object = json.loads(resultado.stdout)
                        listaArchivo = list()

                        listaArchivo.append(name)
                        for track in json_object["tracks"]:
                            trackjson = json.loads(json.dumps(track, indent=4))
                            listaArchivo.append("Track " + checkTrackProperties(trackjson,
                                                                                ["properties", "number"]) + " "
                                                + "[TID " + checkTrackProperties(trackjson, ["id"]) + "]"
                                                + "[" + checkTrackProperties(trackjson,
                                                                             ["type"]) + "]"
                                                + "[" + checkTrackProperties(trackjson,
                                                                             ["properties", "codec_id"]) + "]"
                                                + "[" + checkTrackProperties(trackjson,
                                                                             ["properties", "track_name"]) + "]"
                                                + "[" + checkTrackProperties(trackjson,
                                                                             ["properties", "language"]) + "]"
                                                )

                        for attach in json_object["attachments"]:
                            attachjson = json.loads(json.dumps(attach, indent=4))
                            listaArchivo.append("Attachment " + checkTrackProperties(attachjson, ["id"]) + " "
                                                + "[" + checkTrackProperties(attachjson, ["file_name"]) + "]"
                                                + "[" + checkTrackProperties(attachjson, ["content_type"]) + "]"
                                                + "[" + checkTrackProperties(attachjson, ["size"]) + " bytes]"
                                                )

                        listaArchivosTotal.append(listaArchivo)
            except NameError:
                print(NameError)


def getExcel():
    global listaArchivosTotal, nombreArchivo
    # Crear un libro de trabajo y una hoja de trabajo
    wb = Workbook()
    ws = wb.active
    ws.title = "Tracks"

    maximos = max([len(sublista) for sublista in listaArchivosTotal])
    listaRow = list()
    listaRow.append("Nombre")

    for i in range(maximos - 1):
        listaRow.append("Archivo " + str(i))

    ws.append(listaRow)
    for row in listaArchivosTotal:
        # row[0] = Path(row[0]).stem
        row[0] = row[0].split('\\')[-1].split("':")[0]
        ws.append(row)

    wb.save(nombreArchivo)
    os.system('"' + nombreArchivo + '"')


def checkTrackProperties(trackjson, array):
    long = len(array)
    try:
        match long:
            case 1:
                return str(trackjson[array[0]])
            case 2:
                return str(trackjson[array[0]][array[1]])
            case 3:
                return str(trackjson[array[0]][array[1]][array[2]])
    except:
        return ""


def main():
    check()
    Options(roothVideoAudio)
    match option:
        case 2:
            getExcel()


option = 0
optionSub = 0
intoFolders = False
rooth = r"C:\Users\Walter Rivas\Documents\FilesTransform"
roothVideoAudio = rooth + r"\1.-Video-Audio"
roothSubFull = rooth + r"\3.-Sub-Full"
roothResult = rooth + r"\6.-Result"
nombreArchivo = roothResult + r"\Archivos.xlsx"
listaArchivosTotal = list()

main()
