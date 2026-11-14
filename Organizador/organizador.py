import shutil
from pathlib import Path

# Mapeamento de categorias para extensões
CATEGORIAS = {
    "Imagens": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"],
    "Documentos": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".md"],
    "Planilhas": [".xls", ".xlsx", ".csv", ".ods"],
    "Apresentacoes": [".ppt", ".pptx", ".odp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"],
    "Audios": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Codigos": [".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".json", ".sql"],
    "Executaveis": [".exe", ".msi", ".apk", ".dmg", ".deb"],
}

PASTA_OUTROS = "Outros"


def descobrir_categoria(extensao: str) -> str:
    extensao = extensao.lower()
    for categoria, extensoes in CATEGORIAS.items():
        if extensao in extensoes:
            return categoria
    return PASTA_OUTROS


def gerar_destino_unico(destino: Path) -> Path:
    """Evita sobrescrever arquivos com o mesmo nome."""
    if not destino.exists():
        return destino
    contador = 1
    while True:
        novo = destino.with_name(f"{destino.stem}_{contador}{destino.suffix}")
        if not novo.exists():
            return novo
        contador += 1


def organizar(pasta: str, simular: bool = False) -> None:
    origem = Path(pasta).expanduser().resolve()

    if not origem.is_dir():
        print(f"Erro: '{origem}' não é uma pasta válida.")
        return

    movidos = 0
    for item in origem.iterdir():
        # Ignora subpastas e o próprio script
        if not item.is_file() or item.resolve() == Path(__file__).resolve():
            continue

        categoria = descobrir_categoria(item.suffix)
        pasta_destino = origem / categoria
        destino = gerar_destino_unico(pasta_destino / item.name)

        print(f"{item.name}  ->  {categoria}/{destino.name}")

        if not simular:
            pasta_destino.mkdir(exist_ok=True)
            shutil.move(str(item), str(destino))
        movidos += 1

    acao = "seriam movidos" if simular else "movidos"
    print(f"\nTotal de arquivos {acao}: {movidos}")


if __name__ == "__main__":
    caminho = input("Digite o caminho da pasta a organizar: ").strip().strip('"')
    modo = input("Apenas simular, sem mover nada? (s/n): ").strip().lower()
    organizar(caminho, simular=(modo == "s"))