import re
import time
import yaml
import os
from datetime import datetime, timedelta
import requests
from selenium import webdriver
from selenium.webdriver.edge.options import Options

class RoboDiario:
    def __init__(self, config_path):
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Arquivo de configuração '{config_path}' não encontrado.")

        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

        self.nomeDiario = self.config['nomeDiario']['nome']
        self.__url = self.config['urls']['diario_url']
        self.timeout = self.config['http']['timeout']
        self.headers = self.config['http']['headers']
        self.cadernos = self.config['cadernos']
        self.min_wait_time = self.config['captcha']['min_wait_time']
        self.data_limite_config = datetime.strptime(self.config['data']['limite'], "%Y-%m-%d").date()

        self.log = self.config['logs']['log_file']
        self.erro = self.config['logs']['error_file']
        self.etapas = self.config.get('etapas', [])

    def executar_etapas(self):
        for etapa in self.etapas:
            descricao = etapa.get("descricao", "Etapa sem descrição")
            metodo = etapa.get("metodo")
            parametros = etapa.get("parametros", {})

            if not metodo:
                print(f"Etapa '{descricao}' ignorada: método não definido.")
                continue

            print(f"Iniciando etapa: {descricao}")
            metodo_ref = getattr(self, metodo, None)
            if callable(metodo_ref):
                metodo_ref(**parametros)
            else:
                print(f"Método '{metodo}' não encontrado para a etapa '{descricao}'.")

    def download_atualizacao_diaria(self):
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Edge(options=options)

        atual = datetime.now().date()
        for cod in self.cadernos:
            data = self.data_inicial(f"{self.nomeDiario}_{self.cadernos[cod]}")
            while atual >= data:
                data_str = data.strftime("%Y_%m_%d")
                nome = f"{self.nomeDiario}_{self.cadernos[cod]}_{data_str}.pdf"
                data_url = data.strftime("%d/%m/%Y")
                if self.verifica_pdf(nome):
                    url = self._get_diario(driver, data_url, cod)
                    if url:
                        self._salva_pdf(nome, url)

                data = data + timedelta(days=1)

        driver.quit()

    def verifica_pdf(self, nome):
        print(nome)
        if os.path.exists(f'./dados/{nome}'):
            return False
        else:
            return True

    def _salva_pdf(self, nome, url):
        try:

            self.salva_pdf(nome, url)
            print(f"Arquivo salvo: {nome}")
        except Exception as e:
            print(f"Erro ao salvar PDF {nome}: {e}")

    def salva_pdf(self, nome, url):
        try:
            response = requests.get(url, stream=True)
            if response.headers["Content-Type"] == "application/pdf":
                os.makedirs("./dados", exist_ok=True)
                with open(f"./dados/{nome}", "wb") as pdf_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        pdf_file.write(chunk)
                print(f"PDF salvo com sucesso: {nome}")
            else:
                print("Conteúdo não é um PDF.")
        except Exception as e:
            print(f"Erro ao baixar diretamente: {e}")

    def _get_diario(self, driver, data_url, cod):
        try:
            url = self.gerar_url(data=data_url, cad=cod)
            driver.get(url)

            if "Nenhuma publicação encontrada" not in driver.page_source:
                if self.verifica(driver.page_source):
                    return url
            else:
                print(f"Sem publicações para {data_url} no caderno {cod}.")
                return None
        except Exception as e:
            print(f"Erro ao obter URL para {data_url} no caderno {cod}: {e}")
            return None


    def verifica(self, html):
        texto = re.search("There is no row at position 0", html)
        return not bool(texto)

    def data_inicial(self, filtro, tipo_arquivo="*.pdf"):
        pasta_base = "./dados"
        ultima_data = None

        for root, dirs, files in os.walk(pasta_base):
            for file in files:
                if file.endswith(tipo_arquivo) and filtro in file:
                    try:
                        partes = file.split("_")
                        data_str = "_".join(partes[-3:]).replace(".pdf", "")
                        data = datetime.strptime(data_str, "%Y_%m_%d").date()

                        if ultima_data is None or data > ultima_data:
                            ultima_data = data
                    except (ValueError, IndexError):
                        pass
        return ultima_data if ultima_data else self.data_limite()

    def gerar_url(self, data, cad):
        return self.__url.format(data=data, cad=cad)

    def data_limite(self):
        return self.data_limite_config


if __name__ == '__main__':
    config = 'configs/config_rj.yml'
    robo = RoboDiario(config)
    robo.executar_etapas()
