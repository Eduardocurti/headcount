"""
Sincroniza a base de headcount a partir de um arquivo compartilhado no OneDrive/SharePoint
("Qualquer pessoa com o link pode visualizar") para data/dados.xlsx neste repositório.

Como é chamado:
- Localmente:  ONEDRIVE_URL="https://...&download=1" python sync_onedrive.py
- No GitHub Actions: a variável de ambiente ONEDRIVE_URL vem do Secret configurado no repositório
  (Settings > Secrets and variables > Actions > New repository secret > nome "ONEDRIVE_URL").

O link precisa terminar com "&download=1" (ou "?download=1" se ainda não tiver nenhum "?"),
para virar um link de download direto do arquivo em vez de abrir o visualizador do Office Online.
"""

import os
import sys

import requests

ONEDRIVE_URL = os.environ.get("ONEDRIVE_URL", "").strip()
OUTPUT_PATH = "data/dados.xlsx"
TIMEOUT_SECONDS = 60


def main():
    if not ONEDRIVE_URL:
        print("ERRO: variável de ambiente ONEDRIVE_URL não configurada.")
        sys.exit(1)

    print("Baixando base do OneDrive...")
    try:
        resp = requests.get(ONEDRIVE_URL, timeout=TIMEOUT_SECONDS, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"ERRO ao baixar o arquivo: {exc}")
        sys.exit(1)

    content = resp.content

    # Um arquivo .xlsx é um ZIP e sempre começa com a assinatura "PK".
    # Se vier outra coisa (ex: uma página HTML de login/erro), o link provavelmente
    # expirou ou a permissão de compartilhamento mudou.
    if content[:2] != b"PK":
        print("ERRO: o conteúdo baixado não parece ser um .xlsx válido (sem assinatura ZIP/PK).")
        print("Verifique se o link do OneDrive ainda está com a permissão")
        print('"Qualquer pessoa com o link" e termina com "&download=1".')
        sys.exit(1)

    if len(content) < 1024:
        print(f"AVISO: arquivo baixado é muito pequeno ({len(content)} bytes) — confirme se está correto.")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        f.write(content)

    print(f"OK: base salva em {OUTPUT_PATH} ({len(content):,} bytes).")


if __name__ == "__main__":
    main()
