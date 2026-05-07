# Projeto Arch - Extração e renomeação de arquivos (PDF)

# Bibliotecas usadas no projeto
import os # Para poder conversar com o SO
import json # Precisa dela para a geração dos arquivos JSON que serão o log do projeto
import re # Vem de Regex, é especialista em padões, não procura palavras em si. É muito importante para capturar datas e números
from pypdf import PdfReader # Para trabalhar com os PDF's, descobri ao longo de testes que ela n é boa com tabelas
from datetime import datetime # O datetime é necessário para situações aonde preciso da data e hora
from dotenv import load_dotenv # Para carregar o arquivo .env, com ele eu consigo trancar tudo e deixar o repositório público :D

# --------------------------------------------------------------------------------------------------------------------
# ORGANIZANDO AS VARIÁVEIS GLOBAIS
# --------------------------------------------------------------------------------------------------------------------
# Carrega as variáveis do arquivo .env
load_dotenv()

# Criando as variáveis para as pastas, deixo tudo no dotenv tbm
pasta_pdf = os.getenv("PASTA_PDF")
pasta_log_json = os.getenv("PASTA_LOG_JSON")

# --------------------------------------------------------------------------------------------------------------------
# ORGANIZANDO AS FUNÇÕES PRINCIPAIS DO PROJETO
# --------------------------------------------------------------------------------------------------------------------

# Função responsável por extrair todo o texto do PDF
def extrair_texto_do_pdf(caminho_arquivo):
    
    try:
        reader = PdfReader(caminho_arquivo)
        texto_completo = ""
        
        for pagina in reader.pages:
            texto_completo = texto_completo + pagina.extract_text()
            
        return texto_completo
    
    except Exception as e:
        
        print(f"❌ Erro ao ler o arquivo {caminho_arquivo}: {e}")
        
        return None
    
# -------------------------------
# *******************************
# -------------------------------

