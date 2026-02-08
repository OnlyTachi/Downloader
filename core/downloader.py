import os
import requests
import re
import sys
from tqdm import tqdm


class Downloader:
    def __init__(self, output_folder="downloads"):
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
        }

    def download_file(self, url, filename, folder_name=None, referer=None):
        """
        Gerencia o download, detectando automaticamente o tipo de link.
        """
        target_folder = self.output_folder
        if folder_name:
            target_folder = os.path.join(self.output_folder, folder_name)
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

        if not os.path.splitext(filename)[1]:
            filename += ".mp4"

        filepath = os.path.join(target_folder, filename)

        # --- PROTOCOLO GOOGLE DRIVE ---
        if "drive.google.com" in url:
            print(
                f"   🧠 Detectado link Google Drive. Iniciando protocolo específico..."
            )
            return self._download_google_drive(url, filepath)

        return self._download_generic(url, filepath, referer)

    def _download_generic(self, url, filepath, referer=None):
        session = requests.Session()
        headers = self.base_headers.copy()
        headers["Referer"] = referer if referer else "https://google.com"

        try:
            response = session.get(
                url, headers=headers, stream=True, timeout=60, allow_redirects=True
            )

            if response.status_code == 403:
                print("   🛡️ Erro 403 detectado. Tentando sem Referer...")
                headers.pop("Referer", None)
                response = session.get(
                    url, headers=headers, stream=True, timeout=60, allow_redirects=True
                )

            response.raise_for_status()

            self._save_content(response, filepath)
            return True

        except Exception as e:
            print(f"   ❌ Erro no download: {e}")
            if os.path.exists(filepath):
                os.remove(filepath)
            return False

    def _download_google_drive(self, url, filepath):
        try:
            file_id = self._get_drive_id(url)
            if not file_id:
                print("   ❌ Não foi possível extrair o ID do Google Drive.")
                return False

            download_url = "https://docs.google.com/uc?export=download"
            session = requests.Session()

            # 1. Tentativa inicial
            response = session.get(
                download_url,
                params={"id": file_id},
                stream=True,
                headers=self.base_headers,
            )

            # 2. Bypass de confirmação de vírus (se necessário)
            token = self._get_confirm_token(response)
            if token:
                print("   🛡️ Bypassing verificação de vírus do Google...")
                params = {"id": file_id, "confirm": token}
                response = session.get(
                    download_url, params=params, stream=True, headers=self.base_headers
                )

            if response.status_code != 200:
                print(f"   ❌ Erro Google Drive: Status {response.status_code}")
                return False

            self._save_content(response, filepath)
            return True

        except Exception as e:
            print(f"   ❌ Erro no download do Drive: {e}")
            return False

    def _get_drive_id(self, url):
        patterns = [
            r"/file/d/([a-zA-Z0-9_-]+)",
            r"id=([a-zA-Z0-9_-]+)",
            r"/open\?id=([a-zA-Z0-9_-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _get_confirm_token(self, response):
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                return value
        return None

    def _save_content(self, response, filepath):
        """Salva o stream no disco com barra de progresso tqdm"""
        total_size = int(response.headers.get("content-length", 0))
        block_size = 8192  # 8 KiB

        print(f"   💾 Salvando arquivo...")

        with tqdm(
            total=total_size,
            unit="iB",
            unit_scale=True,
            desc="   ⏬ Progresso",
            leave=True,
        ) as progress_bar:
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))

        # Verificação de integridade básica
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            if size < 2048:  # Se menor que 2KB, pode ser uma página de erro HTML
                try:
                    with open(filepath, "r", errors="ignore") as f:
                        content = f.read(500)
                        if "<html" in content or "DOCTYPE" in content:
                            print(
                                "\n   ⚠️ ALERTA: O arquivo baixado parece ser uma página de erro (HTML)."
                            )
                            print(
                                "      Verifique se o link é público ou se a cota foi excedida."
                            )
                            return False
                except:
                    pass

            print(f"   ✅ Download concluído: {os.path.basename(filepath)}")
            return True
        return False
