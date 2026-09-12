import os
from pathlib import Path
import subprocess
from openpyxl import Workbook
import json


def check():
    global option, optionSub
    option = int(input(
        f'\nmkvextractor (MKVToolNix : mkvextract)\
        \n|-- 1 : Extraer Tracks\
        \n|-- 2 : Listar Tracks con Nombres\
        \n|-- 3 : Extraer Chapters\
        \n\
        \nextractMode: '
    ))

    if option in (1, 2):
        optionStringSub = input("Elija su pista de Extraccion(Por defecto 2) ").rstrip().lstrip()
        optionSub = int('2' if optionStringSub == "" else optionStringSub)
    else:
        optionSub = 0


def get_extension_for_codec(codec):
    """
    Devuelve la extensión adecuada según el codec de la pista,
    soportando tanto subtítulos como audio.
    """
    match codec:
        # --- Subtítulos ---
        case "SubStationAlpha":
            return ".ass"
        case "SubRip/SRT":
            return ".srt"
        case "HDMV PGS":
            return ".sup"
        case "VobSub":
            return ".idx"  # nota: VobSub genera .idx + .sub, mkvextract maneja ambos

        # --- Audio ---
        case "AAC":
            return ".aac"
        case "MP3":
            return ".mp3"
        case "AC-3" | "AC3":
            return ".ac3"
        case "E-AC-3" | "EAC3":
            return ".eac3"
        case "DTS":
            return ".dts"
        case "FLAC":
            return ".flac"
        case "Vorbis":
            return ".ogg"
        case "Opus":
            return ".opus"
        case "PCM":
            return ".wav"
        case "TrueHD":
            return ".thd"

        case _:
            return ""


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
                    extension = get_extension_for_codec(codec)

                    if extension == "":
                        print(f"⚠ ADVERTENCIA: Codec '{codec}' no reconocido para la pista "
                              f"{optionSub} en '{name}'. Se extraerá sin extensión.")

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

        case 3:
            os.makedirs(roothChapters, exist_ok=True)

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
                    fileResult = roothChapters + "\\" + Path(fileVA).stem
                    fileResult = fileResult.replace('\\', '\\\\')

                    resultado = subprocess.run(
                        r'mkvextract.exe chapters "' + pathVA + '"',
                        capture_output=True,
                        text=True,
                        encoding='utf-8'
                    )

                    if resultado.returncode != 0 or not resultado.stdout.strip():
                        print(f"⚠ ADVERTENCIA: '{name}' no tiene chapters o fallo la extraccion.")
                        if resultado.stderr:
                            print(resultado.stderr.strip())
                        continue

                    with open(fileResult + '_chapters.xml', 'w', encoding='utf-8') as chapterFile:
                        chapterFile.write(resultado.stdout)

                    print(f"✔ Chapters extraidos: {name}")


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
rooth = r"C:\Users\win11\Documents\FilesTransform"
roothVideoAudio = rooth + r"\1.-Video-Audio"
roothSubFull = rooth + r"\3.-Sub-Full"
roothChapters = rooth + r"\5.-Attachments"
roothResult = rooth + r"\6.-Result"
nombreArchivo = roothResult + r"\Archivos.xlsx"
listaArchivosTotal = list()

main()
