# Baixador de YouTube

Aplicativo de desktop com interface gráfica (preto e vermelho) para baixar vídeos em **MP4** ou áudios em **MP3** do YouTube, sempre na maior qualidade disponível. Feito em Python com [yt-dlp](https://github.com/yt-dlp/yt-dlp) e `tkinter`.

## Recursos

- **Interface gráfica** simples, sem precisar usar o terminal para baixar.
- **Qualidade máxima**: o vídeo usa a melhor resolução disponível (até 4K/8K, quando existir) e o MP3 sai a 320 kbps.
- **Download de playlists** inteiras, com subpasta própria e arquivos numerados.
- **Botão Cancelar** para interromper o download a qualquer momento.
- **Barra de progresso** com porcentagem, velocidade, tempo restante e posição na playlist (ex.: `[3/20]`).
- **Modo compatibilidade** (H.264, até 1080p) para vídeos que precisam tocar em qualquer player.
- Os arquivos são salvos **na mesma pasta do programa**.
- A janela não trava durante o download.

## Requisitos

- **Python 3.9 ou superior**
- **yt-dlp**
- **ffmpeg** instalado e disponível no PATH (necessário para converter MP3 e juntar vídeo e áudio em alta qualidade)
- `tkinter` (já vem com o Python no Windows e no macOS)

## Instalação

### 1. Instalar o yt-dlp

```bash
pip install -U yt-dlp
```

### 2. Instalar o ffmpeg

**Windows**

```bash
winget install Gyan.FFmpeg
```

Depois feche e abra o terminal de novo para o PATH ser atualizado.

**macOS**

```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu)**

```bash
sudo apt install ffmpeg python3-tk
```

Para conferir se o ffmpeg foi instalado corretamente, abra um terminal novo e rode:

```bash
ffmpeg -version
```

## Como usar

1. Coloque o arquivo `baixar_youtube_gui.py` na pasta onde quer guardar os downloads.
2. Execute:

   ```bash
   python baixar_youtube_gui.py
   ```

   No Windows, também é possível dar dois cliques no arquivo.

3. Cole o link do YouTube (botão **Colar** ou Ctrl+V).
4. Escolha o formato:
   - **MP4**: vídeo na qualidade máxima.
   - **MP3**: áudio a 320 kbps.
5. Clique em **Baixar** (ou aperte Enter).
6. Para parar, clique em **Cancelar**.
7. Use **Abrir pasta** para ver os arquivos baixados.

### Playlists

Marque **"Baixar playlist inteira"** antes de clicar em Baixar. Os arquivos serão salvos assim:

```
Nome da Playlist/
├── 01 - Primeiro vídeo.mp4
├── 02 - Segundo vídeo.mp4
└── ...
```

- Vídeos privados ou indisponíveis são pulados, sem interromper o restante.
- Arquivos que já existem não são baixados de novo. Se a internet cair, basta rodar com o mesmo link para continuar de onde parou.
- Com a opção desmarcada, só o vídeo do link é baixado, mesmo que ele esteja dentro de uma playlist.
- Evite os "Mixes" automáticos do YouTube (links com `list=RD...`), pois não têm fim definido.

### Qualidade e compatibilidade

Por padrão, o MP4 usa a maior resolução disponível, que muitas vezes é VP9 ou AV1. Esses codecs podem não abrir no Windows Media Player ou no player de filmes e séries do Windows. O **VLC** toca sem problemas.

Se o vídeo não abrir no seu player, marque **"Priorizar compatibilidade (H.264, máx. 1080p)"**. Ele toca em qualquer lugar, mas fica limitado a 1080p.

O MP3 sai a 320 kbps, o máximo do formato. Como o áudio original do YouTube já tem qualidade limitada, o arquivo não fica melhor do que a fonte.

## Problemas comuns

| Problema | Solução |
| --- | --- |
| Aviso "ffmpeg não encontrado" | Instale o ffmpeg e **reinicie o terminal** (ou o computador). Confirme com `ffmpeg -version`. |
| `ModuleNotFoundError: yt_dlp` | Rode `pip install -U yt-dlp`. |
| `No module named tkinter` (Linux) | Rode `sudo apt install python3-tk`. |
| Erros como HTTP 403 ou "unable to extract" | O YouTube muda com frequência. Atualize com `pip install -U yt-dlp`. |
| O vídeo baixado não abre no player | Marque o modo compatibilidade (H.264) ou use o VLC. |
| Ficaram arquivos `.part` na pasta | São downloads cancelados. Baixar o mesmo link de novo continua de onde parou, ou você pode apagá-los. |

## Personalização

- **Cores**: estão no começo do arquivo (`COR_FUNDO`, `COR_VERMELHO` e outras). Troque os códigos hexadecimais para mudar o visual.
- **Qualidade do MP3**: altere o valor de `preferredquality` em `montar_opcoes()`.
- **Pasta de destino**: definida por `PASTA_DESTINO` no início do arquivo.

## Gerar um executável (opcional)

Para criar um `.exe` no Windows:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole baixar_youtube_gui.py
```

O executável aparece na pasta `dist/` e salva os downloads ao lado dele. O ffmpeg continua precisando estar instalado no PATH.

## Aviso legal

Use esta ferramenta apenas para baixar conteúdo que você tem permissão para baixar (como seus próprios vídeos, conteúdo com licença livre ou de domínio público). Os termos de uso do YouTube restringem o download de vídeos de terceiros, e o respeito aos direitos autorais é responsabilidade de quem usa o programa.

## Créditos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp), responsável pelo download.
- [FFmpeg](https://ffmpeg.org/), responsável pela conversão e mesclagem de áudio e vídeo.
