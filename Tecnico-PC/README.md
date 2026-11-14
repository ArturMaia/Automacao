# 🌐 INTERNAUTA — Monitor de Sistema e Conexão

Aplicativo desktop simples, feito em **Python + Tkinter**, que mostra em tempo real o uso de **CPU, memória e disco** e testa a **qualidade da conexão com a internet** medindo o tempo de resposta de uma requisição HTTP.

---

## ✨ Funcionalidades

### 🖥️ Monitor de sistema
- Uso de **CPU**, **memória RAM** e **disco**, com barras de progresso e porcentagem.
- Atualização automática a cada **1 segundo**.
- Compatível com Windows, Linux e macOS (o disco monitorado é a raiz do sistema).

### 🌐 Teste de conexão
- Mede o **tempo de resposta** de uma requisição HTTP, o **status HTTP** e o **tamanho do conteúdo** recebido.
- Classifica a qualidade da conexão:

| Tempo de resposta | Classificação   |
|-------------------|-----------------|
| menos de 0,5 s    | 🚀 Ótima        |
| de 0,5 s a 1,5 s  | 👍 Boa          |
| de 1,5 s a 3 s    | ⚠️ Lenta        |
| 3 s ou mais       | 🐢 Muito lenta  |

- Tratamento de erros: **tempo limite excedido**, **sem conexão** e **erros inesperados**.
- Botão **Testar conexão** para teste manual e opção **Testar a cada 10 s** para teste automático.
- O teste roda em uma *thread* separada, então a janela **nunca trava** durante a requisição.

> ℹ️ O teste mede a **latência** (tempo de resposta de `https://www.google.com`), e **não** a velocidade de download.

---

## 📋 Requisitos

- **Python 3.8** ou superior
- Bibliotecas:
  - [`psutil`](https://pypi.org/project/psutil/)
  - [`requests`](https://pypi.org/project/requests/)
- **Tkinter** (já incluído na instalação padrão do Python no Windows e no macOS)

No **Linux** (Debian/Ubuntu), talvez seja necessário instalar o Tkinter separadamente:

```bash
sudo apt install python3-tk
```

---

## 🚀 Instalação e uso

1. **Clone o repositório** (ou baixe o arquivo `INTERNAUTA.py`):

   ```bash
   git clone <URL-DO-SEU-REPOSITORIO>
   cd <PASTA-DO-PROJETO>
   ```

2. **(Opcional) Crie um ambiente virtual:**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux / macOS
   source venv/bin/activate
   ```

3. **Instale as dependências:**

   ```bash
   pip install psutil requests
   ```

4. **Execute o programa:**

   ```bash
   python INTERNAUTA.py
   ```

---

## ⚙️ Configuração

As constantes no início do arquivo `INTERNAUTA.py` permitem personalizar o comportamento:

| Constante               | Padrão                    | Descrição                                      |
|-------------------------|---------------------------|------------------------------------------------|
| `URL_TESTE`             | `https://www.google.com`  | Endereço usado no teste de conexão             |
| `TIMEOUT`               | `5`                       | Tempo máximo de espera da requisição (segundos)|
| `INTERVALO_SISTEMA_MS`  | `1000`                    | Intervalo de atualização de CPU/memória/disco  |
| `INTERVALO_CONEXAO_MS`  | `10000`                   | Intervalo do teste automático de conexão       |

---

## 🗂️ Estrutura do projeto

```
.
├── INTERNAUTA.py   # Código-fonte completo da aplicação
└── README.md       # Este arquivo
```

### Principais componentes do código

- `classificar_qualidade(tempo)` — converte o tempo de resposta em uma classificação de qualidade.
- `verificar_conexao(url)` — faz a requisição e sempre retorna um dicionário com o resultado (ou o erro).
- `App(tk.Tk)` — classe da interface gráfica, com os métodos de atualização do sistema e controle do teste de conexão.

---

## 🛠️ Tecnologias utilizadas

- [Python](https://www.python.org/)
- [Tkinter / ttk](https://docs.python.org/3/library/tkinter.html) — interface gráfica
- [psutil](https://github.com/giampaolo/psutil) — métricas do sistema
- [requests](https://requests.readthedocs.io/) — requisições HTTP

---

## 💡 Ideias para o futuro

- Histórico e gráficos de latência ao longo do tempo
- Teste de velocidade de download/upload
- Escolha da URL de teste pela interface
- Alertas quando a conexão ficar lenta ou cair
- Empacotamento em executável (`.exe`) com PyInstaller

---

## 📄 Licença

Defina aqui a licença do projeto (por exemplo, [MIT](https://opensource.org/licenses/MIT)).
