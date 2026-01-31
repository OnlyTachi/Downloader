import os
import sys
import webbrowser
import platform
import subprocess
from core.driver import kill_driver
from core.downloader import baixar_arquivo
from core.utils import limpar_tela, compactar_pasta, sanitizar_nome
from core.torrent_manager import criar_torrent_da_pasta

# Importação dos Módulos
from modules.animes.animefire import AnimeFire
from modules.animes.animedrive import AnimeDrive
from modules.torrent.redetorrent import RedeTorrent
from modules.torrent.semtorrent import SemTorrent

# Registro de Sites Suportados
REGISTRY = [AnimeFire(), AnimeDrive(), RedeTorrent(), SemTorrent()]


def identificar_site(url):
    for site in REGISTRY:
        if site.pode_processar(url):
            return site
    return None


def abrir_magnets_no_sistema(lista_magnets):
    """
    Tenta abrir os magnet links diretamente no cliente torrent padrão do sistema.
    """
    qtd = len(lista_magnets)
    print(f"\n🚀 Preparando para enviar {qtd} links para o seu cliente Torrent...")
    print("   (Isso pode abrir várias janelas de confirmação no seu programa)")

    confirm = input("   Deseja continuar? (s/n): ").lower()
    if confirm != "s":
        return

    count = 0
    for item in lista_magnets:
        magnet = item["url"]
        try:
            if sys.platform == "win32":
                os.startfile(magnet)
            elif sys.platform == "darwin":
                subprocess.run(["open", magnet])
            else:
                subprocess.run(["xdg-open", magnet])

            count += 1
            print(f"   ✅ Enviado: {item['numero']}")
        except Exception as e:
            print(f"   ❌ Erro ao abrir magnet: {e}")
            try:
                webbrowser.open(magnet)
            except:
                pass

    print(f"\n✨ {count} Torrents enviados para a fila!")


def salvar_lista_magnets(caminho_pasta, lista_magnets):
    """Gera um arquivo TXT com todos os magnets encontrados"""
    arquivo_txt = os.path.join(caminho_pasta, "LISTA_MAGNETS.txt")

    with open(arquivo_txt, "w", encoding="utf-8") as f:
        f.write("=== LISTA DE MAGNET LINKS ===\n")
        f.write(f"Gerado por Python Downloader\n")
        f.write("=" * 40 + "\n\n")

        for item in lista_magnets:
            f.write(f"📺 {item['titulo_completo']}\n")
            f.write(f"{item['url']}\n")
            f.write("-" * 40 + "\n")

    print(f"\n📄 Arquivo de Magnets gerado: {arquivo_txt}")

    print("\nO que deseja fazer?")
    print("1 - Apenas sair (O arquivo TXT já está salvo)")
    print("2 - Abrir todos os links no Cliente Torrent")

    op = input("Escolha: ")
    if op == "2":
        abrir_magnets_no_sistema(lista_magnets)


def processar_download_anime(url):
    site = identificar_site(url)
    if not site:
        print("❌ Site não suportado ou URL inválida.")
        return

    print(f"🔎 Processando com módulo: {site.__class__.__name__}")

    nome_obra_raw = site.get_titulo(url)
    nome_obra = sanitizar_nome(nome_obra_raw)
    print(f"📂 Obra: {nome_obra}")

    lista_conteudo = site.get_conteudo(url)
    if not lista_conteudo:
        print("❌ Nenhum conteúdo encontrado.")
        return

    print(f"📋 {len(lista_conteudo)} itens encontrados.")

    pasta_destino = os.path.join("downloads", nome_obra)
    os.makedirs(pasta_destino, exist_ok=True)

    if lista_conteudo and lista_conteudo[0].get("tipo") == "magnet":
        print("\n🧲 Modo Magnet Link detectado!")
        salvar_lista_magnets(pasta_destino, lista_conteudo)
        return

    # Fluxo normal para sites de vídeo (AnimeFire/Drive)
    baixados_count = 0
    for item in lista_conteudo:
        num = item["numero"]
        link_conteudo = item["url"]

        arquivo_base = os.path.join(pasta_destino, f"{num}.mp4")

        if os.path.exists(arquivo_base) and os.path.getsize(arquivo_base) > 1024:
            print(f"⏭️  Ep {num} já existe.")
            baixados_count += 1
            continue

        print(f"\n🎬 Processando Ep {num}...")
        links = site.get_links_download(link_conteudo)

        if not links:
            print("   ❌ Nenhum link de vídeo extraído.")
            continue

        url_video = (
            links.get("F-HD")
            or links.get("FullHD")
            or links.get("HD")
            or links.get("SD")
            or list(links.values())[0]
        )

        print(f"   ⚡ Baixando: {url_video[:40]}...")
        if baixar_arquivo(url_video, arquivo_base, referer=link_conteudo):
            baixados_count += 1

    # Finalização (Apenas para vídeos)
    print("\n" + "=" * 40)
    print(f"🏁 Finalizado: {baixados_count}/{len(lista_conteudo)} itens.")

    if baixados_count > 0:
        print("\nOpções pós-download:")
        print("1 - Sair")
        print("2 - Criar ZIP")
        print("3 - Criar Torrent (Semear)")

        resp = input("Escolha: ")
        if resp == "2":
            compactar_pasta(pasta_destino)
        elif resp == "3":
            criar_torrent_da_pasta(pasta_destino)


def menu():
    while True:
        limpar_tela()
        print(
            r"""
     _   _ _____  __  __  ___  ____  
    | \ | | ____| \ \/ / / _ \|  _ \ 
    |  \| |  _|    \  / | | | | |_) |
    | |\  | |___   /  \ | |_| |  __/ 
    |_| \_|_____| /_/\_\ \___/|_|    
    
    >>> MODULAR DOWNLOADER 3.2 <<<
    (Multi-Site + Auto-Torrent Adder)
        """
        )
        print("1. Processar Link")
        print("2. Criar Torrent de Pasta Local")
        print("3. Sair")

        opcao = input("\nEscolha: ")

        if opcao == "1":
            url = input("🔗 Cole o link: ")
            processar_download_anime(url)
            input("\nENTER para voltar...")
        elif opcao == "2":
            path = input("📂 Caminho da pasta: ")
            criar_torrent_da_pasta(path)
            input("\nENTER para voltar...")
        elif opcao == "3":
            kill_driver()
            sys.exit()


if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        kill_driver()
        print("\n👋 Interrompido.")
