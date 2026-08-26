import streamlit as st
import pandas as pd
from datetime import datetime

st.title("Painel de Versões - CEBI")

try:
    # Lê o CSV gerado pelo seu script de varredura
    df = pd.read_csv("relatorio_versoes_limpo.csv")
    
    # --- ALTERAÇÃO 1: Ordenação ---
    # Ordena a tabela pela coluna "Módulo" em ordem alfabética (A-Z)
    df = df.sort_values(by="Módulo")
    
    # --- ALTERAÇÃO 2: Filtro de Clientes ---
    # Pega todos os nomes únicos de clientes que estão no CSV e adiciona a opção "Todos"
    lista_clientes = ["Todos"] + list(df["Cliente"].unique())

    # Faz a mesma coisa com os módulos
    lista_modulos = ["Todos"] + list(df["Módulo"].unique())
    
    # Cria a caixa de seleção na tela
    cliente_selecionado = st.selectbox("Selecione o Cliente para visualizar:", lista_clientes)
    modulo_selecionado = st.selectbox("Selecione o Módulo para visualizar:", lista_modulos)

    # Aplica a regra de filtro dependendo do que o usuário escolheu
    if cliente_selecionado != "Todos":
        # Filtra o dataframe para mostrar apenas o cliente selecionado
        df_exibicao = df[df["Cliente"] == cliente_selecionado]
    else:
        df_exibicao = df

    # Faz o filtro de módulo também
    if modulo_selecionado != "Todos":
        # Filtra o dataframe para mostrar apenas o módulo selecionado
        df_exibicao = df[df["Módulo"] == modulo_selecionado]

    # --- NOVA REGRA DE CORES ---
    def pintar_data_antiga(valor):
        # Se não tiver data, deixa transparente
        if valor == "Data indisponível" or pd.isna(valor):
            return ""
        
        try:
            # Converte o texto (dd/mm/yyyy) de volta para uma data matemática
            data_campo = datetime.strptime(str(valor), "%d/%m/%Y")
            hoje = datetime.now()
            
            # Calcula quantos dias se passaram
            diferenca = (hoje - data_campo).days
            
            # Se for maior que 30 dias, retorna o CSS para pintar de vermelho
            if diferenca > 30:
                return "background-color: #ffcccc; color: #a30000;" # Fundo vermelho claro, texto vermelho escuro
            if diferenca > 15 and diferenca <= 30:
                return "background-color: #fff2cc; color: #a36f00;" # Fundo amarelo claro, texto marrom
        except Exception:
            pass
            
        return "" # Se deu qualquer erro na leitura, não pinta nada

    # --- APLICAÇÃO DO ESTILO ---
    # Aplica a nossa regra visual apenas na coluna 'Última Atualização'
    try:
        # Para versões mais recentes do Pandas (que rodam no Streamlit Cloud)
        df_estilizado = df_exibicao.style.map(pintar_data_antiga, subset=["Última Atualização"])
    except AttributeError:
        # Para versões mais antigas do Pandas (caso você rode no seu PC)
        df_estilizado = df_exibicao.style.applymap(pintar_data_antiga, subset=["Última Atualização"])

    # --- EXIBIÇÃO ---
    # Agora passamos o dataframe ESTILIZADO para o Streamlit desenhar!
    st.dataframe(df_estilizado, use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.error("O arquivo 'relatorio_versoes_limpo.csv' não foi encontrado na pasta.")
