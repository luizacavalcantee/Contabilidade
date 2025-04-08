from pathlib import Path
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Importa o módulo de gestão financeira
from src.finance.process_excel import GestaoFinanceira

# Configuração da página
st.set_page_config(
    page_title="Análise Financeira",
    layout="wide",
    page_icon="📊"
)

# Título do app
st.title("📊 Análise Financeira")

# Upload do arquivo
uploaded_file = st.file_uploader(
    "Carregue sua planilha Excel",
    type=["xlsx", "xls"],
    help="Planilha deve conter colunas: Data, Entrada, Saida, Nome Natureza"
)

if uploaded_file is not None:
    try:
        # Salva temporariamente o arquivo
        temp_file = "temp_planilha.xlsx"
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Processa o arquivo
        gestao = GestaoFinanceira(temp_file)
        
        # Abas para diferentes visualizações
        tab1, tab2, tab3 = st.tabs(["📈 Receita", "💸 Despesas", "💰 Resultado"])
        
        with tab1:
            st.header("Receita Bruta Mensal")
            receita = gestao.calcular_receita_bruta()
            
            # Gráfico interativo
            fig = px.bar(
                receita,
                x='Mes_Ano',
                y='Entrada',
                color='Entrada',
                color_continuous_scale='Blues',
                title="Receita Mensal",
                labels={'Entrada': 'Valor (R$)', 'Mes_Ano': 'Mês/Ano'},
                text='Entrada'
            )
            fig.update_traces(
                texttemplate='R$%{text:,.2f}',
                textposition='outside',
                hovertemplate="<b>Mês:</b> %{x}<br><b>Receita:</b> R$%{y:,.2f}<extra></extra>"
            )
            fig.update_layout(
                hovermode="x unified",
                yaxis_tickprefix="R$",
                yaxis_tickformat=",.2f"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabela
            st.dataframe(
                receita.style.format({'Entrada': 'R${:,.2f}'}),
                height=300,
                column_config={
                    "Mes_Ano": "Mês/Ano",
                    "Entrada": st.column_config.NumberColumn("Valor", format="R$ %.2f")
                }
            )
        
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
            
            # Métricas
            col1, col2, col3 = st.columns(3)
            total_receita = resultado['Entrada'].sum()
            total_despesas = resultado['Saida'].sum()
            lucro_total = total_receita - total_despesas
            
            col1.metric("Receita Total", f"R${total_receita:,.2f}")
            col2.metric("Despesas Total", f"R${total_despesas:,.2f}")
            col3.metric(
                "Resultado Final",
                f"R${lucro_total:,.2f}",
                delta_color="inverse" if lucro_total < 0 else "normal"
            )
            
            # Gráfico interativo
            fig = px.bar(
                resultado,
                x='Mes_Ano',
                y='Lucro/Prejuízo',
                color='Lucro/Prejuízo',
                color_continuous_scale=[[0, 'red'], [1, 'green']],
                title="Lucro/Prejuízo Mensal",
                labels={'Lucro/Prejuízo': 'Valor (R$)', 'Mes_Ano': 'Mês/Ano'},
                text='Lucro/Prejuízo'
            )
            fig.update_traces(
                texttemplate='R$%{text:,.2f}',
                textposition='outside',
                hovertemplate="<b>Mês:</b> %{x}<br><b>Resultado:</b> R$%{y:,.2f}<extra></extra>"
            )
            fig.update_layout(
                hovermode="x unified",
                yaxis_tickprefix="R$",
                yaxis_tickformat=",.2f"
            )
            fig.add_hline(y=0, line_width=2, line_dash="dash", line_color="black")
            st.plotly_chart(fig, use_container_width=True)
        
        # Remove o arquivo temporário
        os.remove(temp_file)
        
    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {str(e)}")
        st.stop()

else:
    st.info("ℹ️ Por favor, faça upload de um arquivo Excel para análise")
