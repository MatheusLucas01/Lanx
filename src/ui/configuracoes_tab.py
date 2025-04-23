# src/ui/configuracoes_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                QLineEdit, QMessageBox, QInputDialog, QSpacerItem,
                                QSizePolicy, QFrame, QGridLayout, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class ConfiguracoesTab(QWidget):
       def __init__(self, main_window): # Recebe a instância principal
           super().__init__()
           self.main_window = main_window # Armazena para chamar clear_sales_data

           layout = QVBoxLayout(self) # Layout principal vertical
           layout.setSpacing(20)
           layout.setContentsMargins(25, 25, 25, 25)

           title_label = QLabel("Configurações do Sistema")
           title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
           title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
           layout.addWidget(title_label)

           # --- Frame de Configurações Gerais ---
           general_frame = QFrame()
           general_frame.setFrameShape(QFrame.Shape.StyledPanel)
           general_layout = QGridLayout(general_frame)
           general_layout.setSpacing(10)

           general_layout.addWidget(QLabel("Nome da Lanchonete:"), 0, 0)
           self.shop_name_input = QLineEdit("MR Lanches") # Valor padrão
           general_layout.addWidget(self.shop_name_input, 0, 1)

           general_layout.addWidget(QLabel("Endereço:"), 1, 0)
           self.address_input = QLineEdit("Rua Exemplo, 123") # Valor padrão
           general_layout.addWidget(self.address_input, 1, 1)

           general_layout.addWidget(QLabel("Taxa de Serviço (%):"), 2, 0)
           self.tax_spin = QSpinBox()
           self.tax_spin.setSuffix(" %")
           self.tax_spin.setMinimum(0)
           self.tax_spin.setMaximum(100)
           # self.tax_spin.setValue(10) # Valor padrão, se desejar
           general_layout.addWidget(self.tax_spin, 2, 1)

           # Adiciona stretch para não espremer os campos se a janela for alta
           general_layout.setRowStretch(3, 1)

           layout.addWidget(general_frame)

           # --- Botão Salvar Configurações ---
           save_button = QPushButton("Salvar Configurações")
           save_button.setObjectName("primaryButton") # Para estilização QSS se houver
           save_button.setStyleSheet("padding: 8px 15px; font-weight: bold; background-color: #007bff; color: white; border-radius: 5px;")
           save_button.clicked.connect(self.save_settings) # Conectar a uma função
           layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignCenter)

           # --- SEÇÃO DE AÇÕES PERIGOSAS ---
           layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)) # Espaço

           danger_title = QLabel("Ações Perigosas")
           danger_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #dc3545;")
           danger_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
           layout.addWidget(danger_title)

           danger_frame = QFrame()
           danger_frame.setFrameShape(QFrame.Shape.StyledPanel)
           danger_frame.setStyleSheet("border: 1px solid #dc3545; border-radius: 5px; background-color: #f8d7da;") # Fundo avermelhado
           danger_layout = QVBoxLayout(danger_frame)
           danger_layout.setSpacing(10)

           self.clear_sales_button = QPushButton("Zerar Histórico de Vendas")
           self.clear_sales_button.setObjectName("dangerButton")
           self.clear_sales_button.setStyleSheet("""
               QPushButton#dangerButton { background-color: #dc3545; color: white; border: none; border-radius: 5px; padding: 10px 20px; font-weight: bold; font-size: 14px; }
               QPushButton#dangerButton:hover { background-color: #c82333; }
               QPushButton#dangerButton:pressed { background-color: #bd2130; }
           """)
           self.clear_sales_button.clicked.connect(self.confirm_clear_sales_history)
           danger_layout.addWidget(self.clear_sales_button, alignment=Qt.AlignmentFlag.AlignCenter)

           layout.addWidget(danger_frame)

           # Adiciona um espaçador expansível no final para empurrar tudo para cima
           layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

       def save_settings(self):
           # Aqui você implementaria a lógica para salvar as configurações
           # Por exemplo, em um arquivo JSON de configurações ou no registro
           shop_name = self.shop_name_input.text()
           address = self.address_input.text()
           tax_rate = self.tax_spin.value()
           print(f"DEBUG [ConfigTab]: Salvando configurações - Nome: {shop_name}, End: {address}, Taxa: {tax_rate}%")
           # Exemplo: self.main_window.save_app_settings({'shop_name': shop_name, ...})
           QMessageBox.information(self, "Configurações", "Configurações salvas (simulado).")

       def confirm_clear_sales_history(self):
           """Exibe um diálogo de confirmação MUITO claro antes de zerar as vendas."""
           confirm_msg = (
               "<b>ATENÇÃO! AÇÃO IRREVERSÍVEL!</b><br><br>"
               "Você tem certeza ABSOLUTA que deseja apagar TODO o histórico de vendas?<br><br>"
               "Todos os registros de vendas serão permanentemente removidos e não poderão ser recuperados.<br><br>"
               "<b>Digite 'SIM' (em maiúsculas) para confirmar:</b>"
           )

           text, ok = QInputDialog.getText(
               self,
               "Confirmar Exclusão Total de Vendas",
               confirm_msg,
               QLineEdit.EchoMode.Normal,
               "" # Texto inicial vazio
           )

           if ok and text == "SIM":
               # Segunda confirmação
               reply = QMessageBox.warning(
                   self,
                   "Confirmação Final",
                   "Esta é sua última chance. Zerar o histórico de vendas?",
                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                   QMessageBox.StandardButton.No # Padrão é Não
               )
               if reply == QMessageBox.StandardButton.Yes:
                   print("Confirmação recebida. Solicitando limpeza de vendas...")
                   # Chama o método na janela principal para realmente fazer a limpeza
                   if hasattr(self.main_window, 'clear_sales_data'):
                       self.main_window.clear_sales_data()
                   else:
                       QMessageBox.critical(self, "Erro Interno", "A função para limpar dados não foi encontrada na janela principal.")
               else:
                   QMessageBox.information(self, "Cancelado", "A operação foi cancelada.")
           elif ok: # Clicou OK mas não digitou SIM
               QMessageBox.warning(self, "Confirmação Inválida", "A confirmação 'SIM' não foi digitada corretamente. Operação cancelada.")
           else: # Clicou Cancelar
                QMessageBox.information(self, "Cancelado", "A operação foi cancelada.")
