import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageSequence

BASE = Path(__file__).parent
INPUT = BASE / "INPUT"
OUTPUT = BASE / "OUTPUT"

FFMPEG = shutil.which("ffmpeg")

# Gera uma paleta de 256 cores otimizada para a animação inteira e aplica
# com dithering de alta qualidade — o melhor resultado possível em GIF.
FILTRO_QUALIDADE = (
    "[0:v]split[a][b];"
    "[a]palettegen=stat_mode=diff[p];"
    "[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle"
)


def converter_com_ffmpeg(caminho: Path, destino: Path) -> None:
    resultado = subprocess.run(
        [
            FFMPEG, "-y", "-i", str(caminho),
            "-filter_complex", FILTRO_QUALIDADE,
            "-loop", "0",
            str(destino),
        ],
        capture_output=True,
        text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr.strip().splitlines()[-1] if resultado.stderr else "ffmpeg falhou")


def converter_com_pillow(caminho: Path, destino: Path) -> None:
    with Image.open(caminho) as img:
        frames = []
        duracoes = []
        for frame in ImageSequence.Iterator(img):
            rgba = frame.convert("RGBA")
            # Paleta adaptativa por frame + dithering Floyd-Steinberg
            quantizado = rgba.convert("RGB").quantize(
                colors=256,
                method=Image.Quantize.MEDIANCUT,
                dither=Image.Dither.FLOYDSTEINBERG,
            )
            frames.append(quantizado)
            duracoes.append(frame.info.get("duration", img.info.get("duration", 100)))

        if len(frames) == 1:
            frames[0].save(destino, format="GIF")
        else:
            frames[0].save(
                destino,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=duracoes,
                loop=img.info.get("loop", 0),
                disposal=2,
            )


def main() -> None:
    pastas_criadas = []
    for pasta in (INPUT, OUTPUT):
        if not pasta.exists():
            pasta.mkdir(parents=True)
            pastas_criadas.append(pasta.name)

    if pastas_criadas:
        print(f"Pasta(s) criada(s): {', '.join(pastas_criadas)}")

    imagens = sorted(INPUT.glob("*.webp"))
    if not imagens:
        print("Nenhuma imagem .webp encontrada na pasta INPUT.")
        sys.exit(0)

    if not FFMPEG:
        print("Aviso: ffmpeg nao encontrado, usando Pillow (qualidade um pouco menor).")

    print(f"{len(imagens)} imagem(ns) encontrada(s). Convertendo...")
    sucesso = 0
    for caminho in imagens:
        destino = OUTPUT / (caminho.stem + ".gif")
        try:
            if FFMPEG:
                try:
                    converter_com_ffmpeg(caminho, destino)
                except Exception:
                    converter_com_pillow(caminho, destino)
            else:
                converter_com_pillow(caminho, destino)
            print(f"  [OK] {caminho.name} -> {destino.name}")
            sucesso += 1
        except Exception as erro:
            print(f"  [ERRO] {caminho.name}: {erro}")

    print(f"Concluido: {sucesso}/{len(imagens)} convertida(s) para a pasta OUTPUT.")


if __name__ == "__main__":
    main()
