#!/usr/bin/env python3
"""Baixador de YouTube (MP4 / MP3) com interface gráfica.

- Salva os arquivos na mesma pasta onde este script está.
- Vídeo na maior qualidade disponível; áudio MP3 a 320 kbps.

Requisitos:
    pip install -U yt-dlp
    ffmpeg instalado e disponível no PATH
"""

import os
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

try:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError
    try:
        from yt_dlp.utils import DownloadCancelled
    except ImportError:  # versões muito antigas do yt-dlp
        class DownloadCancelled(Exception):
            pass
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "yt-dlp não encontrado",
        "Instale com:\n\npip install -U yt-dlp",
    )
    sys.exit(1)


# Pasta do próprio script (ou do .exe, se for empacotado com PyInstaller)
if getattr(sys, "frozen", False):
    PASTA_DESTINO = Path(sys.executable).resolve().parent
else:
    PASTA_DESTINO = Path(__file__).resolve().parent


# Paleta preto e vermelho
COR_FUNDO = "#0b0b0b"
COR_CAMPO = "#1a1a1a"
COR_TEXTO = "#f2f2f2"
COR_VERMELHO = "#e50914"
COR_VERMELHO_ESCURO = "#b20710"
COR_VERMELHO_CLARO = "#ff2b36"
COR_DESATIVADO = "#2a2a2a"


class Logger:
    """Envia mensagens do yt-dlp para a interface."""

    def __init__(self, fila: queue.Queue):
        self.fila = fila

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        self.fila.put(("log", msg))


