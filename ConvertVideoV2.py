import subprocess
import os
import json
import time


def run(cmd):
    subprocess.run(cmd, check=True)


def list_files(path, extensions=("mkv", "mp4", "ass", "srt")):
    """Devuelve SOLO archivos (no carpetas), filtrados por extensión."""
    if not path or not os.path.exists(path):
        return []

    result = []
    for item in os.listdir(path):
        full = os.path.join(path, item)

        # ignorar carpetas
        if not os.path.isfile(full):
            continue

        # filtrar solo extensiones válidas
        if item.lower().split(".")[-1] in extensions:
            result.append(item)

    return sorted(result)


def validate_counts(*lists):
    """Verifica que todas las listas tengan la misma cantidad de archivos."""
    lengths = [len(lst) for lst in lists if lst]
    return all(length == lengths[0] for length in lengths)


def build_output_name(folder, filename):
    """Construye el nombre final del archivo MKV según el video principal."""
    base = os.path.splitext(os.path.basename(filename))[0]
    return os.path.join(folder, f"{base}.mkv")


def main():
    mkvmerge_path = os.path.join(os.getcwd(), "mkvmerge.exe")
    if not os.path.exists(mkvmerge_path):
        print("ERROR: mkvmerge.exe no está en la carpeta del script.")
        return

    if not os.path.exists("config.json"):
        print("ERROR: No existe config.json.")
        return

    # Leer config
    with open("config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Datos principales
    video_audio_path = cfg["video_audio"]
    video_audio_path_2 = cfg["video_audio_2"]
    subtitle_path = cfg["subtitle"]["path"]
    subtitle_path_2 = cfg["subtitle_2"]["path"]
    atachment_path = cfg["attachments"]

    # Tracks
    vtrack = cfg["video"]["track"]
    atrack = cfg["audio"]["track"]
    atime = cfg["audio"]["time"]

    strack = cfg["subtitle"]["track"]
    stime = cfg["subtitle"]["time"]

    atrack_2 = cfg["audio_2"]["track"]
    atime_2 = cfg["audio_2"]["time"]

    strack_2 = cfg["subtitle_2"]["track"]
    stime_2 = cfg["subtitle_2"]["time"]

    # Listas de archivos
    listVideoAudio = list_files(video_audio_path)
    listAudioLatino = list_files(video_audio_path_2)
    listSubFull = list_files(subtitle_path)
    listSubSign = list_files(subtitle_path_2)
    listAttachments = list_files(atachment_path)

    # Validar cantidades
    if not validate_counts(listVideoAudio, listSubFull, listAttachments,
                           listAudioLatino, listSubSign):
        print("ERROR: La cantidad de archivos no coincide entre carpetas.")
        return

    for i, fileVA in enumerate(listVideoAudio):

        # --------------------------------------------------------------------
        # Nombre final = nombre del archivo del video principal
        # --------------------------------------------------------------------
        nameVA = listVideoAudio[i]
        output_file = build_output_name(cfg["output"], nameVA)

        cmd = [
            mkvmerge_path,
            "-o", output_file,

            # VIDEO + AUDIO PRINCIPAL
            "--video-tracks", vtrack,
            "--audio-tracks", atrack,
            "--sync", f"{atrack}:{atime}",
            "--no-subtitles",
            "--no-attachments",
            "--no-global-tags",
            "--default-track-flag", f"{vtrack}:yes",
            "--default-track-flag", f"{atrack}:yes",
            os.path.join(video_audio_path, fileVA),

            # SUBTÍTULO PRINCIPAL
            "--no-video",
            "--no-audio",
            "--subtitle-tracks", strack,
            "--default-track-flag", f"{strack}:yes",
            "--sync", f"{strack}:{stime}",
            "--no-track-tags",
            "--no-global-tags",
            "--no-attachments",
            os.path.join(subtitle_path, listSubFull[i]),

            # ATTACHMENTS
            "--no-video",
            "--no-audio",
            "--no-subtitles",
            "--no-track-tags",
            "--no-global-tags",
            os.path.join(atachment_path, listAttachments[i]),
        ]

        # TRACK ORDER (inicia con video, audio, subtítulo)
        track_order = [
            f"0:{vtrack}",
            f"0:{atrack}",
        ]

        # AUDIO SECUNDARIO opcional
        if listAudioLatino:
            cmd += [
                "--no-video",
                "--audio-tracks", atrack_2,
                "--sync", f"{atrack_2}:{atime_2}",
                "--no-subtitles",
                "--no-attachments",
                "--no-global-tags",
                "--default-track-flag", f"{atrack_2}:no",
                os.path.join(video_audio_path_2, listAudioLatino[i]),
            ]
            track_order.append(f"3:{atrack_2}")

        track_order.append(f"1:{strack}")

        # SUBTÍTULO SECUNDARIO opcional
        if listSubSign:
            cmd += [
                "--no-video",
                "--no-audio",
                "--subtitle-tracks", strack_2,
                "--default-track-flag", f"{strack_2}:no",
                "--sync", f"{strack_2}:{stime_2}",
                "--no-track-tags",
                "--no-global-tags",
                "--no-attachments",
                os.path.join(subtitle_path_2, listSubSign[i]),
            ]
            track_order.append(f"4:{strack_2}")

        # ULTIMOS AJUSTES
        cmd += [
            "--title", "",
            "--track-order", ",".join(track_order)
        ]

        # --- Obtener nombre final del archivo ---
        output_file = cmd[cmd.index("-o") + 1]
        nombre_final = os.path.basename(output_file)

        print(f"🏁 Archivo final: {nombre_final}\n")

        # --- Ejecutar mkvmerge con progreso ---
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for linea in process.stdout:
            linea = linea.strip()
            if linea.startswith("Progress"):
                # Ejemplo: "Progress: 34%" → obtener solo el número
                porcentaje = linea.replace("Progress: ", "")
                print(f"{nombre_final} → {porcentaje}")

        process.wait()

        print("\n✔ Finalizado:", nombre_final)
        print("Código de salida:", process.returncode)
        time.sleep(30)


if __name__ == "__main__":
    main()
