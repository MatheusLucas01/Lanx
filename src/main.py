# src/main.py
import sys
import os
import json
from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QLabel, QLineEdit, QMessageBox,
                                 QTabWidget, QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, QDateTime, QDate, QTime
from PyQt6.QtGui import QFont, QIcon, QPixmap

# Importar configurações
from config import PRODUCTS_FILE, SALES_FILE, LOGIN_BACKGROUND_IMAGE

# Importar componentes da UI do pacote 'ui'
from ui.dashboard import Dashboard
from ui.cadastro_tab import CadastroTab
from ui.estoque_tab import EstoqueTab
from ui.vendas_gerente_tab import VendasTab # Nome do arquivo alterado
from ui.fiscal_tab import FiscalTab
from ui.configuracoes_tab import ConfiguracoesTab
from ui.financeiro_tab import FinanceiroTab
from ui.pos_interface import POSInterface
# PaymentDialog é importado por POSInterface

class SistemaLanchonetePremium(QWidget):
        # Usa os caminhos importados de config.py
        PRODUCTS_FILE = PRODUCTS_FILE
        SALES_FILE = SALES_FILE
        LOGIN_BACKGROUND_IMAGE = LOGIN_BACKGROUND_IMAGE

        def __init__(self):
            super().__init__()
            self.setObjectName("mainWindow") # ID para estilização (background)
            print(f"DEBUG [Main]: Procurando products em: {self.PRODUCTS_FILE}")
            print(f"DEBUG [Main]: Procurando vendas em: {self.SALES_FILE}")
            print(f"DEBUG [Main]: Procurando imagem login em: {self.LOGIN_BACKGROUND_IMAGE}")

            self.setWindowTitle("Sistema de Lanchonete Premium")
            self.setGeometry(50, 50, 1350, 900) # Tamanho inicial

            # Layout principal que ocupará toda a janela
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0) # Sem margens
            self.main_layout.setSpacing(0) # Sem espaçamento

            self.products = [] # Inicializa a lista de produtos
            self.load_products_from_file()
            self.next_product_id = self.calculate_next_id()

            self.current_interface = None # Para rastrear a interface ativa (login, pos, manager)

            self.init_ui() # Mostra a tela de login inicial

        def calculate_next_id(self):
            """Calcula o próximo ID de produto disponível."""
            if not self.products: return 1
            # Garante que estamos pegando 'id' e tratando caso não exista ou não seja int
            max_id = 0
            for p in self.products:
                p_id = p.get('id', 0)
                if isinstance(p_id, int) and p_id > max_id:
                    max_id = p_id
            return max_id + 1

        def get_next_product_id(self):
            """Retorna o próximo ID e incrementa o contador."""
            current_id = self.next_product_id
            self.next_product_id += 1
            return current_id

        def load_products_from_file(self):
            """Carrega os produtos do arquivo JSON."""
            if os.path.exists(self.PRODUCTS_FILE):
                try:
                    with open(self.PRODUCTS_FILE, "r", encoding='utf-8') as f:
                        loaded_products = json.load(f)

                    # Validação e limpeza dos dados carregados
                    default_product = {'id': 0, 'name': '', 'description': '', 'price': 0.0, 'category': 'Outros', 'stock': 0}
                    valid_products = []
                    ids_seen = set()
                    if isinstance(loaded_products, list): # Verifica se é uma lista
                        for p in loaded_products:
                            if isinstance(p, dict): # Verifica se é um dicionário
                                merged_p = {**default_product, **p} # Garante campos padrão
                                p_id = merged_p.get('id')
                                # ID deve ser int > 0 e único
                                if isinstance(p_id, int) and p_id > 0 and p_id not in ids_seen:
                                    # Garante que price e stock são numéricos
                                    try: merged_p['price'] = float(merged_p.get('price', 0.0))
                                    except (ValueError, TypeError): merged_p['price'] = 0.0
                                    try: merged_p['stock'] = int(merged_p.get('stock', 0))
                                    except (ValueError, TypeError): merged_p['stock'] = 0

                                    valid_products.append(merged_p)
                                    ids_seen.add(p_id)
                                else:
                                    print(f"ALERTA [Main]: Produto inválido/duplicado ignorado no carregamento: {p}")
                            else:
                                print(f"ALERTA [Main]: Item inválido (não é dict) encontrado na lista de produtos: {p}")
                        self.products = valid_products
                    else:
                        print(f"ERRO [Main]: Conteúdo de {self.PRODUCTS_FILE} não é uma lista JSON.")
                        self.products = []

                except json.JSONDecodeError as e:
                    QMessageBox.warning(self, "Erro ao Carregar Produtos", f"O arquivo '{os.path.basename(self.PRODUCTS_FILE)}' está corrompido ou mal formatado.\nErro: {e}\n\nProdutos não foram carregados.")
                    self.products = []
                except IOError as e:
                    QMessageBox.warning(self, "Erro de Leitura", f"Não foi possível ler o arquivo de produtos.\nErro: {e}")
                    self.products = []
                except Exception as e:
                    QMessageBox.critical(self, "Erro Inesperado", f"Erro inesperado ao carregar produtos: {e}")
                    self.products = []
            else:
                print(f"AVISO [Main]: Arquivo {self.PRODUCTS_FILE} não encontrado. Iniciando com lista vazia.")
                self.products = []

            # Adiciona exemplos se o arquivo não existir ou estiver vazio após carregar/validar
            if not self.products:
                print("AVISO [Main]: Lista de produtos vazia. Adicionando exemplos e salvando.")
                self.products = [
                     {'id': 1, 'name': 'Hamburguer Clássico', 'description': 'Pão, carne, queijo', 'price': 18.50, 'category': 'Lanche', 'stock': 50},
                     {'id': 2, 'name': 'Coca-Cola Lata', 'description': '350ml', 'price': 5.00, 'category': 'Bebida', 'stock': 100},
                     {'id': 3, 'name': 'Batata Frita Média', 'description': 'Porção', 'price': 9.00, 'category': 'Lanche', 'stock': 80}
                ]
                self.save_products_to_file() # Salva os exemplos

            print(f"DEBUG [Main]: {len(self.products)} produtos carregados/inicializados.")


        def save_products_to_file(self):
            """Salva a lista atual de produtos no arquivo JSON."""
            print(f"DEBUG [Main]: Salvando {len(self.products)} produtos em {self.PRODUCTS_FILE}...")
            try:
                with open(self.PRODUCTS_FILE, "w", encoding='utf-8') as f:
                    json.dump(self.products, f, indent=4, ensure_ascii=False)
                print("DEBUG [Main]: Produtos salvos com sucesso.")
            except IOError as e:
                QMessageBox.critical(self, "Erro ao Salvar Produtos", f"Não foi possível salvar as alterações nos produtos.\nErro: {e}")
            except Exception as e:
                 QMessageBox.critical(self, "Erro Inesperado", f"Erro inesperado ao salvar produtos: {e}")

        def init_ui(self):
            """Inicializa a interface (começa com a tela de login)."""
            self.show_login_window()

        def clear_layout(self):
            """Remove todos os widgets do layout principal."""
            if self.main_layout is None: return
            while self.main_layout.count():
                child = self.main_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater() # Marca para exclusão segura

        def show_login_window(self):
            """Configura e exibe a tela de login."""
            print("DEBUG [Main]: Configurando tela de login...")
            self.clear_layout() # Limpa a interface anterior
            self.current_interface = 'login'

            # --- Estilo com Background ---
            bg_style = ""
            image_path = self.LOGIN_BACKGROUND_IMAGE
            if os.path.exists(image_path):
                # Converte para path absoluto e usa / para QSS
                bg_image_path_qss = os.path.abspath(image_path).replace("\\", "/")
                # Usar border-image para melhor controle de preenchimento/esticamento
                bg_style = f"""
                    QWidget#mainWindow {{
                        border-image: url('{bg_image_path_qss}') 0 0 0 0 stretch stretch;
                    }}
                    /* Estilo para o frame de login ficar visível sobre o fundo */
                    QFrame#loginFrame {{
                        background-color: rgba(255, 255, 255, 0.92); /* Fundo branco semi-transparente */
                        border-radius: 15px;
                        border: 1px solid rgba(0, 0, 0, 0.1);
                    }}
                    QLineEdit {{
                        padding: 10px;
                        border: 1px solid #ced4da;
                        border-radius: 5px;
                        font-size: 11pt;
                        background-color: white; /* Garante fundo branco */
                    }}
                    QPushButton#primaryButton {{
                        background-color: #007bff;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 12px;
                        font-size: 11pt;
                        font-weight: bold;
                    }}
                    QPushButton#primaryButton:hover {{ background-color: #0056b3; }}
                    QLabel#loginTitleLabel {{ /* ID para o título */
                        color: #0056b3;
                        background: transparent; /* Sem fundo próprio */
                        font-weight: bold;
                        font-size: 24pt;
                        margin-bottom: 10px;
                    }}
                """
                print(f"DEBUG [Main]: Estilo de fundo da imagem aplicado: {bg_image_path_qss}")
            else:
                print(f"ERRO [Main]: Imagem de fundo NÃO encontrada em: {image_path}")
                # Estilo básico sem imagem
                bg_style = """
                    QWidget#mainWindow { background-color: #e9ecef; }
                    QFrame#loginFrame { background-color: white; border-radius: 10px; }
                    /* ... outros estilos básicos ... */
                """
            self.setStyleSheet(bg_style)

            # --- Widgets de Login ---
            # Widget centralizador para alinhar o frame no meio
            center_widget = QWidget()
            center_layout = QHBoxLayout(center_widget) # Layout horizontal para centralizar
            center_layout.addStretch() # Empurra para a direita

            login_frame = QFrame(); login_frame.setObjectName("loginFrame")
            login_frame.setFixedWidth(400); login_frame.setMaximumHeight(450)
            frame_layout = QVBoxLayout(login_frame)
            frame_layout.setContentsMargins(40, 40, 40, 40); frame_layout.setSpacing(20)

            self.titulo_label = QLabel("MR Lanches")
            self.titulo_label.setObjectName("loginTitleLabel") # Aplica o ID do estilo
            self.titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(self.titulo_label)

            frame_layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

            self.usuario_entry = QLineEdit(); self.usuario_entry.setPlaceholderText("Usuário")
            frame_layout.addWidget(self.usuario_entry)

            self.senha_entry = QLineEdit(); self.senha_entry.setPlaceholderText("Senha")
            self.senha_entry.setEchoMode(QLineEdit.EchoMode.Password)
            frame_layout.addWidget(self.senha_entry)

            frame_layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

            self.login_button = QPushButton("Entrar"); self.login_button.setObjectName("primaryButton")
            self.login_button.setMinimumHeight(45)
            frame_layout.addWidget(self.login_button)

            # Conexões
            self.login_button.clicked.connect(self.validar_login)
            self.senha_entry.returnPressed.connect(self.validar_login) # Enter na senha

            center_layout.addWidget(login_frame) # Adiciona frame ao centro
            center_layout.addStretch() # Empurra para a esquerda

            # Adiciona o widget centralizador ao layout principal da janela
            self.main_layout.addWidget(center_widget)

            self.usuario_entry.setFocus() # Foco no campo de usuário
            print("DEBUG [Main]: Tela de login exibida.")


        def validar_login(self):
            """Valida as credenciais de login."""
            usuario = self.usuario_entry.text().strip().lower() # Ignora espaços e caixa
            senha = self.senha_entry.text()

            if usuario == "caixa" and senha == "123":
                print("DEBUG [Main]: Login como CAIXA bem-sucedido.")
                self.show_pos_interface()
            elif usuario == "admin" and senha == "admin":
                print("DEBUG [Main]: Login como ADMIN bem-sucedido.")
                self.show_manager_interface()
            else:
                print(f"ERRO [Main]: Tentativa de login falhou. Usuário: '{usuario}'")
                QMessageBox.critical(self, "Erro de Login", "Usuário ou senha inválidos!")
                self.senha_entry.clear()
                self.usuario_entry.setFocus()
                self.usuario_entry.selectAll()

        def show_manager_interface(self):
            """Configura e exibe a interface do Gerente com abas."""
            print("DEBUG [Main]: Configurando interface do Gerente...")
            self.clear_layout()
            self.current_interface = 'manager'
            self.setStyleSheet("") # Remove o estilo de background do login

            self.tab_widget = QTabWidget()
            self.tab_widget.setStyleSheet("""
                QTabWidget::pane { border: 1px solid #C4C4C3; top:-1px; background: #f8f9fa; border-radius: 5px; }
                QTabBar::tab { background: #e1e1e1; border: 1px solid #C4C4C3; border-bottom-color: #C2C7CB; border-top-left-radius: 4px; border-top-right-radius: 4px; min-width: 8ex; padding: 8px 15px; margin-right: 2px; }
                QTabBar::tab:selected, QTabBar::tab:hover { background: #d4d4d4; }
                QTabBar::tab:selected { border-color: #9B9B9B; border-bottom-color: #f8f9fa; /* Mesmo fundo do pane */ font-weight: bold; }
                QTabBar::tab:!selected { margin-top: 2px; }
            """)

            # Instancia as abas, passando 'self' (main_window) como referência
            self.dashboard_tab = Dashboard(self)
            self.tab_widget.addTab(self.dashboard_tab, "📊 Resumo")

            self.cadastro_tab = CadastroTab(self)
            self.tab_widget.addTab(self.cadastro_tab, "📋 Cadastros")

            self.financeiro_tab = FinanceiroTab(self)
            self.tab_widget.addTab(self.financeiro_tab, "💰 Financeiro")

            self.estoque_tab = EstoqueTab(self)
            self.tab_widget.addTab(self.estoque_tab, "📦 Estoque")

            self.vendas_gerente_tab = VendasTab(self) # Usando a classe correta
            self.tab_widget.addTab(self.vendas_gerente_tab, "🛒 Venda Rápida") # Nome mais descritivo

            self.fiscal_tab = FiscalTab() # Não precisa de 'self' por enquanto
            self.tab_widget.addTab(self.fiscal_tab, "🧾 Fiscal")

            self.configuracoes_tab = ConfiguracoesTab(self) # Passa 'self'
            self.tab_widget.addTab(self.configuracoes_tab, "⚙️ Configurações")

            self.tab_widget.currentChanged.connect(self.tab_changed) # Conecta sinal de mudança de aba
            self.main_layout.addWidget(self.tab_widget) # Adiciona o widget de abas ao layout principal

            # Chama manualmente o método da primeira aba para carregar dados iniciais
            self.tab_changed(0)
            print("DEBUG [Main]: Interface do Gerente exibida.")

        def tab_changed(self, index):
            """Chamado quando o usuário troca de aba na interface do gerente."""
            current_tab_widget = self.tab_widget.widget(index)
            tab_name = self.tab_widget.tabText(index)
            print(f"DEBUG [Main]: Aba alterada para: {tab_name} (Índice: {index})")

            # Tenta chamar métodos específicos de atualização/carregamento da aba ativa
            if hasattr(current_tab_widget, 'update_summary'):
                print(f"-> Chamando update_summary() para {tab_name}")
                current_tab_widget.update_summary()
            elif hasattr(current_tab_widget, 'load_data'):
                print(f"-> Chamando load_data() para {tab_name}")
                current_tab_widget.load_data()
            elif hasattr(current_tab_widget, 'load_estoque'):
                 print(f"-> Chamando load_estoque() para {tab_name}")
                 current_tab_widget.load_estoque()
            elif hasattr(current_tab_widget, 'update_products_combo'):
                 print(f"-> Chamando update_products_combo() para {tab_name}")
                 current_tab_widget.update_products_combo()
            elif hasattr(current_tab_widget, 'load_products_to_table'): # Para aba Cadastro
                 print(f"-> Chamando load_products_to_table() para {tab_name}")
                 current_tab_widget.load_products_to_table()
            # Adicione outras chamadas 'elif' para métodos de outras abas se necessário

        def show_pos_interface(self):
            """Configura e exibe a interface do Ponto de Venda (Caixa)."""
            print("DEBUG [Main]: Configurando interface do POS...")
            self.clear_layout()
            self.current_interface = 'pos'
            self.setStyleSheet("") # Remove estilo de background do login

            # --- Header Simples para o POS ---
            header = QLabel("Ponto de Venda - Caixa")
            header.setStyleSheet("""
                background-color: #343a40; /* Cor escura */
                color: white;
                padding: 10px 15px;
                font-size: 14pt;
                font-weight: bold;
            """)
            header.setFixedHeight(45) # Altura fixa
            self.main_layout.addWidget(header) # Adiciona header no topo

            # --- Interface POS ---
            # Garante que os produtos estão carregados antes de criar o POS
            if not self.products:
                print("ALERTA [Main]: Tentando mostrar POS, mas lista de produtos está vazia. Recarregando...")
                self.load_products_from_file()
                if not self.products:
                    QMessageBox.critical(self, "Erro Fatal", "Não foi possível carregar os produtos necessários para o Ponto de Venda.")
                    self.show_login_window() # Volta para o login
                    return

            try:
                # Cria a instância da interface POS, passando a lista de produtos ATUAL
                self.pos_interface = POSInterface(self, self.products)
                # Adiciona a interface POS ao layout, fazendo-a ocupar o espaço restante (stretch=1)
                self.main_layout.addWidget(self.pos_interface, 1)
                print("DEBUG [Main]: Interface POS exibida.")
            except Exception as e_pos:
                 print(f"ERRO CRÍTICO [Main]: Falha ao criar ou adicionar POSInterface: {e_pos}")
                 QMessageBox.critical(self, "Erro ao Iniciar POS", f"Não foi possível carregar o Ponto de Venda:\n{e_pos}")
                 self.show_login_window() # Tenta voltar para o login em caso de erro grave

        def update_pos_shortcuts(self):
            """Informa a interface POS para atualizar seus atalhos (se existir)."""
            if self.current_interface == 'pos' and hasattr(self, 'pos_interface'):
                print("DEBUG [Main]: Solicitando atualização de atalhos do POS devido à mudança de estoque.")
                self.pos_interface.update_products(self.products) # Passa a lista atualizada

        def update_estoque_global(self, product_name, quantidade_vendida):
            """Atualiza o estoque de um produto na lista principal e salva."""
            updated = False
            stock_updated = False
            for product in self.products:
                if product.get('name') == product_name:
                    current_stock = product.get('stock', 0)
                    new_stock = current_stock - quantidade_vendida
                    product['stock'] = new_stock if new_stock >= 0 else 0 # Evita estoque negativo
                    stock_updated = True
                    print(f"DEBUG [Main]: Estoque atualizado - Produto: {product_name}, Qtd Vendida: {quantidade_vendida}, Novo Estoque: {product['stock']}")
                    if product['stock'] < 5: # Limite de alerta baixo
                        print(f"ALERTA [Main]: Estoque baixo para {product_name} ({product['stock']})")
                    break # Para após encontrar e atualizar

            if stock_updated:
                self.save_products_to_file() # Salva a lista de produtos com estoque atualizado
                # Atualiza a aba de estoque se estiver visível no modo gerente
                if self.current_interface == 'manager' and hasattr(self, 'estoque_tab') and self.tab_widget.currentWidget() == self.estoque_tab:
                    print("-> Atualizando tabela de EstoqueTab após venda.")
                    self.estoque_tab.load_estoque()
                # Atualiza os atalhos no POS se ele estiver ativo
                self.update_pos_shortcuts()
            else:
                print(f"AVISO [Main]: Produto '{product_name}' não encontrado para atualização de estoque.")


        def registrar_venda_historico(self, total, metodo_pagamento, itens_vendidos):
            """Salva uma venda no histórico e atualiza o estoque."""
            print(f"DEBUG [Main]: Registrando Venda - Total: {total}, Método: {metodo_pagamento}, Itens: {len(itens_vendidos)}")

            # 1. Atualiza o estoque para cada item vendido
            for item in itens_vendidos:
                nome = item.get('produto')
                qtd = item.get('quantidade')
                if nome and isinstance(qtd, int) and qtd > 0:
                    self.update_estoque_global(nome, qtd)
                else:
                    print(f"AVISO [Main]: Item inválido ignorado na atualização de estoque: {item}")

            # 2. Cria o registro da venda
            venda = {
                'data': QDateTime.currentDateTime().toString(Qt.DateFormat.ISODate), # Formato ISO 8601
                'itens': itens_vendidos, # Lista de dicts {'produto': nome, 'quantidade': qtd, 'preco': preco_unit}
                'total': float(total), # Garante float
                'metodo_pagamento': metodo_pagamento
            }

            # 3. Salva a venda no arquivo JSON
            self.salvar_venda(venda)

            # 4. Atualiza o Dashboard e Relatórios se estiverem visíveis no modo Gerente
            if self.current_interface == 'manager':
                if hasattr(self, 'dashboard_tab') and self.tab_widget.currentWidget() == self.dashboard_tab:
                    print("-> Atualizando Dashboard após venda.")
                    self.dashboard_tab.update_summary()
                if hasattr(self, 'financeiro_tab') and self.tab_widget.currentWidget() == self.financeiro_tab:
                    print("-> Atualizando FinanceiroTab após venda.")
                    self.financeiro_tab.load_data() # Recarrega os dados do relatório

        def salvar_venda(self, venda):
            """Adiciona uma venda ao arquivo JSON de histórico."""
            vendas = []
            try:
                if os.path.exists(self.SALES_FILE) and os.path.getsize(self.SALES_FILE) > 0: # Verifica se não está vazio
                    with open(self.SALES_FILE, "r", encoding='utf-8') as f:
                        vendas = json.load(f)
                    if not isinstance(vendas, list): # Se o conteúdo não for uma lista, reseta
                        print(f"ALERTA [Main]: Conteúdo de {self.SALES_FILE} não era uma lista. Resetando.")
                        vendas = []
                else:
                    vendas = [] # Arquivo não existe ou está vazio
            except json.JSONDecodeError:
                print(f"ALERTA [Main]: Arquivo {self.SALES_FILE} corrompido. Histórico de vendas será sobrescrito.")
                vendas = []
            except IOError as e:
                 print(f"AVISO [Main]: Não foi possível ler {self.SALES_FILE}: {e}. Iniciando nova lista.")
                 vendas = []

            vendas.append(venda) # Adiciona a nova venda à lista

            try:
                with open(self.SALES_FILE, "w", encoding='utf-8') as f:
                    json.dump(vendas, f, indent=4, ensure_ascii=False)
                print(f"DEBUG [Main]: Venda salva em {self.SALES_FILE}.")
            except IOError as e:
                QMessageBox.critical(self, "Erro Crítico", f"Não foi possível salvar a venda no histórico.\nErro: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Erro Inesperado", f"Erro inesperado ao salvar venda: {e}")


        def clear_sales_data(self):
            """Apaga o conteúdo do arquivo de vendas (chamado pela ConfiguracoesTab)."""
            print(f"--- ATENÇÃO [Main]: Iniciando processo para zerar {self.SALES_FILE} ---")
            try:
                # Escreve uma lista JSON vazia '[]' no arquivo, sobrescrevendo
                with open(self.SALES_FILE, "w", encoding='utf-8') as f:
                    json.dump([], f)
                print(f"--- SUCESSO [Main]: Arquivo {self.SALES_FILE} zerado. ---")
                QMessageBox.information(self, "Histórico Zerado", "O histórico de vendas foi apagado com sucesso.")

                # Atualizar UIs relevantes (se estiverem na interface do gerente)
                if self.current_interface == 'manager':
                    if hasattr(self, 'dashboard_tab') and self.tab_widget.currentWidget() == self.dashboard_tab:
                        print("-> Atualizando Dashboard após zerar vendas.")
                        self.dashboard_tab.update_summary()
                    if hasattr(self, 'financeiro_tab') and self.tab_widget.currentWidget() == self.financeiro_tab:
                        print("-> Atualizando FinanceiroTab após zerar vendas.")
                        self.financeiro_tab.generate_report() # Gera relatório vazio

            except (IOError, Exception) as e:
                print(f"--- ERRO CRÍTICO [Main] ao tentar zerar {self.SALES_FILE}: {e} ---")
                QMessageBox.critical(self, "Erro ao Zerar Histórico", f"Não foi possível apagar o histórico de vendas.\nErro: {e}")


    # --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
        app = QApplication(sys.argv)
        # Adicionar um ícone à aplicação (opcional)
        # app_icon = QIcon("path/to/your/icon.png")
        # app.setWindowIcon(app_icon)

        sistema = SistemaLanchonetePremium()
        sistema.show() # Mostra a janela principal (que inicia com o login)
        sys.exit(app.exec())
