"""Monitor de sistema e conexão, com interface gráfica (Tkinter).

Mostra em tempo real o uso de CPU, memória e disco e testa a qualidade
da conexão com a internet medindo o tempo de resposta de uma requisição HTTP.
"""

import os
import threading
import time
import tkinter as tk
from tkinter import ttk

import psutil
import requests

URL_TESTE = "https://www.google.com"
TIMEOUT = 5                 # segundos
INTERVALO_SISTEMA_MS = 1000  # atualização de CPU/memória/disco
INTERVALO_CONEXAO_MS = 10000  # teste automático de conexão


def classificar_qualidade(tempo: float) -> str:
    """Classifica a conexão com base no tempo de resposta."""
    if tempo < 0.5:
        return "🚀 Ótima"
    if tempo < 1.5:
        return "👍 Boa"
    if tempo < 3:
        return "⚠️ Lenta"
    return "🐢 Muito lenta"


def verificar_conexao(url: str = URL_TESTE) -> dict:
    """Mede tempo, status e tamanho da resposta. Sempre retorna um dicionário."""
    try:
        inicio = time.perf_counter()
        resposta = requests.get(url, timeout=TIMEOUT)
        tempo = time.perf_counter() - inicio
        return {
            "ok": True,
            "status": resposta.status_code,
            "tempo": tempo,
            "tamanho_kb": len(resposta.content) / 1024,
            "qualidade": classificar_qualidade(tempo),
        }
    except requests.Timeout:
        return {"ok": False, "erro": "⏱️ Tempo limite excedido. Conexão muito lenta."}
    except requests.ConnectionError:
        return {"ok": False, "erro": "❌ Sem conexão com a internet."}
    except requests.RequestException as e:
        return {"ok": False, "erro": f"⚠️ Erro inesperado: {e}"}


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Monitor de Sistema e Conexão")
        self.geometry("460x520")
        self.minsize(420, 480)

        self.testando = False
        self.var_auto = tk.BooleanVar(value=False)

        self.var_cpu = tk.StringVar(value="0%")
        self.var_mem = tk.StringVar(value="0%")
        self.var_disco = tk.StringVar(value="0%")

        self.var_status = tk.StringVar(value="—")
        self.var_tempo = tk.StringVar(value="—")
        self.var_tamanho = tk.StringVar(value="—")
        self.var_qualidade = tk.StringVar(value="Clique em “Testar conexão”")

        self._montar_interface()

        # A primeira chamada de cpu_percent sempre retorna 0.0; ela serve
        # apenas para "armar" a medição das próximas chamadas.
        psutil.cpu_percent(interval=None)
        self.after(INTERVALO_SISTEMA_MS, self.atualizar_sistema)

    # ---------------------------------------------------------------- UI
    def _montar_interface(self) -> None:
        pad = {"padx": 12, "pady": 6}

        # --- Sistema
        quadro_sis = ttk.LabelFrame(self, text="🖥️  Sistema")
        quadro_sis.pack(fill="x", **pad)
        self.barra_cpu = self._linha_barra(quadro_sis, "CPU", self.var_cpu)
        self.barra_mem = self._linha_barra(quadro_sis, "Memória", self.var_mem)
        self.barra_disco = self._linha_barra(quadro_sis, "Disco", self.var_disco)

        # --- Conexão
        quadro_con = ttk.LabelFrame(self, text="🌐  Conexão com a internet")
        quadro_con.pack(fill="x", **pad)

        self._linha_info(quadro_con, "Status HTTP:", self.var_status)
        self._linha_info(quadro_con, "Tempo de resposta:", self.var_tempo)
        self._linha_info(quadro_con, "Conteúdo recebido:", self.var_tamanho)

        ttk.Label(
            quadro_con, textvariable=self.var_qualidade,
            font=("Segoe UI", 13, "bold"), wraplength=380, justify="center",
        ).pack(pady=10)

        controles = ttk.Frame(quadro_con)
        controles.pack(pady=(0, 10))
        self.btn_testar = ttk.Button(
            controles, text="Testar conexão", command=self.testar_conexao
        )
        self.btn_testar.pack(side="left", padx=5)
        ttk.Checkbutton(
            controles, text="Testar a cada 10 s",
            variable=self.var_auto, command=self._alternar_auto,
        ).pack(side="left", padx=5)

        ttk.Label(
            self,
            text=f"O teste mede o tempo de resposta de {URL_TESTE}\n"
                 "(latência), não a velocidade de download.",
            justify="center", foreground="gray",
        ).pack(pady=8)

    @staticmethod
    def _linha_barra(pai: ttk.Frame, nome: str, variavel: tk.StringVar) -> ttk.Progressbar:
        linha = ttk.Frame(pai)
        linha.pack(fill="x", padx=10, pady=5)
        ttk.Label(linha, text=nome, width=9).pack(side="left")
        barra = ttk.Progressbar(linha, maximum=100, mode="determinate")
        barra.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Label(linha, textvariable=variavel, width=7, anchor="e").pack(side="left")
        return barra

    @staticmethod
    def _linha_info(pai: ttk.Frame, nome: str, variavel: tk.StringVar) -> None:
        linha = ttk.Frame(pai)
        linha.pack(fill="x", padx=10, pady=2)
        ttk.Label(linha, text=nome).pack(side="left")
        ttk.Label(linha, textvariable=variavel).pack(side="right")

    # ----------------------------------------------------------- Sistema
    def atualizar_sistema(self) -> None:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        # os.sep funciona em Windows ("\\") e em Linux/macOS ("/")
        disco = psutil.disk_usage(os.path.abspath(os.sep)).percent

        for barra, var, valor in (
            (self.barra_cpu, self.var_cpu, cpu),
            (self.barra_mem, self.var_mem, mem),
            (self.barra_disco, self.var_disco, disco),
        ):
            barra["value"] = valor
            var.set(f"{valor:.0f}%")

        self.after(INTERVALO_SISTEMA_MS, self.atualizar_sistema)

    # ----------------------------------------------------------- Conexão
    def testar_conexao(self) -> None:
        if self.testando:
            return
        self.testando = True
        self.btn_testar.state(["disabled"])
        self.var_qualidade.set("Testando…")
        # A requisição roda em outra thread para a janela não travar
        threading.Thread(target=self._executar_teste, daemon=True).start()

    def _executar_teste(self) -> None:
        resultado = verificar_conexao()
        self.after(0, self._mostrar_resultado, resultado)

    def _mostrar_resultado(self, r: dict) -> None:
        if r["ok"]:
            self.var_status.set(str(r["status"]))
            self.var_tempo.set(f"{r['tempo']:.2f} s")
            self.var_tamanho.set(f"{r['tamanho_kb']:.2f} KB")
            self.var_qualidade.set(f"Qualidade: {r['qualidade']}")
        else:
            self.var_status.set("—")
            self.var_tempo.set("—")
            self.var_tamanho.set("—")
            self.var_qualidade.set(r["erro"])

        self.testando = False
        self.btn_testar.state(["!disabled"])

    def _alternar_auto(self) -> None:
        if self.var_auto.get():
            self._ciclo_auto()

    def _ciclo_auto(self) -> None:
        if not self.var_auto.get():
            return
        self.testar_conexao()
        self.after(INTERVALO_CONEXAO_MS, self._ciclo_auto)


if __name__ == "__main__":
    App().mainloop()