import os
import sys
import zipfile
import re


def limpar_tela():
    os.system("clear" if os.name == "posix" else "cls")


def formatar_tamanho(t):
    if t == 0:
        return "??"
    for u in ["B", "KB", "MB", "GB"]:
        if t < 1024.0:
            return f"{t:.2f} {u}"
        t /= 1024.0
    return f"{t:.2f} TB"


def sanitizar_nome(nome):
    """Remove caracteres inválidos para nomes de pasta/arquivo"""
    return re.sub(r'[<>:"/\\|?*]', "", nome).strip()


def compactar_pasta(caminho_pasta):
    try:
        nome_zip = f"{caminho_pasta}.zip"
        print(f"\n📦 Compactando para: {os.path.basename(nome_zip)}...")

        with zipfile.ZipFile(nome_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            count = 0
            for root, dirs, files in os.walk(caminho_pasta):
                for file in files:
                    if file.endswith(".mp4"):
                        caminho_completo = os.path.join(root, file)
                        zipf.write(caminho_completo, arcname=file)
                        count += 1
                        sys.stdout.write(f"\r   -> Add: {file}")
                        sys.stdout.flush()

        print(f"\n✅ ZIP criado com {count} arquivos!")
        return True
    except Exception as e:
        print(f"\n❌ Erro ao zipar: {e}")
        return False


# talvez ninguem use isso nunca... mas ta aqui se precisar (eu utilizo bastante)
