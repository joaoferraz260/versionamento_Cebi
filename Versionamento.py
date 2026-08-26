import requests
import urllib3
import csv
import concurrent.futures
from email.utils import parsedate_to_datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

clientes = {
    "SAESA": "https://saocaetanosaesa.cebicloud.com.br",
    "Poços": "https://pocosdecaldasdmae.cebicloud.com.br",
    "SAECIL": "https://lemesaecil.cebicloud.com.br",
    "Rio Claro": "https://rioclarodaae.cebicloud.com.br",
    "Penapolis": "https://penapolisdaep.cebicloud.com.br",
    "Pirai": "https://barradopiraipref.cebicloud.com.br",
    "Cosmopolis": "https://cosmopolispref.cebicloud.com.br",
    "Descalvado": "https://descalvadopref.cebicloud.com.br",
    "Iracemápolis": "https://iracemapolispref.cebicloud.com.br",
    "Salto": "https://saltosaae.cebicloud.com.br",
    "São Carlos": "https://saocarlossaaegg.cebicloud.com.br",
    "Guaratinguetá": "https://guaratinguetasaeg.cebicloud.com.br",
    "Mogi Guaçu": "https://mogiguacusamae.cebicloud.com.br",
    "Lençois Paulista": "https://lencoispaulistasaae.cebicloud.com.br",
    "SAAE Mogi Mirim": "https://mogimirimsaae.cebicloud.com.br",
    "Engenheiro Coelho": "https://engcoelho.cebicloud.com.br",
    "SAEAN": "https://arturnogueirasae.cebicloud.com.br",
    "Mogi das Cruzes": "https://sistemas.semae.sp.gov.br",
    "Itu": "https://cis-itu.cebicloud.com.br"
}

modulos = {
    "Administração": "/administracao",
    "Analytics": "/analytics",
    "Analytics Designer": "/analytics_designer",
    "Usuários": "/usuarios",
    "Balcão": "/balcao_ssb",
    "Pessoas": "/pessoas",
    "Leitura": "/leitura",
    "Controle de Leitura": "/ssb_controle_leitura",
    "Corte": "/corte",
    "Dívida Ativa": "/divida_ativa_ssb",
    "Hidrometria": "/ssb_hidrometria",
    "Baixa": "/baixa",
    "CRC": "/crc",
    "Rois de apoio": "/rois_apoio",
    "SSB Principal": "/ssb_principal",
    "Gerenciamento de Serviços": "/gerenciamento_servicos",
    "OmniChannel": "/Omnichannel",
    "Funcionários": "/funcionarios",
    "Gestão de Documentos": "/gestao_documentos",
    "Agendamento de Atendimentos": "/agendamento_atendimentos",
    "Controle Interno": "/controle_interno",
    "EFD Reinf": "/efd_reinf",
    "Materiais": "/materiais",
    "Compras e Licitações": "/compras_legado",
    "Frota": "/frota",
    "Patrimônio": "/patrimonio",
    "Portal de Licitações": "/portal_licitacoes",
    "Concurso Público": "/concurso_publico",
    "Fornecedores": "/fornecedores",
    "Folha Diversos": "/folha_diversos",
    "Autorização de Pagamento": "/autorizacao_pagamento",
    "Treinamento e Desenvolvimento": "/treinamento_desenvolvimento"
    }

endpoint_api = "/api/AppInfo" 
# O arquivo que usaremos como "isca" para pegar a data do IIS
arquivo_estatico = "/index.html" 

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

def checar_versao(nome_cliente, url_cliente, nome_modulo, caminho_modulo):
    # Monta a base da URL (ex: https://orgao1.gov.br/financeiro)
    url_base_modulo = f"{url_cliente.rstrip('/')}/{caminho_modulo.strip('/')}"
    
    url_api = f"{url_base_modulo}/{endpoint_api.lstrip('/')}"
    url_isca = f"{url_base_modulo}/{arquivo_estatico.lstrip('/')}"
    
    try:
        # 1. Pega a versão na API
        resposta_api = requests.get(url_api, headers=headers, timeout=30, verify=False)
        resposta_api.raise_for_status() 
        dados_json = resposta_api.json()
        versao = dados_json.get("versaoApi")
        
        if versao:
            data_atualizacao = "Data indisponível"
            
            # 2. Se achou a versão, faz a requisição HEAD rápida no arquivo estático
            try:
                resposta_isca = requests.head(url_isca, headers=headers, timeout=15, verify=False)
                if resposta_isca.status_code == 200:
                    data_bruta = resposta_isca.headers.get("Last-Modified")
                    
                    if data_bruta:
                        try:
                            # Converte a data em inglês para um 'Objeto de Data' no Python
                            data_obj = parsedate_to_datetime(data_bruta)
                            # Formata para dd/mm/yyyy
                            data_atualizacao = data_obj.strftime("%d/%m/%Y")
                        except Exception:
                            # Se por acaso o IIS mandar uma data fora do padrão, mantém a original
                            data_atualizacao = data_bruta
            except Exception:
                pass # Se o index.html não existir, ignora
            
            # Retorna o dicionário completo!
            return {
                "Cliente": nome_cliente, 
                "Módulo": nome_modulo, 
                "Versão": versao,
                "Última Atualização": data_atualizacao
            }
            
    except Exception:
        pass 
    return None

# --- Resto do código continua normal ---
combinacoes = [(nc, uc, nm, cm) for nc, uc in clientes.items() for nm, cm in modulos.items()]
resultados = []

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futuros = [executor.submit(checar_versao, *comb) for comb in combinacoes]
    for futuro in concurrent.futures.as_completed(futuros):
        resultado = futuro.result()
        if resultado is not None:
            resultados.append(resultado)

# --- AQUI TAMBÉM MUDOU: Adicionamos a nova coluna para salvar o CSV ---
with open("relatorio_versoes_limpo.csv", mode="w", newline="", encoding="utf-8") as arquivo_csv:
    colunas = ["Cliente", "Módulo", "Versão", "Última Atualização"]
    escritor = csv.DictWriter(arquivo_csv, fieldnames=colunas)
    escritor.writeheader()
    escritor.writerows(resultados)
    
print("Concluído! CSV gerado.")
