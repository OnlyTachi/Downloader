import time
from modules.base import BaseSite
from core.driver import get_driver
from bs4 import BeautifulSoup
import requests


# animedrive e meio instável, mas vamos manter o suporte básico
class AnimeDrive(BaseSite):
    def pode_processar(self, url: str) -> bool:
        return "animesdrive" in url or "animedrive" in url

    def get_titulo(self, url: str) -> str:
        try:
            return url.split("/anime/")[-1].split("/")[0]
        except:
            return "animedrive_download"

    def get_conteudo(self, url: str):
        print("   🔍 (Drive) Buscando lista de episódios...")
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            episodios = []

            # Lógica extraída do seu antigo anime.py (_get_animedrive_eps)
            lista = soup.find("ul", class_="episodios")
            if lista:
                for li in lista.find_all("li"):
                    div = li.find("div", class_="episodiotitle")
                    if div:
                        a = div.find("a", href=True)
                        if a:
                            # Extrai numero do link: .../episodio-01
                            href = a["href"]
                            try:
                                num = href.split("-")[-1]
                            except:
                                num = "XX"
                            episodios.append({"numero": num, "url": href})

            # AnimeDrive lista decrescente, inverte para ordem correta
            return episodios[::-1]
        except Exception as e:
            print(f"❌ Erro AnimeDrive: {e}")
            return []

    def get_links_download(self, url_ep: str) -> dict:
        """
        AnimeDrive geralmente requer Selenium pois os links são ofuscados ou dinâmicos.
        """
        links = {}
        driver = get_driver()
        if not driver:
            return links

        try:
            driver.get(url_ep)
            time.sleep(2)  # Espera carregar scripts

            # Tenta encontrar links diretos no HTML renderizado
            # Baseado na lógica de extração genérica do utils.py antigo
            elems = driver.find_elements("xpath", "//a")
            for elem in elems:
                try:
                    txt = elem.text.strip()
                    href = elem.get_attribute("href")

                    if (
                        txt in ["F-HD", "HD", "SD", "Download"]
                        and href
                        and "http" in href
                    ):
                        # Filtra links que não sejam propaganda
                        if "drive" in href or "google" in href or "blogger" in href:
                            key = txt if txt != "Download" else "SD"
                            links[key] = href
                except:
                    continue

        except Exception as e:
            print(f"   ❌ Erro Selenium Drive: {e}")

        return links
