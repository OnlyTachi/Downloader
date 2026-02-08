import os
from typing import Any, Dict, List, Optional

import requests
from modules.base import BaseSite
from core.utils import extract_drive_id, download_drive_file, save_stream


class GoogleDrive(BaseSite):
    def pode_processar(self, url: str) -> bool:
        return "drive.google.com" in url or "docs.google.com" in url

    def get_titulo(self, url: str) -> str:
        return "Google Drive Download"

    def download(self, url: str, folder: str, session: Any) -> bool:
        """Download de arquivo do Google Drive.

        Args:
            url: URL do Google Drive.
            folder: Pasta de destino para o arquivo.
            session: Sessão requests para fazer a requisição.

        Returns:
            True se download bem-sucedido, False caso contrário.
        """
        file_id = extract_drive_id(url)
        if not file_id:
            print("Não foi possível extrair o ID do arquivo do Google Drive.")
            return False

        download_url = "https://docs.google.com/uc?export=download"
        params = {"id": file_id}

        print(f"Processando Google Drive ID: {file_id}")

        try:
            response = session.get(download_url, params=params, stream=True)

            token = self._get_confirm_token(response)
            if token:
                params["confirm"] = token
                print(
                    "Token de confirmação recebido (arquivo grande), "
                    "reiniciando requisição..."
                )
                response = session.get(download_url, params=params, stream=True)

            filename = download_drive_file(response.headers.get("Content-Disposition"))
            if not filename:
                filename = f"gdrive_{file_id}"  # Fallback

            filepath = os.path.join(folder, filename)
            print(f"Baixando: {filename}")

            save_stream(response, filepath)
            return True

        except Exception as e:
            print(f"Erro no download do Google Drive: {e}")
            return False

    def get_conteudo(self, url: str) -> List[Dict[str, str]]:
        """Valida e prepara conteúdo do Google Drive para download.

        Args:
            url: URL do Google Drive.

        Returns:
            Lista com informações do item ou lista vazia se inválido.
        """
        print(f"🔎 Analisando Link do Google Drive...")

        file_id = extract_drive_id(url)
        if not file_id:
            print("❌ Erro: Não foi possível extrair o ID do arquivo.")
            return []

        if not self._verificar_status_arquivo(file_id):
            return []

        return [{"numero": "01", "url": url, "tipo": "video"}]

    def get_links_download(self, url_conteudo: str) -> Dict[str, str]:
        return {"Drive": url_conteudo}

    def _verificar_status_arquivo(self, file_id: str) -> bool:
        """Verifica se o arquivo está online, banido ou deletado.

        Args:
            file_id: ID do arquivo no Google Drive.

        Returns:
            True se arquivo está acessível, False caso esté banido/deletado.
        """
        url_check = f"https://drive.google.com/uc?id={file_id}&export=download"

        try:
            response = requests.get(url_check, stream=True)

            if response.status_code == 404:
                print(
                    "❌ ERRO: Arquivo não encontrado (404). "
                    "O link pode estar quebrado."
                )
                return False

            content_type = response.headers.get("Content-Type", "").lower()

            if "text/html" in content_type:
                content_sample = ""
                try:
                    for chunk in response.iter_content(chunk_size=4096):
                        content_sample += chunk.decode("utf-8", errors="ignore")
                        if len(content_sample) > 5000:
                            break
                except:
                    pass

                content_lower = content_sample.lower()

                if (
                    "viola nossos termos" in content_lower
                    or "violate our terms" in content_lower
                ):
                    print("\n❌ ⛔ ARQUIVO BANIDO PELO GOOGLE!")
                    print("   Motivo: Violação dos Termos de Serviço.")
                    print("   Ação: Download cancelado para este item.\n")
                    return False

                if "não existe" in content_lower or "doesn't exist" in content_lower:
                    print("\n❌ 🗑️  ARQUIVO DELETADO ou URL INVÁLIDA.")
                    print("   O Google diz que o arquivo não existe.\n")
                    return False

                if (
                    "solicite acesso" in content_lower
                    or "request access" in content_lower
                ):
                    print("\n❌ 🔒 ACESSO NEGADO.")
                    print("   O arquivo é privado e você não tem permissão.\n")
                    return False

                if (
                    "verificação de vírus" in content_lower
                    or "virus scan" in content_lower
                ):
                    print(
                        "⚠️  Aviso: Arquivo grande "
                        "(sem verificação de vírus). Prosseguindo..."
                    )
                    return True

            print("✅ Link do Drive parece Válido.")
            return True

        except Exception as e:
            print(f"⚠️ Erro ao verificar status do Drive: {e}")
            # Na dúvida, tentamos baixar
            return True

    def _get_confirm_token(self, response: Any) -> Optional[str]:
        """Busca o token de confirmação para arquivos grandes do Drive.

        Args:
            response: Resposta do requests.

        Returns:
            Token de confirmação ou None se não encontrado.
        """
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                return value
        return None
