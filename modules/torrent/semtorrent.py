import requests
import re
from bs4 import BeautifulSoup
from modules.base import BaseSite


class SemTorrent(BaseSite):
    def pode_processar(self, url: str) -> bool:
        return "semtorrent.com" in url

    def get_titulo(self, url: str) -> str:
        try:
            slug = url.strip("/").split("/")[-1]
            return slug
        except:
            return "semtorrent_export"

    def get_conteudo(self, url: str):
        print("   🔍 (SemTorrent) Buscando Magnets (Filtro: Dublado/Dual)...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")

            itens = []

            # O site usa estrutura similar ao RedeTorrent: (amem)
            # <a> com href="magnet:..." e title="Nome do Episódio"
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("magnet:"):
                    # O título geralmente está no atributo 'title'
                    titulo = link.get("title", link.text).strip()
                    titulo_lower = titulo.lower()

                    # --- FILTRO RIGOROSO ---
                    # Garante que seja Dublado ou Dual Áudio
                    if "dublado" not in titulo_lower and "dual" not in titulo_lower:
                        continue

                    # --- EXTRAÇÃO DE NÚMERO (REGEX) ---
                    # Padrão: "01º EPISÓDIO", "S02E01", "Episódio 01"
                    match_num = re.search(r"(\d+)[º°]", titulo)
                    match_sea = re.search(r"S\d+E(\d+)", titulo, re.IGNORECASE)
                    match_ep_txt = re.search(
                        r"Epis[oó]dio\s*(\d+)", titulo, re.IGNORECASE
                    )

                    if match_sea:
                        num = match_sea.group(1)
                    elif match_num:
                        num = match_num.group(1)
                    elif match_ep_txt:
                        num = match_ep_txt.group(1)
                    else:
                        num = "999"  # Fica no final se não achar número

                    itens.append(
                        {
                            "numero": num.zfill(2),
                            "titulo_completo": titulo,
                            "url": href,
                            "tipo": "magnet",
                        }
                    )

            # --- ORDENAÇÃO ---
            def chave_ordenacao(item):
                try:
                    return int(item["numero"])
                except:
                    return 9999

            itens.sort(key=chave_ordenacao)

            if not itens:
                print("   ⚠️ Nenhum link encontrado com os critérios (Dublado/Dual).")
            else:
                print(f"   ✅ {len(itens)} links filtrados e ordenados.")

            return itens

        except Exception as e:
            print(f"❌ Erro ao ler SemTorrent: {e}")
            return []

    def get_links_download(self, url_conteudo: str) -> dict:
        return {"magnet": url_conteudo}