# Função responsável por realizar a extração das informações no modelo do PDF
def extracao_pdf(texto_pdf):
    
    print("\n🤺 Arch iniciando o processo de extração")
    dados = {}
    
    # -------------------------------------------------------------------------
    # CAPTURANDO E VALIDANDO A DATA DA NOTA (Filtro de Maio/2026), isso foi preciso pq as informações de medição e região
    # só foram adicionadas depois desse mês em específico
    # -------------------------------------------------------------------------
    padrao_data = r"Data da emissão da NFS-e\s*(\d{2}/\d{2}/\d{4})"
    busca_data = re.search(padrao_data, texto_pdf[:400])
    
    if busca_data:
        data_brasileira = busca_data.group(1)
        try:
            data_python = datetime.strptime(data_brasileira, "%d/%m/%Y")
            
            # criando uma data de "corte" para 1° de Maio de 2026
            data_corte = datetime.strptime("01/05/2026", "%d/%m/%Y")
            
            # Se a data do PDF for menor (anterior) à data de corte, a extração é abortada
            if data_python < data_corte:
                print(f"⏭️  Nota ignorada - a data {data_brasileira} é anterior ao novo padrão (05/2026)")
                return None # Retornamos 'None' para avisar a main que esse PDF não deve ser processado
            
            dados["data_emissao"] = data_python.strftime("%Y-%m-%d")
            print(f"🟢  Data válida encontrada: {data_brasileira}")
            
        except Exception as e:
            print(f"⚠️  Erro ao formatar a data: {e}")
            dados["data_emissao"] = data_brasileira
    else:
        print("⚠️  Data de Emissão não encontrada - pulando arquivo por segurança")
        return None # Sem data, é mais seguro não renomear para evitar estragos
    
    # -------------------------------------------------------------------------
    # 1 - CAPTURANDO O NÚMERO DA NOTA FISCAL (Com filtro de tamanho)
    # -------------------------------------------------------------------------
    # Série da DPS   -> âncora fixa antes dos blocos de valores
    # \s+            -> Pula as quebras de linha (o + garante que tem pelo menos um espaço/linha)
    # \d{40,55}      -> Ignora a Chave de Acesso (um número entre 40 e 55 dígitos)
    # \s+            -> Pula a quebra de linha de novo
    # (\d+)          -> Captura o número da nota, que vem logo abaixo da chave de acesso, só captura por causa dos parenteses
    
    padrao_nota = r"Série da DPS\s+\d{40,55}\s+(\d+)"
    busca_nota = re.search(padrao_nota, texto_pdf[:400], re.IGNORECASE) # Usei o ignore case pra deixar ele blindado contra
                                                                        # qualquer erro de digitação do usuário
    
    if busca_nota:
        dados["numero_nota"] = busca_nota.group(1)
        print(f"🟢  Número da Nota encontrado: {dados['numero_nota']}")
        
        dados["numero_nota"] = "000000000" + dados['numero_nota'] # Por padrão os nomes tem esse zero, então apenas usei
                                                                  # a mesma quantidade para fazer uma união
    else:
        dados["numero_nota"] = None
        print("⚠️  Número da Nota não encontrado")
        
    # -------------------------------------------------------------------------
    # 2 - CAPTURANDO A REGIÃO DO CONTRATO
    # -------------------------------------------------------------------------

    # O pypdf pode quebrar linhas tanto no meio do número do pedido 
    # quanto no nome da região, o Regex foi ajustado para ignorar essas quebras (experiência própria)

    # (?:\d\s*){8,11} -> ÂNCORA INICIAL: O '\d\s*' procura um número permitindo que tenha espaço ou quebra de linha logo após ele 
    #                    O '{8,11}' repete isso de 8 a 11 vezes, lê o pedido perfeitamente mesmo se estiver quebrado.
    
    # -\s*            -> LIGAÇÃO: Captura o primeiro hífen ignorando espaços ao redor
    # ([\s\S]+?)      -> O ALVO: O '[\s\S]' é o coringa supremo que captura qualquer coisa, inclusive quebras de linha
    #                    O '+?' garante a "captura preguiçosa", parando só quando ele chega na próxima regra
    
    # \s*-\s*Projeto  -> ÂNCORA FINAL: Para a captura no hífen antes da palavra "Projeto"
    
    # foquei na estrutura: um número de 8 a 11 dígitos (mesmo que quebrado em várias linhas), 
    # um hífen, a região (podendo ter quebra de linha), um hífen, e a palavra Projeto
    padrao_regiao = r"(?:\d\s*){8,11}-\s*([\s\S]+?)\s*-\s*Projeto"
    busca_regiao = re.search(padrao_regiao, texto_pdf[1175:2400], re.IGNORECASE)
    
    if busca_regiao:
        # o raplace é para que caso alguma região venha com quebra de linha ou espaço, ela será limpa para ser usada sem erro
        regiao_limpa = busca_regiao.group(1).replace("\n", " ").strip()
        dados["regiao"] = regiao_limpa
        print(f"🟢  Região Identificada: {dados['regiao']}")
    else:
        dados["regiao"] = "Regiao_Nao_Encontrada"
        print("⚠️   Região não encontrada")
        
    # -------------------------------------------------------------------------
    # 3 - CAPTURANDO A MEDIÇÃO
    # -------------------------------------------------------------------------
    # \"?        -> Procura uma aspa no começo, o '?' significa que ela é opcional (evita falhas se o pypdf acabar não lendo essa aspa)
    # Medicao N  -> Procura exatamente essa palavra
    # [º°]       -> o símbolo pode ser o ordinal (º) ou o de grau (°)
    # :\s*       -> Procura os dois pontos seguidos de qualquer quantidade de espaços em branco
    # (\d+)      -> captura apenas números (um ou mais), só aceita dígitos, ele vai parar assim que esbarrar numa string/vazio
    
    padrao_medicao = r"\"?Medicao\s+N[º°]?\s*:?\s*(\d+)"
    busca_medicao = re.search(padrao_medicao, texto_pdf[1175:2400], re.IGNORECASE) # Usa o mesmo corte que já pega a descrição
    
    if busca_medicao:
        # Não é preciso o replace("\n") ou strip() aqui porque (\d+) garante que só teremos números puros no resultado
        dados["medicao"] = busca_medicao.group(1)
        print(f"🟢  N° da Medição Identificada: {dados['medicao']}")
    else:
        dados["medicao"] = "Medicao_Nao_Encontrada"
        print("⚠️  N° da Medição não encontrada")
        
    return dados