def montar_opcoes(
    tipo: str,
    compativel: bool,
    playlist: bool,
    fila: queue.Queue,
    cancelar: threading.Event,
) -> dict:
    """Monta as opções do yt-dlp para a melhor qualidade possível."""

    def hook_progresso(d):
        if cancelar.is_set():
            raise DownloadCancelled()
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            baixado = d.get("downloaded_bytes", 0)
            pct = (baixado / total * 100) if total else 0
            vel = d.get("speed")
            eta = d.get("eta")
            info = d.get("info_dict") or {}
            idx, n = info.get("playlist_index"), info.get("n_entries")
            prefixo = f"[{idx}/{n}] " if playlist and idx and n else ""
            partes = [f"{prefixo}{pct:.1f}%"]
            if vel:
                partes.append(f"{vel / 1_048_576:.2f} MB/s")
            if eta is not None:
                partes.append(f"faltam {int(eta)}s")
            fila.put(("progresso", pct, "  •  ".join(partes)))
        elif d["status"] == "finished":
            fila.put(("progresso", 100, "Download concluído, processando..."))

    def hook_pos(d):
        if cancelar.is_set():
            raise DownloadCancelled()
        if d["status"] == "started":
            fila.put(("status", "Convertendo / mesclando com ffmpeg..."))

    if playlist:
        # Cria uma subpasta com o nome da playlist e numera os arquivos
        modelo = "%(playlist_title|Playlist)s/%(playlist_index&{} - |)s%(title)s.%(ext)s"
    else:
        modelo = "%(title)s.%(ext)s"

    opcoes = {
        "outtmpl": str(PASTA_DESTINO / modelo),
        "noplaylist": not playlist,
        "ignoreerrors": playlist,  # pula vídeos indisponíveis em vez de parar tudo
        "windowsfilenames": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": Logger(fila),
        "progress_hooks": [hook_progresso],
        "postprocessor_hooks": [hook_pos],
    }

    if tipo == "mp3":
        opcoes.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }],
        })
    else:
        if compativel:
            # H.264 + AAC: toca em qualquer player (limite de 1080p no YouTube)
            formato = "bv*[vcodec^=avc1]+ba[ext=m4a]/bv*[vcodec^=avc1]+ba/b[ext=mp4]/b"
        else:
            # Maior resolução/bitrate disponível (pode ser VP9/AV1, até 4K/8K)
            formato = "bv*+ba/b"
        opcoes.update({
            "format": formato,
            "merge_output_format": "mp4",
        })

    return opcoes


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Downloader")
        self.geometry("620x530")
        self.minsize(560, 490)

        self.fila: queue.Queue = queue.Queue()
        self.cancelar = threading.Event()
        self.baixando = False

        self.var_link = tk.StringVar()
        self.var_tipo = tk.StringVar(value="mp4")
        self.var_compat = tk.BooleanVar(value=False)
        self.var_playlist = tk.BooleanVar(value=False)

        self._aplicar_tema()
        self._montar_interface()
        self._verificar_ffmpeg()
        self.after(100, self._processar_fila)

    # ---------- Tema ----------
    def _aplicar_tema(self):
        self.configure(bg=COR_FUNDO)
        s = ttk.Style(self)
        s.theme_use("clam")

        s.configure(
            ".",
            background=COR_FUNDO,
            foreground=COR_TEXTO,
            fieldbackground=COR_CAMPO,
            bordercolor=COR_VERMELHO_ESCURO,
            lightcolor=COR_FUNDO,
            darkcolor=COR_FUNDO,
            troughcolor=COR_CAMPO,
            focuscolor=COR_FUNDO,
            font=("Segoe UI", 10),
        )
        s.configure("TFrame", background=COR_FUNDO)
        s.configure("TLabel", background=COR_FUNDO, foreground=COR_TEXTO)
        s.configure(
            "Titulo.TLabel",
            foreground=COR_VERMELHO,
            font=("Segoe UI", 17, "bold"),
        )

        s.configure("TLabelframe", background=COR_FUNDO, bordercolor=COR_VERMELHO_ESCURO)
        s.configure(
            "TLabelframe.Label",
            background=COR_FUNDO,
            foreground=COR_VERMELHO,
            font=("Segoe UI", 10, "bold"),
        )

        s.configure(
            "TEntry",
            fieldbackground=COR_CAMPO,
            foreground=COR_TEXTO,
            insertcolor=COR_TEXTO,
            bordercolor=COR_VERMELHO_ESCURO,
            padding=6,
        )
        s.map("TEntry", bordercolor=[("focus", COR_VERMELHO)])

        s.configure(
            "TButton",
            background=COR_VERMELHO,
            foreground="white",
            bordercolor=COR_VERMELHO,
            padding=(14, 6),
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        s.map(
            "TButton",
            background=[
                ("disabled", COR_DESATIVADO),
                ("pressed", COR_VERMELHO_ESCURO),
                ("active", COR_VERMELHO_CLARO),
            ],
            foreground=[("disabled", "#6a6a6a")],
            bordercolor=[("disabled", COR_DESATIVADO)],
        )

        for estilo in ("TCheckbutton", "TRadiobutton"):
            s.configure(estilo, background=COR_FUNDO, foreground=COR_TEXTO)
            s.map(
                estilo,
                background=[("active", COR_FUNDO)],
                foreground=[("disabled", "#666666")],
                indicatorcolor=[
                    ("selected", COR_VERMELHO),
                    ("!selected", COR_CAMPO),
                ],
            )

        s.configure(
            "Horizontal.TProgressbar",
            background=COR_VERMELHO,
            troughcolor=COR_CAMPO,
            bordercolor=COR_FUNDO,
            lightcolor=COR_VERMELHO,
            darkcolor=COR_VERMELHO,
            thickness=14,
        )
        s.configure(
            "Vertical.TScrollbar",
            background=COR_VERMELHO_ESCURO,
            troughcolor=COR_CAMPO,
            bordercolor=COR_FUNDO,
            arrowcolor=COR_TEXTO,
        )
        s.map("Vertical.TScrollbar", background=[("active", COR_VERMELHO)])

    # ---------- Interface ----------
    def _montar_interface(self):
        pad = {"padx": 14, "pady": 6}
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=4, pady=4)

        ttk.Label(frame, text="BAIXADOR DE YOUTUBE", style="Titulo.TLabel").pack(
            anchor="w", padx=14, pady=(10, 2)
        )
        ttk.Label(frame, text="Link do YouTube:").pack(anchor="w", **pad)

        linha = ttk.Frame(frame)
        linha.pack(fill="x", padx=14)
        self.entry = ttk.Entry(linha, textvariable=self.var_link)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.iniciar())
        self.entry.focus()
        ttk.Button(linha, text="Colar", width=8, command=self.colar).pack(
            side="left", padx=(6, 0)
        )

        # Formato
        caixa = ttk.LabelFrame(frame, text="Formato")
        caixa.pack(fill="x", **pad)
        ttk.Radiobutton(
            caixa, text="MP4 (vídeo, qualidade máxima)",
            variable=self.var_tipo, value="mp4", command=self._atualizar_opcoes,
        ).pack(anchor="w", padx=10, pady=(6, 2))
        ttk.Radiobutton(
            caixa, text="MP3 (áudio, 320 kbps)",
            variable=self.var_tipo, value="mp3", command=self._atualizar_opcoes,
        ).pack(anchor="w", padx=10, pady=2)
        self.chk_compat = ttk.Checkbutton(
            caixa,
            text="Priorizar compatibilidade (H.264, máx. 1080p)",
            variable=self.var_compat,
        )
        self.chk_compat.pack(anchor="w", padx=30, pady=(2, 8))

        ttk.Checkbutton(
            frame,
            text="Baixar playlist inteira (cria uma subpasta com o nome da playlist)",
            variable=self.var_playlist,
        ).pack(anchor="w", padx=14, pady=2)

        # Botões
        botoes = ttk.Frame(frame)
        botoes.pack(fill="x", padx=14, pady=4)
        self.btn_baixar = ttk.Button(botoes, text="Baixar", command=self.iniciar)
        self.btn_baixar.pack(side="left")
        self.btn_cancelar = ttk.Button(
            botoes, text="Cancelar", command=self.cancelar_download, state="disabled"
        )
        self.btn_cancelar.pack(side="left", padx=6)
        ttk.Button(botoes, text="Abrir pasta", command=self.abrir_pasta).pack(
            side="left", padx=6
        )

        # Progresso
        self.barra = ttk.Progressbar(frame, maximum=100)
        self.barra.pack(fill="x", padx=14, pady=(10, 2))
        self.lbl_status = ttk.Label(frame, text="Pronto.")
        self.lbl_status.pack(anchor="w", padx=14)

        # Log
        ttk.Label(frame, text="Registro:").pack(anchor="w", padx=14, pady=(8, 0))
        log_frame = ttk.Frame(frame)
        log_frame.pack(fill="both", expand=True, padx=14, pady=(2, 8))
        self.log = tk.Text(
            log_frame,
            height=6,
            state="disabled",
            wrap="word",
            bg=COR_CAMPO,
            fg=COR_TEXTO,
            insertbackground=COR_TEXTO,
            selectbackground=COR_VERMELHO,
            selectforeground="white",
            relief="flat",
            highlightthickness=1,
            highlightbackground=COR_VERMELHO_ESCURO,
            highlightcolor=COR_VERMELHO,
            font=("Consolas", 9),
        )
        scroll = ttk.Scrollbar(log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._escrever_log(f"Pasta de destino: {PASTA_DESTINO}")

    def _atualizar_opcoes(self):
        estado = "normal" if self.var_tipo.get() == "mp4" else "disabled"
        self.chk_compat.configure(state=estado)

    def _verificar_ffmpeg(self):
        if shutil.which("ffmpeg") is None:
            self._escrever_log(
                "AVISO: ffmpeg não encontrado no PATH. MP3 e vídeo em alta "
                "qualidade podem falhar. Reinicie o terminal/computador após "
                "instalar o ffmpeg."
            )

    # ---------- Ações ----------
    def colar(self):
        try:
            self.var_link.set(self.clipboard_get().strip())
        except tk.TclError:
            pass

    def abrir_pasta(self):
        try:
            if sys.platform.startswith("win"):
                os.startfile(PASTA_DESTINO)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(PASTA_DESTINO)])
            else:
                subprocess.run(["xdg-open", str(PASTA_DESTINO)])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a pasta:\n{e}")

    def iniciar(self):
        if self.baixando:
            return
        link = self.var_link.get().strip()
        if not link.startswith(("http://", "https://")):
            messagebox.showwarning(
                "Link inválido", "Cole um link que comece com http:// ou https://"
            )
            return

        self.baixando = True
        self.btn_baixar.configure(state="disabled")
        self.cancelar.clear()
        self.btn_cancelar.configure(state="normal")
        self.barra["value"] = 0
        self.lbl_status.configure(text="Iniciando...")
        self._escrever_log(f"Baixando: {link}")

        threading.Thread(
            target=self._baixar,
            args=(
                link,
                self.var_tipo.get(),
                self.var_compat.get(),
                self.var_playlist.get(),
            ),
            daemon=True,
        ).start()

    def cancelar_download(self):
        if not self.baixando:
            return
        self.cancelar.set()
        self.btn_cancelar.configure(state="disabled")
        self.lbl_status.configure(text="Cancelando...")
        self._escrever_log("Cancelando download...")

    def _baixar(self, link: str, tipo: str, compativel: bool, playlist: bool):
        """Roda em outra thread para não travar a janela."""
        try:
            opcoes = montar_opcoes(tipo, compativel, playlist, self.fila, self.cancelar)
            with YoutubeDL(opcoes) as ydl:
                info = ydl.extract_info(link, download=True)
            baixados = (info or {}).get("requested_downloads") or []
            caminho = baixados[0].get("filepath") if baixados and not playlist else None
            self.fila.put(("fim", caminho or str(PASTA_DESTINO)))
        except DownloadCancelled:
            self.fila.put(("cancelado",))
        except DownloadError as e:
            if self.cancelar.is_set():
                self.fila.put(("cancelado",))
            else:
                self.fila.put(("erro", str(e)))
        except Exception as e:
            self.fila.put(("erro", f"Erro inesperado: {e}"))

    # ---------- Comunicação entre threads ----------
    def _processar_fila(self):
        try:
            while True:
                msg = self.fila.get_nowait()
                tipo = msg[0]
                if tipo == "progresso":
                    self.barra["value"] = msg[1]
                    self.lbl_status.configure(text=msg[2])
                elif tipo == "status":
                    self.lbl_status.configure(text=msg[1])
                elif tipo == "log":
                    self._escrever_log(msg[1])
                elif tipo == "fim":
                    self._finalizar()
                    self.barra["value"] = 100
                    self.lbl_status.configure(text="Concluído!")
                    self._escrever_log(f"Salvo em: {msg[1]}")
                elif tipo == "cancelado":
                    self._finalizar()
                    self.barra["value"] = 0
                    self.lbl_status.configure(text="Download cancelado.")
                    self._escrever_log(
                        "Download cancelado. Arquivos parciais (.part) podem "
                        "ficar na pasta; baixar de novo continua de onde parou."
                    )
                elif tipo == "erro":
                    self._finalizar()
                    self.lbl_status.configure(text="Falha no download.")
                    self._escrever_log(f"ERRO: {msg[1]}")
                    messagebox.showerror("Erro no download", msg[1])
        except queue.Empty:
            pass
        self.after(100, self._processar_fila)

    def _finalizar(self):
        self.baixando = False
        self.btn_baixar.configure(state="normal")
        self.btn_cancelar.configure(state="disabled")

    def _escrever_log(self, texto: str):
        self.log.configure(state="normal")
        self.log.insert("end", texto + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()