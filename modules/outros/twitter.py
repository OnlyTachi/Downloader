import time
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.driver import get_driver
from core.utils import resolve_redirect
from modules.base import BaseSite


class Twitter(BaseSite):
    def __init__(self):
        self.driver = get_driver()

    def pode_processar(self, url: str) -> bool:
        return "twitter.com" in url or "x.com" in url or "t.co" in url

    def get_titulo(self, url: str) -> str:
        return "Twitter_Thread_Download"

    def get_conteudo(self, url: str):
        print(f"🔎 Processando Twitter: {url}")
        try:
            links = self.get_drive_links(url)

            if not links:
                print("\n❌ AVISO: Nenhum link encontrado.")
                print("   MOTIVOS PROVÁVEIS:")
                print("   1. O link t.co aponta para um arquivo deletado/banido.")
                print("   2. O Twitter exige LOGIN para ver o conteúdo.")
                print("   3. O navegador abriu sem estar logado na sua conta.")
                return []

            results = []
            for i, link in enumerate(links):
                results.append({"numero": f"{i+1:02}", "url": link, "tipo": "video"})
            return results

        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO NO MÓDULO TWITTER: {e}")
            print("--- Detalhes do Erro (Traceback) ---")
            traceback.print_exc()
            print("------------------------------------")
            return []

    def get_links_download(self, url_conteudo: str) -> dict:
        return {"Drive": url_conteudo}

    def get_drive_links(self, url):
        print(f"   🌐 Acessando URL: {url}")
        self.driver.get(url)

        print("   ⏳ Aguardando carregamento da página (10s)...")
        time.sleep(10)

        current_url = self.driver.current_url
        if "drive.google.com" in current_url or "docs.google.com" in current_url:
            print(f"   🔀 Redirecionamento direto detectado!")
            print(f"   📂 Link Drive encontrado: {current_url}")

            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                if (
                    "viola nossos termos" in page_text
                    or "violate our terms" in page_text
                ):
                    print(
                        "\n   ❌ ⛔ AVISO: Este arquivo foi BANIDO pelo Google (Violação de Termos)."
                    )
                    print(
                        "   O download provavelmente falhará, mas o link foi capturado.\n"
                    )
            except:
                pass

            return [current_url]

        if "login" in current_url:
            print(f"   ⚠️ ALERTA: Redirecionado para tela de login! ({current_url})")
            print("   👉 Por favor, faça login no navegador aberto AGORA.")
            input(
                "   ⌨️  Pressione ENTER aqui no terminal após fazer login no navegador... "
            )

        print("   📜 Rolando página para carregar respostas...")
        for i in range(1, 6):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            print(f"      -> Scroll {i}/5...")
            time.sleep(3)

        print("   🕵️  Procurando tweets na página...")
        try:
            tweet_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, '[data-testid="tweetText"]')
                )
            )
        except Exception:
            print("   ⚠️ Não foi possível encontrar elementos de texto de tweet.")
            tweet_elements = []

        print(f"   📊 Tweets analisados: {len(tweet_elements)}")

        found_links = []
        for index, tweet in enumerate(tweet_elements):
            try:
                links = tweet.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if not href:
                        continue

                    if "t.co/" in href:
                        try:
                            final_url = resolve_redirect(href)
                        except:
                            final_url = href
                    else:
                        final_url = href

                    if (
                        "drive.google.com" in final_url
                        or "docs.google.com" in final_url
                    ):
                        print(
                            f"   ✅ Link Drive encontrado no tweet {index+1}: {final_url}"
                        )
                        found_links.append(final_url)
            except Exception as e:
                print(f"   ⚠️ Erro ao ler um tweet específico: {e}")
                continue

        return list(dict.fromkeys(found_links))