# -------------------------------
# *******************************
# -------------------------------

# Função responsável por pegar a hora atual do sistema, vai ajudar nas exibições, pega somente as horas e os minutos
def get_hora_atual() -> str:
    return datetime.now().strftime("%H:%M")

# -------------------------------
# *******************************
# -------------------------------

# Função responsável por pegar a hora atual do sistema, vai ajudar nas exibições, pega somente as horas e os minutos
def get_dia_atual() -> str:
    return datetime.now().strftime("%d/%m/%Y")

# --------------------------------------------------------------------------------------------------------------------
# A FUNÇÃO MAIN DO PROJETO - Responsável pelo gerênciamento das demais e controle do fluxo de execução
# --------------------------------------------------------------------------------------------------------------------

def main():
    
    print(f"\n\n💽 Arch iniciando o processo de coleta - {get_hora_atual()}")
    
    # começando com uma verificação simples de pasta e arquivos antes de começar, iniciando pelo mais recente na pasta
    if not os.path.exists(pasta_pdf):
        print(f"🗺️  Pasta de PDF não encontrada: {pasta_pdf}")
        return 

    # Pegando todos os arquivos .pdf da pasta
    arquivos = [f for f in os.listdir(pasta_pdf) if f.endswith('.pdf')]
    
    if not arquivos:
        print("🔕 Nenhum arquivo PDF encontrado para processar")
        return

    # Essa lista vai começar vazia e vai receber o dicionário de cada PDF lido
    dados_totais = []
    
    for nome_arquivo in arquivos:
        caminho_antigo = os.path.join(pasta_pdf, nome_arquivo)
        
        # Extração, para funcionar eu preciso enviar o caminho de cada arquivo e não um diretório todo
        texto = extrair_texto_do_pdf(caminho_antigo)
        
        if texto:
            
            # chamando a função para o processamento dos dados
            infos = extracao_pdf(texto)
            
            # Se infos for None, significa que a extração abortou lá na verificação da data, ou seja, ela inteira é None
            # se eu usasse infos["data_emissao"] ela daria erro pq a gaveta não existe, pq o return altera a variável em si
            if infos is None:
                continue # O comando 'continue' interrompe a volta atual do loop e pula para o próximo arquivo da pasta
            
            infos["arquivo"] = nome_arquivo
            
            # Definição do novo nome com base na solicitação
            novo_nome = f"nfe_{infos['numero_nota']}_-_{infos['regiao']}_-_{infos['medicao']}°_MEDIÇÃO.pdf"
            caminho_novo = os.path.join(pasta_pdf, novo_nome)
            
            # Renomeação Física do arquivo
            try:
                # verificando se o nome novo já existe para não sobrescrever sem querer
                if not os.path.exists(caminho_novo):
                    os.rename(caminho_antigo, caminho_novo)
                    infos["nome_antigo_do_arquivo"] = nome_arquivo
                    infos["nome_novo_do_arquivo"] = novo_nome
                    print(f"✅ Renomeado: {nome_arquivo} -> {novo_nome}")
                else:
                    print(f"👥  Arquivo {novo_nome} já existe - Pulando renomeação")
            except Exception as e:
                print(f"❌ Erro ao renomear {nome_arquivo}: {e}")
                
            dados_totais.append(infos)

    # Geração do Log JSON (Unificado)
    if dados_totais:
        
        nome_log = f"LOG_{datetime.now().strftime('%d-%m-%Y')}_HORA_{datetime.now().strftime("%H-%M")}.json"
        caminho_log = os.path.join(pasta_log_json, nome_log)
        
        with open(caminho_log, 'w', encoding='utf-8') as f:
            json.dump(dados_totais, f, indent=4, ensure_ascii=False)
            
        print(f"\n📄 Log gerado com sucesso: {nome_log}\n")

# O 'if __name__' garante que o robô só comece a rodar se este arquivo for executado diretamente
if __name__ == "__main__":
    main()