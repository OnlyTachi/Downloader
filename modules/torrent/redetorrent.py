import requests
import re
from bs4 import BeautifulSoup
from modules.base import BaseSite


# poderia ter juntado com o semtorrent, mas preferi deixar separado para facilitar manutenção futura..
class RedeTorrent(BaseSite):
    def pode_processar(self, url: str) -> bool:
        return "redetorrent" in url

    def get_titulo(self, url: str) -> str:
        try:
            slug = url.split("/")[-2] if url.endswith("/") else url.split("/")[-1]
            return slug.replace("-torrent", "").replace("-download", "")
        except:
            return "redetorrent_export"

    def get_conteudo(self, url: str):
        print("   🔍 (RedeTorrent) Buscando Magnets (Filtro: Dublado/Dual)...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            r = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")

            itens = []

            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.startswith("magnet:"):
                    titulo = link.get("title", link.text).strip()
                    titulo_lower = titulo.lower()

                    # --- FILTRO RIGOROSO ---
                    # Só aceita se tiver "Dublado" ou "Dual" no nome
                    if "dublado" not in titulo_lower and "dual" not in titulo_lower:
                        continue

                    # --- EXTRAÇÃO INTELIGENTE DE NÚMERO ---
                    # Tenta vários padrões para achar o número do episódio
                    # Padrão 1: "S03E01"
                    match_sea = re.search(r"S\d+E(\d+)", titulo, re.IGNORECASE)
                    # Padrão 2: "01º Episódio" ou "01°"
                    match_num = re.search(r"(\d+)[º°]", titulo)
                    # Padrão 3: "Episódio 01"
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
                        # Se for temporada completa ou filme, define um número alto para ficar no fim ou início
                        num = "999"

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
            print(f"❌ Erro ao ler RedeTorrent: {e}")
            return []

    def get_links_download(self, url_conteudo: str) -> dict:
        return {"magnet": url_conteudo}
