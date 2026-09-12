import os
import re
import subprocess


# ============================================================
# Utilidades de tiempo
# ============================================================

def timecode_to_seconds(timecode):
    """
    Convierte 'HH:MM:SS' o 'HH:MM:SS.mmm' (segundos con decimales) a
    segundos (float). Ya no se usan frames ni fps.
    """
    parts = timecode.split(":")
    if len(parts) != 3:
        raise ValueError(
            f"Formato esperado HH:MM:SS o HH:MM:SS.mmm, recibido: {timecode}"
        )
    hh, mm, ss = parts
    return int(hh) * 3600 + int(mm) * 60 + float(ss)


def seconds_to_ffmpeg_time(seconds):
    """Convierte segundos (float) a formato HH:MM:SS.mmm que ffmpeg acepta."""
    hh = int(seconds // 3600)
    mm = int((seconds % 3600) // 60)
    ss = seconds % 60
    return f"{hh:02d}:{mm:02d}:{ss:06.3f}"


def get_duration_seconds(input_path):
    """Obtiene la duración total del audio en segundos usando ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", input_path],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())


# ============================================================
# Parseo del .txt de inicios (segundos decimales, sin fin ni frames)
# ============================================================

LINE_PATTERN = re.compile(
    r"^\s*(\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s*$"
)


def parse_start_times_file(txt_path):
    """
    Lee un .txt con líneas en formato 'HH:MM:SS' o 'HH:MM:SS.mmm'
    (solo el inicio del corte, en segundos decimales) y devuelve una
    lista de timecodes de inicio, uno por línea. Ignora líneas vacías.
    """
    starts = []
    with open(txt_path, "r", encoding="utf-8") as f:
        for num_linea, linea in enumerate(f, start=1):
            linea = linea.strip()
            if not linea:
                continue

            match = LINE_PATTERN.match(linea)
            if not match:
                raise ValueError(
                    f"Línea {num_linea} con formato inválido: '{linea}'. "
                    f"Se esperaba 'HH:MM:SS' o 'HH:MM:SS.mmm'."
                )

            starts.append(match.group(1))

    return starts


# ============================================================
# Corte de un solo archivo (un segmento)
# ============================================================

def cut_segment_aac(input_path, output_path, start_tc, duration_var,
                     reencode=True):
    """
    Elimina el segmento que va desde start_tc (formato 'HH:MM:SS' o
    'HH:MM:SS.mmm') hasta start_tc + duration_var segundos, generando
    output_path sin ese tramo.

    duration_var: duración del corte en segundos, admite decimales
    (ej. 1.5 -> 1 segundo y medio).
    """
    start_seconds = timecode_to_seconds(start_tc)
    end_seconds = start_seconds + duration_var

    duration = get_duration_seconds(input_path)
    if start_seconds >= duration:
        raise ValueError(
            f"El inicio del corte ({start_tc} = {start_seconds:.3f}s) está "
            f"fuera de la duración del audio ({duration:.3f}s)."
        )

    if end_seconds > duration:
        raise ValueError(
            f"El fin calculado del corte ({end_seconds:.3f}s = inicio "
            f"{start_seconds:.3f}s + {duration_var}s) excede la duración "
            f"del audio ({duration:.3f}s)."
        )

    start_cut = seconds_to_ffmpeg_time(start_seconds)
    end_cut = seconds_to_ffmpeg_time(end_seconds)

    tmp_dir = os.path.dirname(output_path) or "."
    part1 = os.path.join(tmp_dir, "_part1_tmp.aac")
    part2 = os.path.join(tmp_dir, "_part2_tmp.aac")
    list_file = os.path.join(tmp_dir, "_concat_list.txt")

    codec_args = ["-c:a", "aac", "-b:a", "192k"] if reencode else ["-c", "copy"]

    # Parte 1: desde el inicio hasta start_cut
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path, "-to", start_cut,
        *codec_args, part1
    ], check=True, capture_output=True, text=True)

    # Parte 2: desde end_cut hasta el final
    subprocess.run([
        "ffmpeg", "-y", "-ss", end_cut, "-i", input_path,
        *codec_args, part2
    ], check=True, capture_output=True, text=True)

    for p in (part1, part2):
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            raise RuntimeError(
                f"El archivo '{p}' quedó vacío. Revisa que start/end "
                f"estén dentro de la duración del audio original."
            )

    with open(list_file, "w", encoding="utf-8") as f:
        f.write(f"file '{os.path.abspath(part1)}'\n")
        f.write(f"file '{os.path.abspath(part2)}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", output_path
    ], check=True, capture_output=True, text=True)

    os.remove(part1)
    os.remove(part2)
    os.remove(list_file)


# ============================================================
# Procesamiento de la carpeta completa
# ============================================================

def list_aac_files(folder):
    """Devuelve solo archivos .aac (no carpetas), ordenados alfabéticamente."""
    if not folder or not os.path.exists(folder):
        return []

    result = []
    for item in os.listdir(folder):
        full = os.path.join(folder, item)
        if os.path.isfile(full) and item.lower().endswith(".aac"):
            result.append(item)

    return sorted(result)


def process_folder(input_folder, output_folder, starts_txt_path, duration_var,
                    reencode=True):
    """
    Recorre input_folder (archivos .aac ordenados alfabéticamente),
    aplica el inicio de corte de la línea correspondiente del .txt
    (el fin se calcula como inicio + duration_var segundos), y guarda
    el resultado en output_folder con el MISMO nombre de archivo.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    archivos = list_aac_files(input_folder)
    inicios = parse_start_times_file(starts_txt_path)

    if len(archivos) != len(inicios):
        raise ValueError(
            f"La cantidad de archivos .aac ({len(archivos)}) no coincide con "
            f"la cantidad de líneas del .txt ({len(inicios)}). "
            f"Deben ser iguales."
        )

    if not archivos:
        print("ADVERTENCIA: No se encontraron archivos .aac en la carpeta de entrada.")
        return

    for i, nombre_archivo in enumerate(archivos):
        input_path = os.path.join(input_folder, nombre_archivo)
        output_path = os.path.join(output_folder, nombre_archivo)
        start_tc = inicios[i]

        print(f"[{i + 1}/{len(archivos)}] Procesando '{nombre_archivo}' "
              f"-> corte desde {start_tc} + {duration_var}s")

        try:
            cut_segment_aac(input_path, output_path, start_tc, duration_var, reencode)
            print(f"    ✔ Listo: '{output_path}'")
        except Exception as e:
            print(f"    ✘ ERROR procesando '{nombre_archivo}': {e}")
            continue


# ============================================================
# Punto de entrada — ajusta estas rutas
# ============================================================

if __name__ == "__main__":
    INPUT_FOLDER   = r"C:\Users\win11\Documents\FilesTransform\3.-Sub-Full\DBZ"
    OUTPUT_FOLDER  = r"C:\Users\win11\Documents\FilesTransform\3.-Sub-Full\DBZ-Cortado\500"
    STARTS_TXT     = r"C:\Users\win11\Documents\Pycharm Projects\ArchivosAnime\RangosAudio.txt"
    DURATION_VAR   = 0.5  # duración del corte en segundos (admite decimales)

    process_folder(INPUT_FOLDER, OUTPUT_FOLDER, STARTS_TXT, DURATION_VAR)