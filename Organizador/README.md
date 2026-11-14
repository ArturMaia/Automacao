# 📁 Organizador de Arquivos
<p align="center">
  <img src="https://github.com/ArturMaia/Automacao/blob/main/Organizador/arquivos.jpg" alt="ARQUIVOS" style="width: 350px; border-radius: 200px;"> 
</p>

Script em Python que organiza automaticamente os arquivos de uma pasta, separando-os em subpastas por tipo (imagens, documentos, vídeos, etc.). Possui um **modo de simulação** para você conferir o resultado antes de mover qualquer coisa.

## ✨ Funcionalidades

- Classifica arquivos por extensão em 9 categorias, mais a pasta `Outros`
- Modo de simulação (`dry run`) que mostra o que seria feito sem alterar nada
- Evita sobrescrever arquivos: se já existir um com o mesmo nome, adiciona um sufixo numérico (`foto.jpg` → `foto_1.jpg`)
- Ignora subpastas e o próprio script
- Aceita caminhos com `~` (pasta do usuário) e caminhos entre aspas
- Usa apenas a biblioteca padrão do Python, sem dependências externas

## 📂 Categorias

| Pasta | Extensões |
|---|---|
| **Imagens** | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.svg` `.webp` `.heic` |
| **Documentos** | `.pdf` `.doc` `.docx` `.txt` `.odt` `.rtf` `.md` |
| **Planilhas** | `.xls` `.xlsx` `.csv` `.ods` |
| **Apresentacoes** | `.ppt` `.pptx` `.odp` |
| **Videos** | `.mp4` `.mkv` `.avi` `.mov` `.wmv` `.flv` |
| **Audios** | `.mp3` `.wav` `.flac` `.aac` `.ogg` `.m4a` |
| **Compactados** | `.zip` `.rar` `.7z` `.tar` `.gz` |
| **Codigos** | `.py` `.js` `.html` `.css` `.java` `.c` `.cpp` `.json` `.sql` |
| **Executaveis** | `.exe` `.msi` `.apk` `.dmg` `.deb` |
| **Outros** | Qualquer extensão não listada acima |

## 🔧 Requisitos

- Python 3.6 ou superior

##  Como usar

1. Informe o caminho do diretório que deseja organizar.
2. Responda `s` para apenas simular ou `n` para mover os arquivos de verdade.

> 💡 **Dica:** rode primeiro em modo simulação (`s`) para conferir o resultado. Depois, execute novamente com `n` para aplicar a organização.

## Como funciona

- **`descobrir_categoria(extensao)`**: compara a extensão (sem diferenciar maiúsculas de minúsculas) com o dicionário `CATEGORIAS` e retorna o nome da pasta correspondente, ou `Outros` se não houver correspondência.
- **`gerar_destino_unico(destino)`**: se já houver um arquivo com o mesmo nome no destino, gera um novo nome com contador (`_1`, `_2`, ...) para evitar sobrescrita.
- **`organizar(pasta, simular)`**: percorre os arquivos da pasta, define a categoria de cada um, cria a subpasta se necessário e move o arquivo (ou apenas exibe a ação no modo de simulação).

Para mudar o nome da pasta de arquivos não classificados, altere a constante `PASTA_OUTROS`.

## Observações

- Apenas os arquivos **diretamente na pasta informada** são organizados. Subpastas e seus conteúdos não são alterados.
- Arquivos movidos **não são restaurados automaticamente**. Use o modo de simulação em pastas importantes.
- Evite executar em pastas de sistema ou de projetos de código, pois arquivos podem ser movidos e quebrar referências.

## Ideias de melhorias

- Aceitar o caminho da pasta via argumento de linha de comando (`argparse`)
- Gerar um log das movimentações para permitir desfazer a operação
- Organizar também por data de modificação
- Criar interface gráfica com `tkinter`
