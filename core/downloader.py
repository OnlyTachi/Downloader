import os
import requests
import sys
from .utils import formatar_tamanho


def baixar_arquivo(url, caminho_destino, referer=None):
    # Headers aprimorados do antigo utils.py para evitar 403 (talvez com alguns bugs)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Referer": referer if referer else "https://google.com",
    }

    session = requests.Session()

    try:
        # allow_redirects=True é crucial para links do Google/Blogspot
        r = session.get(
            url, headers=headers, stream=True, timeout=60, allow_redirects=True
        )

        # Lógica de Retry para erro 403 (comum no Google Video)
        if r.status_code == 403:
            print("   🛡️ Erro 403 detectado. Tentando sem Referer...")
            headers.pop("Referer", None)
            r = session.get(
                url, headers=headers, stream=True, timeout=60, allow_redirects=True
            )

        if r.status_code == 200:
            total_size = int(r.headers.get("content-length", 0))
            t_str = formatar_tamanho(total_size)

            print(f"   💾 Salvando ({t_str})...")

            with open(caminho_destino, "wb") as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int(100 * downloaded / total_size)
                            sys.stdout.write(f"\r   ⏬ Progresso: {percent}%")
                            sys.stdout.flush()

            print("\n   ✅ Download concluído!")
            return True
        else:
            print(f"\n   ❌ Erro HTTP: {r.status_code}")
            return False

    except Exception as e:
        print(f"\n   ❌ Erro no download: {e}")
        if os.path.exists(caminho_destino):
            os.remove(caminho_destino)
        return False
