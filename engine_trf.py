import os
import time
import yaml
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from util.routes import definir_caminho, verifica_caminho


class PJEConsulta:
    def __init__(self, config_path):
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Arquivo de configuração '{config_path}' não encontrado.")

        with open(config_path, "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

        # Inicializando parâmetros
        self.nomeDiario = self.config['nomeTRT']['nome']
        self.__url = self.config['urls']['consulta_url']
        self.timeout = self.config['http']['timeout']
        self.headers = self.config['http']['headers']
        self.min_wait_time = self.config['captcha']['min_wait_time']
        self.log_file = self.config['logs']['log_file']
        self.error_file = self.config['logs']['error_file']
        self.etapas = self.config.get('etapas', [])

        # Criar pastas para logs, se necessário
        self.log_path = os.path.dirname(self.log_file)
        os.makedirs(self.log_path, exist_ok=True)

    def log(self, message):
        """Registra mensagens em log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as log:
            log.write(f"[{timestamp}] {message}\n")
        print(message)

    def log_error(self, error_message):
        """Registra mensagens de erro em um arquivo de log específico."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.error_file, "a") as log_error:
            log_error.write(f"[{timestamp}] {error_message}\n")
        print(f"ERRO: {error_message}")

    def executar_etapas(self):
        """Executa todas as etapas definidas no arquivo de configuração."""
        for etapa in self.etapas:
            descricao = etapa.get("descricao", "Etapa sem descrição")
            metodo = etapa.get("metodo")
            parametros = etapa.get("parametros", {})

            if not metodo:
                self.log(f"Etapa '{descricao}' ignorada: método não definido.")
                continue

            self.log(f"Iniciando etapa: {descricao}")
            metodo_ref = getattr(self, metodo, None)
            if callable(metodo_ref):
                try:
                    metodo_ref(**parametros)
                    self.log(f"Etapa '{descricao}' concluída com sucesso.")
                except Exception as e:
                    self.log_error(f"Erro na etapa '{descricao}': {e}")
            else:
                self.log_error(f"Método '{metodo}' não encontrado para a etapa '{descricao}'.")

    def configurar_driver(self):
        """Configura o WebDriver com os headers necessários."""
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Edge(options=options)
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": self.headers})
        return driver

    def consulta(self):
        """Executa a consulta no site definido."""
        driver = None
        try:
            driver = self.configurar_driver()
            driver.get(self.__url)

            cpf_or_cnpj, tipo = self.get_cpf_or_cnpj()

            # Identifica se o tipo é CPF ou CNPJ e preenche o formulário
            tipo_xpath = (
                '//*[@id="fPP:consultaSearchForm"]/div[6]/div[1]/label/input[1]'
                if tipo == "CPF"
                else '//*[@id="fPP:consultaSearchForm"]/div[6]/div[1]/label/input[2]'
            )
            driver.find_element(By.XPATH, tipo_xpath).click()

            # insere o cpf ou cpnj
            driver.find_element(By.XPATH, '//*[@id="fPP:dpDec:documentoParte"]').send_keys(cpf_or_cnpj)

            # Clica no botão de pesquisa
            driver.find_element(By.XPATH, '//*[@id="fPP:searchProcessos"]').click()
            time.sleep(self.min_wait_time)

            # Captura os dados
            dados = driver.find_elements(By.XPATH, '//*[@id="fPP:processosGridPanel_body"]')
            for dado in dados:
                self.log(f"Dado capturado: {dado.text}")

        except NoSuchElementException as e:
            self.log_error(f"Elemento não encontrado: {e}")
        except TimeoutException as e:
            self.log_error(f"Timeout durante a consulta: {e}")
        except Exception as e:
            self.log_error(f"Erro inesperado na consulta: {e}")
        finally:
            if driver:
                driver.quit()

    def get_cpf_or_cnpj(self):
        """Retorna um CPF ou CNPJ para uso na consulta."""
        return "25358210873", "CPF"


if __name__ == "__main__":
    config = "configs/config_trf.yml"
    try:
        robo = PJEConsulta(config)
        robo.executar_etapas()
    except Exception as e:
        print(f"Erro ao iniciar o robô: {e}")
