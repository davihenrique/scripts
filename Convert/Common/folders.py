import sys
from pathlib import Path


def get_input_output_paths(caller_dir=None):
    """
    Retorna os caminhos INPUT e OUTPUT baseado no diretório do script chamador.
    
    Args:
        caller_dir: Diretório do script chamador. Se None, usa o diretório do script que importou este módulo.
    
    Returns:
        tuple: (INPUT_path, OUTPUT_path)
    """
    if caller_dir is None:
        # Obtém o diretório do arquivo que importou este módulo
        frame = sys._getframe(1)
        caller_file = frame.f_globals.get('__file__')
        if caller_file:
            caller_dir = Path(caller_file).parent
        else:
            caller_dir = Path.cwd()
    else:
        caller_dir = Path(caller_dir)
    
    input_path = caller_dir / "INPUT"
    output_path = caller_dir / "OUTPUT"
    
    # Criar pastas se não existirem
    input_path.mkdir(parents=True, exist_ok=True)
    output_path.mkdir(parents=True, exist_ok=True)
    
    return input_path, output_path


def main():
    """
    Quando executado sozinho, apenas mostra uma mensagem informando que é uma biblioteca.
    """
    print("⚠️  Este é um módulo (biblioteca) e não deve ser executado diretamente.")
    print("Use-o importando em seus scripts com: from folders import get_input_output_paths")


if __name__ == "__main__":
    main()
