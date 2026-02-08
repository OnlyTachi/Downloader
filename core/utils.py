import requests
import re
import os
import sys
import zipfile


def limpar_tela():
    """Limpa o console de acordo com o sistema operacional."""
    os.system("clear" if os.name == "posix" else "cls")


def format_size(size_bytes):
    """Formata bytes para um formato legível (KB, MB, GB, etc)."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    s = float(size_bytes)
    while s >= 1024 and i < len(size_name) - 1:
        s /= 1024
        i += 1
    return f"{s:.2f} {size_name[i]}"


def sanitizar_nome(nome):
    """Remove caracteres inválidos para nomes de pasta/arquivo."""
    return re.sub(r'[<>:"/\\|?*]', "", nome).strip()


def resolve_redirect(url):
    """Resolve links encurtados para obter a URL real."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=15)
        return response.url
    except requests.RequestException:
        try:
            response = requests.get(url, allow_redirects=True, stream=True, timeout=15)
            response.close()
            return response.url
        except:
            return url


def extract_drive_id(url):
    """Extrai o ID do arquivo de uma URL do Google Drive."""
    patterns = [
        r"/file/d/([a-zA-Z0-9_-]+)",
        r"id=([a-zA-Z0-9_-]+)",
        r"/d/([a-zA-Z0-9_-]+)",
        r"drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_confirm_token(response):
    """Extrai o token de confirmação para arquivos grandes do Drive."""
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None


def save_stream(response, filepath):
    """Salva o stream de dados no arquivo com barra de progresso."""
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024 * 1024  # 1MB chunks
    wrote = 0

    try:
        with open(filepath, "wb") as f:
            for data in response.iter_content(block_size):
                wrote += len(data)
                f.write(data)
                if total_size > 0:
                    percent = (wrote / total_size) * 100
                    sys.stdout.write(
                        f"\rBaixando: {percent:.1f}% ({format_size(wrote)} / {format_size(total_size)})"
                    )
                else:
                    sys.stdout.write(
                        f"\rBaixado: {format_size(wrote)} (Tamanho total desconhecido)"
                    )
                sys.stdout.flush()
        print("\n✅ Download concluído!")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao salvar arquivo: {e}")
        return False


def download_drive_file(url, destination_folder="downloads"):
    """Lógica completa para baixar arquivos do Google Drive."""
    print(f"🔍 Analisando link...")
    real_url = resolve_redirect(url)
    file_id = extract_drive_id(real_url)

    if not file_id:
        print("❌ Não foi possível extrair o ID do Google Drive.")
        return None

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    session = requests.Session()
    download_url = "https://docs.google.com/uc?export=download"

    # Primeira tentativa para pegar cookies e verificar se precisa de confirmação
    response = session.get(download_url, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(download_url, params=params, stream=True)

    # Tenta obter nome do arquivo
    cd = response.headers.get("Content-Disposition")
    filename = None
    if cd:
        fname_match = re.findall('filename="(.+)"', cd)
        if not fname_match:
            fname_match = re.findall("filename=(.+)", cd)
        if fname_match:
            filename = fname_match[0]

    if not filename:
        filename = f"drive_file_{file_id}"

    filename = sanitizar_nome(filename)
    filepath = os.path.join(destination_folder, filename)

    print(f"📦 Arquivo: {filename}")
    if save_stream(response, filepath):
        return filepath
    return None


def compactar_pasta(caminho_pasta):
    """Compacta arquivos .mp4 de uma pasta em um arquivo ZIP."""
    if not os.path.exists(caminho_pasta):
        print(f"❌ Pasta não encontrada: {caminho_pasta}")
        return False

    try:
        nome_zip = f"{caminho_pasta}.zip"
        print(f"\n📦 Compactando arquivos MP4 em: {os.path.basename(nome_zip)}...")

        with zipfile.ZipFile(nome_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            count = 0
            for root, dirs, files in os.walk(caminho_pasta):
                for file in files:
                    if file.lower().endswith(".mp4"):
                        caminho_completo = os.path.join(root, file)
                        # Salva apenas o nome do arquivo no zip, sem a estrutura de pastas
                        zipf.write(caminho_completo, arcname=file)
                        count += 1
                        sys.stdout.write(f"\r   -> Adicionado: {file}")
                        sys.stdout.flush()

        if count > 0:
            print(f"\n✅ ZIP criado com sucesso! ({count} arquivos)")
            return True
        else:
            print("\n⚠️ Nenhum arquivo .mp4 encontrado para compactar.")
            if os.path.exists(nome_zip):
                os.remove(nome_zip)
            return False
    except Exception as e:
        print(f"\n❌ Erro ao zipar: {e}")
        return False


if __name__ == "__main__":
    limpar_tela()
    print("=== Google Drive Downloader & Zipper Tool ===\n")

    # Exemplo de fluxo de uso:
    link = input("Cole o link do Google Drive (ou t.co): ").strip()
    if link:
        arquivo_baixado = download_drive_file(link)

        if arquivo_baixado:
            opcao = input(
                "\nDeseja compactar a pasta de downloads agora? (s/n): "
            ).lower()
            if opcao == "s":
                compactar_pasta("downloads")
    else:
        print("Saindo...")


# talvez ninguem use isso nunca... mas ta aqui se precisar (eu utilizo bastante)
