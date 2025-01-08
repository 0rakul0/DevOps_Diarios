# Projeto: RoboDiario - Download Automático de Diários Oficiais

## Descrição
O **RoboDiario** é uma solução automatizada para realizar o download dos Diários Oficiais de Justiça do Estado do Rio de Janeiro (DJRJ). Este script utiliza o Selenium para interagir com o site do Tribunal de Justiça do RJ, acessando e baixando os arquivos em formato PDF, conforme os parâmetros configurados no arquivo de configuração YAML.

---

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
├── configs
│   └── config_rj.yml         # Arquivo de configuração YAML
├── dados                     # Diretório onde os PDFs baixados são salvos
├── logs                      # Diretório para armazenar os arquivos de log
├── RoboDiario.py             # Script principal do robô
├── engine.py                 # Classe principal para automação e lógica
├── util
│   └── routes.py             # Funções auxiliares para manipulação de caminhos
└── README.md                 # Documento de orientação do projeto
```

---

## Requisitos

Certifique-se de que você tem os seguintes componentes instalados:

1. **Python** (versão 3.8 ou superior)
2. **Bibliotecas Python**:
   - `selenium`
   - `pyyaml`
   - `requests`
3. **Driver Selenium**:
   - Microsoft Edge WebDriver (compatível com a versão do seu navegador Edge)

---

## Funcionalidades Principais

### 1. **Download Organizado de PDFs**
   - Os diários oficiais são baixados automaticamente para os diretórios correspondentes, organizados por estado, tipo de diário, ano e mês.
   - O nome dos arquivos segue o padrão: `DJ<ESTADO>_<CADERNO>_<YYYY_MM_DD>.pdf`.

### 2. **Controle de Atualização**
   - O robô mantém um histórico das datas já processadas e baixa apenas os arquivos que ainda não foram salvos.

### 3. **Configuração Flexível**
   - Os parâmetros de URLs, cadernos, tempos de espera, e logs são completamente personalizáveis via um arquivo de configuração YAML.

### 4. **Sistema de Logs**
   - Logs detalhados para registrar erros e operações realizadas durante a execução.

---

## Melhorias Recentes

1. **Validação do Nome dos Arquivos**  
   - O script agora valida o nome dos arquivos PDF com um regex robusto antes de salvá-los.  
   - Caminhos são gerados automaticamente com base no estado, tipo do diário e data.

2. **Organização por Subdiretórios**  
   - PDFs são salvos em subdiretórios estruturados no formato: `./dados/<ESTADO>/<TIPO_DIARIO>/<ANO>/<MES>/`.

3. **Funções Auxiliares Modulares**  
   - A lógica para definir caminhos e verificar se arquivos já existem foi movida para o módulo `routes.py` em `util`.

4. **Melhor Tratamento de Exceções**  
   - Logs mais detalhados para rastrear falhas em downloads ou na geração de URLs.

---

## Instalação e Configuração

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

### 2. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 3. Configuração do Arquivo YAML
Edite o arquivo `configs/config_rj.yml` com as informações necessárias. Segue um exemplo do formato do arquivo de configuração:

```yaml
nomeDiario:
  nome: "DJRJ"

urls:
  diario_url: "https://www3.tjrj.jus.br/consultadje/pdf.aspx?dtPub={data}&caderno={cad}&pagina=-1"

http:
  timeout: 10
  headers:
    User-Agent: "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0"
    Accept: "application/json, text/javascript, */*; q=0.01"
    X-Requested-With: "XMLHttpRequest"

logs:
  log_file: "log_robo_rj.txt"
  error_file: "erro_robo_rj.txt"

captcha:
  min_wait_time: 5

cadernos:
  A: "Administrativo"
  S: "Judicial_-_2_Instancia"
  C: "Judicial_-_1_Instancia_Capital"
  I: "Judicial_-_1_Instancia_Interior"
  E: "Edital"

data:
  limite: "2025-01-02"

