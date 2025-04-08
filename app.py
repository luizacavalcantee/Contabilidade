import streamlit as st
import pandas as pd
from backend.app.services.process_excel import GestaoFinanceira
import os

# Configuração da página
st.set_page_config(page_title="Análise Financeira", layout="wide")

# Título do app
st.title("📊 Análise Financeira")

# Upload do arquivo
uploaded_file = st.file_uploader("Carregue sua planilha Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Salva temporariamente o arquivo para processamento
        temp_file = "temp_planilha.xlsx"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Processa o arquivo
        gestao = GestaoFinanceira(temp_file)
        
        # Abas para diferentes visualizações
        tab1, tab2, tab3 = st.tabs(["Receita", "Despesas", "Resultado"])
        
        with tab1:
            st.header("Receita Bruta Mensal")
            receita = gestao.calcular_receita_bruta()
            st.bar_chart(receita.set_index('Mes_Ano')['Entrada'])
            
            # Mostra os dados em tabela
            st.dataframe(receita.style.format({'Entrada': 'R${:,.2f}'}))
        
        with tab2:
            st.header("Despesas por Categoria")
            despesas = gestao.calcular_despesas()
            
            # Gráfico de linhas para evolução temporal
            pivot_despesas = despesas.pivot(index='Mes_Ano', columns='Categoria', values='Saida').fillna(0)
            st.line_chart(pivot_despesas)
            
            # Tabela detalhada
            st.dataframe(despesas.style.format({'Saida': 'R${:,.2f}'}))
        
        with tab3:
            st.header("Resultado Financeiro")
            resultado = gestao.calcular_resultado_financeiro()
            
            # Gráfico de lucro/prejuízo
            st.bar_chart(resultado.set_index('Mes_Ano')['Lucro/Prejuízo'])
            
            # Métricas resumidas
            col1, col2, col3 = st.columns(3)
            total_receita = resultado['Entrada'].sum()
            total_despesas = resultado['Saida'].sum()
            lucro_total = total_receita - total_despesas
            
            col1.metric("Receita Total", f"R${total_receita:,.2f}")
            col2.metric("Despesas Total", f"R${total_despesas:,.2f}")
            col3.metric("Resultado Final", f"R${lucro_total:,.2f}", 
                        delta_color="inverse" if lucro_total < 0 else "normal")
            
        # Remove o arquivo temporário
        os.remove(temp_file)
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")