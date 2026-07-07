# 📥 Modular Hybrid Downloader

Um sistema robusto e modular escrito em Python para baixar animes, séries e extrair magnet links de torrents automaticamente. O projeto utiliza uma abordagem híbrida (**Requests + Selenium**) para contornar proteções anti-bot e capturar links de vídeo ou torrents de forma inteligente.

---

## 🚀 Funcionalidades

- **Arquitetura Modular:** Fácil de adicionar novos sites criando apenas um arquivo na pasta `modules`.
- **Híbrido e Furtivo:**
- Usa `requests` para velocidade quando possível.
- Usa **Selenium (Modo Stealth)** para sites com proteção (Cloudflare/Anti-bot) ou carregamento dinâmico (JS).

- **Sites de Vídeo (Animes):** Baixa arquivos `.mp4` sequencialmente, detecta qualidade (F-HD, HD, SD) e organiza em pastas.
- **Sites de Torrent:**
- Extrai **Magnet Links** da página.
- **Filtro Inteligente:** Seleciona apenas arquivos "Dublado" ou "Dual Áudio".
- **Ordenação:** Organiza os episódios na ordem correta (01, 02, 03...).

- **Automação:** Envio direto de links para clientes Torrent (ex: qBittorrent).
- **Gerador de Torrent:** Cria arquivos `.torrent` a partir de pastas locais.
- **Utilitários:** Compactação automática em ZIP pós-download.

---

## 📋 Sites Suportados Atualmente

| Categoria             | Sites                     |
| --------------------- | ------------------------- |
| **Vídeos (MP4)**      | AnimeFire, AnimeDrive     |
| **Torrents (Magnet)** | Rede Torrent, Sem Torrent |

---

## ⚙️ Instalação

### Pré-requisitos

- Python 3.8 ou superior.
- Google Chrome instalado.

### Passo a Passo

1. **Clone o repositório:**

```bash
git clone https://github.com/OnlyTachi/Downloader.git
cd Downloader

```

2. **Instale as dependências:**

```bash
pip install -r requirements.txt

```

> **Nota:** O `requirements.txt` deve conter: `requests`, `beautifulsoup4`, `selenium`, `webdriver-manager`, `torrentool`.

---

## 🖥️ Como Usar

Execute o arquivo principal:

```bash
python main.py

```

### Menu Principal

1. **Processar Link:** Cole a URL da obra. O sistema identifica automaticamente se é vídeo ou torrent.

- **Animes:** Salva vídeos em `downloads/NomeDoAnime`.
- **Torrents:** Filtra dublados e gera `LISTA_MAGNETS.txt`.

2. **Criar Torrent Local:** Transforma uma pasta em `.torrent` com trackers públicos embutidos.
3. **Sair:** Encerra os drivers e o programa com segurança.

---

## 🛠️ Guia de Desenvolvimento (Novos Módulos)

O sistema é extensível. Para adicionar um novo site, crie um arquivo em `modules/categoria/seusite.py` herdando de `BaseSite`.

### 1. Estrutura do Módulo

```python
from modules.base import BaseSite

class SeuNovoSite(BaseSite):
    def pode_processar(self, url: str) -> bool:
        return "seusite.com" in url

    def get_titulo(self, url: str) -> str:
        return "titulo-da-obra"

    def get_conteudo(self, url: str):
        # Lógica de extração de episódios/links
        pass

    def get_links_download(self, url_conteudo: str) -> dict:
        # Retorna dict com qualidades ou magnet link
        pass

```

### 2. Registro

No `main.py`, adicione sua classe à lista `REGISTRY`:

```python
REGISTRY = [
    AnimeFire(),
    SeuNovoSite()
]

```

---

## 📁 Estrutura do Projeto

```text
Downloader/
│
├── core/                   # Núcleo do sistema
│   ├── driver.py           # Gerenciador do Selenium (Anti-detect)
│   ├── downloader.py       # Motor de download HTTP
│   ├── torrent_manager.py  # Criador de arquivos .torrent
│   └── utils.py            # Limpeza de tela, ZIP, formatação
│
├── modules/                # Módulos dos sites (Plugins)
│   ├── base.py             # Classe Abstrata (Interface)
│   ├── animes/             # Sites de streaming
│   │   ├── animefire.py
│   │   └── animedrive.py
│   └── torrent/            # Sites de torrent
│       ├── redetorrent.py
│       └── semtorrent.py
│
├── downloads/              # Pasta onde os arquivos são salvos
├── main.py                 # Ponto de entrada (Menu)
└── requirements.txt        # Dependências


```

---

## ⚠️ Aviso Legal

Este software foi desenvolvido para fins **educacionais**. O usuário é inteiramente responsável pelo uso da ferramenta e pelo cumprimento das leis de direitos autorais vigentes.

---
