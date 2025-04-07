import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mplcursors
from matplotlib.widgets import Button
import os

class GestaoFinanceira:
    def __init__(self, file_path):
        self.file_path = file_path
        try:
            self.df = pd.read_excel(file_path)
            self.processar_dados()
        except Exception as e:
            print(f"Error loading or processing file: {e}")
            raise
    
    def processar_dados(self):
        self.df['Data'] = pd.to_datetime(self.df['Data'], errors='coerce')
        self.df['Mes_Ano'] = self.df['Data'].dt.to_period('M')
        
        for col in ['Entrada', 'Saida']:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        self.df.dropna(subset=['Entrada', 'Saida'], how='all', inplace=True)
    
    def calcular_receita_bruta(self):
        receita_mensal = self.df.groupby('Mes_Ano')['Entrada'].sum().reset_index()
        receita_mensal['Mes_Ano'] = receita_mensal['Mes_Ano'].astype(str)
        return receita_mensal
    
    def calcular_despesas(self):
        df_despesas = self.df[self.df['Saida'].notnull()].copy()
        df_despesas.dropna(subset=['Nome Natureza'], inplace=True)

        categorias = {
            "Despesas Operacionais": ["SERVICOS DE PUBLICIDADE E PROP", "MARKETING DIRETO", "SERVICO DE DIVULGACAO", 
                                    "CONSULTORIA", "LICENCA DE USO", "SERVICOS INFORMATICA", 
                                    "SERVICOS LIMPEZA E CONSERVACAO", "CERTIFICADO DIGITAL"],
            "Despesas Administrativas": ["ALUGUEL DE IMOVEIS", "CONDOMINIO", "ENERGIA ELETRICA", 
                                       "TELEFONIA  MOVEL", "TELEFONIA  FIXA", "MATERIAL DE EXPEDIENTE"],
            "Despesas Financeiras e Tributárias": ["TARIFAS BANCARIAS", "IOF", "JUROS PAGOS", 
                                                 "IRRF APLICACAO FINANCEIRA", "SIMPLES NACIONAL", 
                                                 "EMOLUMENTOS CARTORIOS", "TAXAS MUNICIPAIS", 
                                                 "CIM CADASTRO INSCRICAO MUNICIP"],
            "Despesas com Pessoal": ["PRO LABORE", "INSS SOBRE PRO LABORE", "CONFRATERNIZACAO", 
                                     "CURSOS E TREINAMENTOS", "LANCHES E REFEICOES"],
            "Investimentos e Aplicações": ["APLICACAO ITAU AUTO MAIS", "RESGATE ITAU AUTO MAIS", 
                                         "RESGATE INTER CDB MAIS", "APLICACAO INTER CDB MAIS", 
                                         "AJUSTE DE RENDIMENTO APLICACAO", "RENDIMENTO DE APLICACOES FINAN", 
                                         "CONSORCIO ITAU"],
            "Despesas Eventuais e Diversas": ["ADIANT. DE LUCRO", "ADIANTAMENTO DE CLIENTES", 
                                            "ENTRADAS DE TRANSFERENCIAS", "PAGAMENTOS DIVERSOS", 
                                            "OUTRAS DESPESAS", "SEGUROS PESSOAIS E EMPRESARIAI", 
                                            "MULTAS PUNITIVAS", "DOACOES E CONTRIBUICOES", 
                                            "CONDUCAO E TRANSPORTE", "IPTU IMP PREDIAL TERRIT URBANO"]
        }
        
        def categorizar(nome):
            if pd.isna(nome):
                return "Outros"
            nome = str(nome).upper()
            for categoria, itens in categorias.items():
                if any(pd.notna(nome) and pd.Series(nome).str.contains(item, case=False, na=False).any() for item in itens):  # Verificação mais flexível
                    return categoria  
            return 

        df_despesas['Categoria'] = df_despesas['Nome Natureza'].apply(categorizar)
        df_despesas['Mes_Ano'] = df_despesas['Mes_Ano'].astype(str)
        despesas_mensais = df_despesas.groupby(['Mes_Ano', 'Categoria'])['Saida'].sum().reset_index()
        return despesas_mensais
    
    def calcular_resultado_financeiro(self):
        receita = self.calcular_receita_bruta()
        despesas = self.calcular_despesas().groupby('Mes_Ano')['Saida'].sum().reset_index()
        resultado = receita.merge(despesas, on='Mes_Ano', how='left').fillna(0)
        resultado['Lucro/Prejuízo'] = resultado['Entrada'] - resultado['Saida']
        return resultado
    
    def visualizar_dados(self):
        try:
            receita = self.calcular_receita_bruta()
            despesas = self.calcular_despesas()
            resultado = self.calcular_resultado_financeiro()
            
            sns.set_theme(style="whitegrid")
            
            # Gráfico 1: Receita Mensal (mantido como está)
            plt.figure(figsize=(12, 6))
            ax = sns.barplot(x='Mes_Ano', y='Entrada', data=receita, hue='Mes_Ano', 
                            legend=False, palette="coolwarm", dodge=False)
            for p in ax.patches:
                ax.annotate(f"R${p.get_height():,.2f}", 
                           (p.get_x() + p.get_width() / 2., p.get_height()), 
                           ha='center', va='bottom', fontsize=10, color='black')
            plt.xticks(rotation=45)
            plt.title("Receita Bruta Mensal")
            plt.xlabel("Mês/Ano")
            plt.ylabel("Valor (R$)")
            plt.tight_layout()
            plt.show()
            

            # Gráfico 2: Despesas por Categoria (linhas)

            # Preparar os dados
            pivot_despesas = despesas.pivot(index='Mes_Ano', columns='Categoria', values='Saida').fillna(0)

            # Plotar linhas para cada categoria com marcadores apenas nos meses
            ax = pivot_despesas.plot(kind='line', marker='o', markersize=8, linewidth=2.5, figsize=(18, 10), 
                                    colormap='tab20', alpha=0.8)

            # Adicionar apenas os pontos fixos para os meses
            for categoria in pivot_despesas.columns:
                plt.scatter(pivot_despesas.index, pivot_despesas[categoria], label=categoria, alpha=0)

            # Ajustes estéticos
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.yticks(fontsize=10)
            plt.title("Evolução das Despesas por Categoria", fontsize=14, pad=20)
            plt.xlabel("Mês/Ano", fontsize=12, labelpad=10)
            plt.ylabel("Valor (R$)", fontsize=12, labelpad=10)
            plt.legend(title='Categorias', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9, title_fontsize=10)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout(pad=3.0)

            # Tooltips interativos apenas para os pontos dos meses
            cursor = mplcursors.cursor(plt.gca().collections, hover=True)

            @cursor.connect("add")
            def on_add(sel):
                x, y = sel.target
                mes = pivot_despesas.index[int(x)]
                categoria = sel.artist.get_label()
                valor = y

                sel.annotation.set(text=f"Mês: {mes}\nCategoria: {categoria}\nValor: R${valor:,.2f}",
                                bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.9),
                                fontsize=10)

            plt.show()

            
            # Gráfico 3: Lucro/Prejuízo Mensal (com tooltips)
            plt.figure(figsize=(12, 6))
            ax = sns.barplot(x='Mes_Ano', y='Lucro/Prejuízo', data=resultado, 
                            hue='Mes_Ano', legend=False, 
                            palette=['red' if x < 0 else 'green' for x in resultado['Lucro/Prejuízo']])
            
            # Adicionando tooltips
            cursor = mplcursors.cursor(ax, hover=True)
            @cursor.connect("add")
            def on_add(sel):
                x, y = sel.target
                mes = resultado['Mes_Ano'].iloc[int(x)]
                valor = y
                situacao = "Prejuízo" if valor < 0 else "Lucro"
                sel.annotation.set_text(f"Mês: {mes}\n{situacao}: R${abs(valor):,.2f}")
                sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)
            
            plt.axhline(0, color='black', linewidth=1.2, linestyle='dashed')
            plt.xticks(rotation=45)
            plt.title("Lucro/Prejuízo Mensal (passe o mouse para ver os valores)")
            plt.xlabel("Mês/Ano")
            plt.ylabel("Valor (R$)")
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error visualizing data: {e}")
            raise

# Exemplo de uso
try:
    # Obtém o diretório atual do script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Constrói o caminho absoluto para o arquivo
    file_path = os.path.join(base_dir, "../../planilha.xlsx")
    gestao = GestaoFinanceira(file_path)
    gestao.visualizar_dados()
except Exception as e:
    print(f"Error in main execution: {e}")