etapas:
  - descricao: "Baixar os diários oficiais por caderno e data"
    metodo: "download_atualizacao_diaria"
    parametros: {}

  - descricao: "Obter a URL do diário oficial"
    metodo: "_get_diario"
    parametros:
      driver: "Driver Selenium configurado"
      data_url: "Data formatada no padrão dd/MM/yyyy"
      cod: "Código do caderno"

  - descricao: "Salvar o PDF da URL válida"
    metodo: "_salva_pdf"
    parametros:
      nome: "Nome do arquivo PDF no formato NomeDiario_Caderno_Data.pdf"
      url: "URL do diário oficial válido"
```

---

## Como Executar

### 1. Certifique-se de que o driver do Selenium está configurado corretamente no **PATH** do sistema.

- **Microsoft Edge**: Eu estou usando o nativo do windows, mas fique a vontade para escolher outro 

### 2. Execute o Script Principal
```bash
python RoboDiario.py
```

---

## Principais Funcionalidades

### 1. **Download Automático de PDFs**
   - Baixa os diários oficiais para cada caderno especificado no arquivo de configuração.
   - O nome dos arquivos é gerado no formato: `DJRJ_<CADERNO>_<YYYY_MM_DD>.pdf`.

### 2. **Continuidade de Downloads**
   - Identifica automaticamente a última data já baixada e continua o download a partir dessa data.

---

## Personalização

### Adicionar Novos Cadernos
Para incluir novos cadernos no arquivo de configuração, basta adicioná-los na seção `cadernos` do YAML:
```yaml
cadernos:
  F: "Novo_Caderno"
```

### Alterar Data Limite
A data limite inicial pode ser alterada na seção `data`:
```yaml
data:
  limite: "YYYY-MM-DD"
```

### Alterar Parâmetros de Timeout
Para ajustar o tempo de espera entre as requisições HTTP, edite a seção `http`:
```yaml
http:
  timeout: 20
```
---

## Estrutura do Código

### Classe: `RoboDiario`
Responsável por toda a lógica do robô.

- **Métodos Principais:**
- **`__init__`**: Inicializa o robô e carrega a configuração YAML.
- **`executar_etapas`**: Executa as etapas definidas no arquivo de configuração.
- **`download_atualizacao_diaria`**: Realiza o download dos diários conforme as datas e cadernos especificados.
- **`_get_diario`**: Interage com o site, verifica se o conteúdo é válido e salva os PDFs.
- **`verifica`**: Verifica se o conteúdo é válido (sem mensagens de erro).
- **`data_inicial`**: Identifica a última data de download realizada.
- **`gerar_url`**: Gera a URL para o download com base na data e caderno.
- **`data_limite`**: Define a data inicial para o processo.

---

## Logs
**ainda falta implementar**

- **Arquivo de Log Principal**:
  - Nome: Definido em `logs.log_file` no YAML.
  - Exemplo: `log_robo_rj.txt`
  - Descrição: Contém logs detalhados sobre o progresso das etapas.

- **Arquivo de Erros**:
  - Nome: Definido em `logs.error_file` no YAML.
  - Exemplo: `erro_robo_rj.txt`
  - Descrição: Registra erros encontrados durante a execução do robô.

**Como Habilitar Logs**: Certifique-se de que a configuração `logs` no arquivo YAML esteja corretamente definida com os caminhos dos arquivos de log.

---

## Contribuição

Se você deseja contribuir para este projeto, siga as etapas abaixo:

1. **Fork o Repositório**:
   - Crie um fork do repositório para sua conta.

2. **Crie uma Branch para sua Funcionalidade**:
   ```bash
   git checkout -b minha-funcionalidade
   ```

3. **Submeta suas Alterações**:
   ```bash
   git commit -m 'Adicionando minha funcionalidade'
   ```

4. **Envie a Branch**:
   ```bash
   git push origin minha-funcionalidade
   ```

5. **Abra um Pull Request**:
   - Crie um Pull Request no repositório original para revisar e fundir suas alterações.

---

## Licença

Este projeto é licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## Contato

Para dúvidas ou suporte, entre em contato:
- **E-mail:** jefferson.ti@hotmail.com.br
- **GitHub:** [LINK_DO_REPOSITORIO](https://github.com/0rakul0/DevOps_Diarios)

## Contribuições

Sinta-se à vontade para abrir issues ou enviar pull requests para melhorar o projeto. 
Para feedback ou dúvidas, entre em contato: **<seu-email-aqui>**.

