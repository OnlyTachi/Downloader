import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

_driver_instance = None


def get_driver():
    global _driver_instance
    if _driver_instance:
        return _driver_instance

    print("🚀 Iniciando Motor (Selenium Modo Furtivo)...")
    options = Options()

    # Configurações básicas
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")

    # Configurações Anti-Detecção
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Tenta encontrar binário no Linux (pois nem sempre está no PATH, entao modifiquei para procurar em locais comuns)
    if sys.platform.startswith("linux"):
        caminhos_linux = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
            "/snap/bin/google-chrome",
        ]
        for c in caminhos_linux:
            if os.path.exists(c):
                options.binary_location = c
                break

    try:
        service = Service(ChromeDriverManager().install())
        _driver_instance = webdriver.Chrome(service=service, options=options)

        # Script evasivo para remover propriedade 'webdriver' do navigator
        _driver_instance.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
            },
        )
        return _driver_instance
    except Exception as e:
        print(f"❌ Erro ao iniciar driver: {e}")
        return None


def kill_driver():
    global _driver_instance
    if _driver_instance:
        try:
            _driver_instance.quit()
        except:
            pass
        _driver_instance = None
