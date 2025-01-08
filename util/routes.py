import os
import re


def definir_caminho(nome_arquivo):
    """
    Define o caminho de armazenamento com base no nome do arquivo usando regex.
    """
    # Regex para capturar os campos no nome do arquivo
    match = re.match(r'^(DJ(\w{2}))_(.*)?_(\d{4})_(\d{2})_(\d{2})\.(pdf)$', nome_arquivo)
    if not match:
        raise ValueError(f"O nome do arquivo '{nome_arquivo}' não segue o padrão esperado.")

    diario, estado, subcategoria, ano, mes, dia, tipo = match.groups()

    caminho_final = f'./dados/{estado}/{diario}/{tipo}/{ano}/{mes}'
    os.makedirs(caminho_final, exist_ok=True)
    return caminho_final


def verifica_caminho(nome_arquivo):
    """
    Verifica se o arquivo já existe no caminho gerado.
    """
    try:
        # Define o caminho completo usando regex
        caminho_base = definir_caminho(nome_arquivo)
        caminho_completo = os.path.join(caminho_base, nome_arquivo)

        # Verifica se o arquivo já existe
        return not os.path.exists(caminho_completo)
    except ValueError as e:
        print(f"Erro ao verificar caminho: {e}")
        return False

