# Projeto Arch  - Automação para extração e renomeação de arquivos (PDF)🤺

Um projeto de automação (RPA) desenvolvido em Python com o objetivo de otimizar processos e gestão de arquivos. O Arch atua na extração de dados estruturados de notas fiscais em PDF e realiza a renomeação em lote desses arquivos, gerando logs de rastreabilidade.

Este projeto nasceu da necessidade de aplicar conceitos práticos de programação para resolver problemas reais de tarefas repetitivas, mantendo o foco em melhorias cirúrgicas, graduais e contínuas no código.

---

## ⚙️ O que o Arch faz?

* **Leitura de PDFs:** Varre um diretório local em busca de arquivos `.pdf` e extrai seu conteúdo em texto
* **Validação de Data:** Verifica automaticamente se a NFS-e foi emitida a partir do padrão atualizado (01/05/2026). Arquivos anteriores são ignorados por segurança, considerando a falta de padronização de datas antigas
* **Extração por Padrões (Regex):** Utiliza expressões regulares (`re`), ignorando formatações instáveis ou quebras de linha do PDF, para focar na captura cirúrgica de:
  * Número da Nota Fiscal
  * Região de faturamento
  * Número da Medição
  * Número do Projeto
  * Pedido de Compra
* **Renomeação Padronizada:** Renomeia os arquivos fisicamente de forma dinâmica, seguindo o formato rigoroso: 
  `nfe_000000000123_-_SAO_PAULO_-_1°_MEDIÇÃO_-_PROJETO_12345.67_-_PEDIDO_98765.pdf`
* **Geração de Logs:** Cria automaticamente um arquivo `.json` unificado contendo o histórico de todos os dados extraídos, mapeando o nome original e o novo nome de cada arquivo modificado durante a execução

---

## 🥣 Tecnologias Utilizadas

* **[Python 3](https://www.python.org/):** Linguagem principal do projeto
* **[pypdf](https://pypi.org/project/pypdf/):** Biblioteca para manipulação e extração de texto dos arquivos PDF
* **[python-dotenv](https://pypi.org/project/python-dotenv/):** Gerenciamento de variáveis de ambiente para manter caminhos de pastas locais seguros e fora do versionamento público
* **Módulos nativos:** `os` (navegação no SO e manipulação de arquivos), `json` (geração de logs), `re` (Regex) e `datetime` (validação e formatação de datas)

---

## 🔐 Configuração das Variáveis de Ambiente (.env)

Para que a Ema funcione corretamente no ambiente local ou no servidor, é necessário criar um arquivo chamado `.env` na raiz do projeto contendo as variáveis abaixo.

> **Atenção:** Caso alguma de suas credenciais possua caracteres especiais utilizados para anotações no ecossistema Python (como o caractere `#`), é obrigatório envolver o valor em aspas duplas `" "` para garantir a interpretação correta pelo sistema

```env
# ------------------------------------------
# CAMINHO DAS PASTAS
# ------------------------------------------
PASTA_PDF=C:\Caminho\Para\Os\PDF's
PASTA_LOG_JSON=C:\Caminho\Para\A\Pasta\Log
