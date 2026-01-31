import os
import sys
from torrentool.api import Torrent

# Lista de Trackers Públicos (Essenciais para o torrent funcionar)
TRACKERS_PUBLICOS = [
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.moeking.me:6969/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "http://tracker.openbittorrent.com:80/announce",
    "udp://tracker.coppersurfer.tk:6969/announce",
    "udp://9.rarbg.to:2710/announce",
]
# talvez adicionar mais trackers conforme necessário ou suporte a trackers privados no futuro...


def criar_torrent_da_pasta(caminho_pasta):
    """
    Lê uma pasta de arquivos e cria um arquivo .torrent correspondente.
    """
    if not os.path.exists(caminho_pasta):
        print(f"❌ Pasta não encontrada: {caminho_pasta}")
        return None

    # Nome do torrent será o nome da pasta
    nome_torrent = os.path.basename(caminho_pasta.rstrip(os.sep))
    arquivo_saida = f"{caminho_pasta}.torrent"

    print(f"\n🔨 Criando Torrent para: {nome_torrent}...")

    try:
        # Cria o objeto Torrent
        t = Torrent.create_from(caminho_pasta)

        # Configurações do Torrent
        t.announce_urls = TRACKERS_PUBLICOS
        t.comment = "Gerado por Python Modular Downloader"
        t.created_by = "Python Script"
        t.private = False  # Torrent público

        # Salva o arquivo
        t.to_file(arquivo_saida)

        print(f"✅ Arquivo Torrent criado com sucesso!")
        print(f"   📂 Arquivo: {arquivo_saida}")
        print(f"   🧲 Magnet Link (Copie para testar no qBittorrent):")
        print("-" * 50)
        print(t.magnet_link)
        print("-" * 50)

        return t.magnet_link

    except Exception as e:
        print(f"❌ Erro ao criar torrent: {e}")
        return None
