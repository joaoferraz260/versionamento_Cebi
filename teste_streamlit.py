import streamlit as st
import pandas as pd

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

    # --- EXIBIÇÃO ---
    # Mostra a tabela filtrada e ordenada (hide_index=True tira aquela coluna de números 0, 1, 2...)
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.error("O arquivo 'relatorio_versoes_limpo.csv' não foi encontrado na pasta. Rode o script principal primeiro!")
