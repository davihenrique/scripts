import subprocess
import sys
from pathlib import Path

# Adiciona a pasta Common ao path para importar folders
sys.path.insert(0, str(Path(__file__).parent.parent / "Common"))
from folders import get_input_output_paths


def converter_mp4_para_gif(caminho: Path, destino: Path) -> None:
    """
    Converte um arquivo MP4 para GIF usando ffmpeg.
    
    Args:
        caminho: Caminho do arquivo MP4
        destino: Caminho do arquivo GIF de saída
    """
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i", str(caminho),
        "-vf", "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        "-loop", "0",
        str(destino)
    ]
    
    resultado = subprocess.run(ffmpeg_command, capture_output=True, text=True)
    
    if resultado.returncode != 0:
        raise RuntimeError(resultado.stderr.strip().splitlines()[-1] if resultado.stderr else "ffmpeg falhou")


def main() -> None:
    # Get INPUT and OUTPUT paths
    input_path, output_path = get_input_output_paths()
    
    # Procura por arquivos .mp4
    videos = sorted(input_path.glob("*.mp4"))
    
    if not videos:
        print("Nenhum arquivo .mp4 encontrado na pasta INPUT.")
        sys.exit(0)
    
    print(f"{len(videos)} video(s) encontrado(s). Convertendo...")
    sucesso = 0
    
    for caminho in videos:
        destino = output_path / (caminho.stem + ".gif")
        try:
            converter_mp4_para_gif(caminho, destino)
            print(f"  [OK] {caminho.name} -> {destino.name}")
            sucesso += 1
        except Exception as erro:
            print(f"  [ERRO] {caminho.name}: {erro}")
    
    print(f"Concluido: {sucesso}/{len(videos)} convertido(s) para a pasta OUTPUT.")


if __name__ == "__main__":
    main()
