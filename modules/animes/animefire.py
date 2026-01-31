import requests
from bs4 import BeautifulSoup
from modules.base import BaseSite
from core.driver import get_driver


# quando hospedado pelo google e algo mais dificil de lidar... por enquanto sem suporte
class AnimeFire(BaseSite):
    def pode_processar(self, url: str) -> bool:
        # Agora aceita .io, .plus, .net, etc.
        return "animefire." in url

    def get_titulo(self, url: str) -> str:
        try:
            return url.split("/animes/")[-1].split("/")[0]
        except:
            return "anime_fire_download"

    def get_conteudo(self, url: str):
        print("   🔍 (Fire) Buscando lista de episódios...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            if not url.startswith("http"):
                url = "https://" + url

            r = requests.get(url, headers=headers, timeout=10)

            if r.status_code != 200:
                print(f"   ⚠️ Erro HTTP {r.status_code} ao acessar o site.")

            soup = BeautifulSoup(r.text, "html.parser")
            episodios = []

            # Seletor genérico para links de episódios
            links = soup.find_all("a", class_="lEp")

            for link in links:
                ep_url = link.get("href")
                try:
                    num = ep_url.split("/")[-1]
                except:
                    num = "00"

                episodios.append({"numero": num, "url": ep_url})

            return episodios[::-1]
        except Exception as e:
            print(f"❌ Erro ao ler AnimeFire: {e}")
            return []

    def get_links_download(self, url_ep: str) -> dict:
        links = {}

        # MÉTODO 1: Requests (Rápido - Tentativa de converter URL para /download/)
        try:
            url_dl = url_ep.replace("/animes/", "/download/")
            r = requests.get(url_dl, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    txt = a.text.strip()
                    if txt in ["F-HD", "FullHD", "HD", "SD"]:
                        links[txt] = a["href"]
        except:
            pass

        if links:
            return links

        # MÉTODO 2: Selenium (Lento - Fallback)
        print("   ⚠️ Método rápido falhou. Usando Selenium...")
        driver = get_driver()
        if driver:
            try:
                driver.get(url_ep)
                elems = driver.find_elements("tag name", "a")
                for elem in elems:
                    try:
                        href = elem.get_attribute("href")
                        txt = elem.text.strip()
                        if (
                            txt in ["F-HD", "FullHD", "HD", "SD"]
                            and href
                            and "http" in href
                        ):
                            links[txt] = href
                    except:
                        continue
            except Exception as e:
                print(f"   ❌ Erro Selenium: {e}")

        return links
