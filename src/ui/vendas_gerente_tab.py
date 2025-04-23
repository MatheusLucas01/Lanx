# src/ui/vendas_gerente_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
                                QFrame, QGridLayout, QSpinBox, QInputDialog, QHeaderView)
from PyQt6.QtCore import Qt

class VendasTab(QWidget): # Interface de Vendas para o Gerente
       def __init__(self, main_window):
           super().__init__()
           self.main_window = main_window
           self.carrinho_local = [] # Carrinho específico desta aba
           layout = QGridLayout(self)

           title_label = QLabel("Registro Rápido de Vendas (Gerente)")
           title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
           layout.addWidget(title_label, 0, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignCenter)

           # --- Frame para Adicionar Item ---
           add_item_frame = QFrame(); add_item_frame.setFrameShape(QFrame.Shape.StyledPanel)
           add_item_layout = QGridLayout(add_item_frame)
           add_item_layout.addWidget(QLabel("Produto:"), 0, 0)
           self.produto_combo = QComboBox()
           # Chama update_products_combo APÓS o combo ser criado
           add_item_layout.addWidget(self.produto_combo, 0, 1)
           add_item_layout.addWidget(QLabel("Quantidade:"), 1, 0)
           self.quantidade_spinbox = QSpinBox(); self.quantidade_spinbox.setMinimum(1); self.quantidade_spinbox.setMaximum(999) # Limite razoável
           add_item_layout.addWidget(self.quantidade_spinbox, 1, 1)
           self.adicionar_button = QPushButton("Adicionar ao Carrinho"); self.adicionar_button.clicked.connect(self.adicionar_ao_carrinho_local)
           add_item_layout.addWidget(self.adicionar_button, 2, 0, 1, 2)
           layout.addWidget(add_item_frame, 1, 0, 1, 2) # Ocupa 2 colunas

           # --- Frame do Carrinho ---
           cart_frame = QFrame(); cart_frame.setFrameShape(QFrame.Shape.StyledPanel)
           cart_layout = QVBoxLayout(cart_frame)
           cart_layout.addWidget(QLabel("Carrinho:"))
           self.carrinho_table = QTableWidget(); self.carrinho_table.setColumnCount(4); # Produto, Qtd, Preço Unit, Subtotal
           self.carrinho_table.setHorizontalHeaderLabels(["Produto", "Qtd", "Preço Unit.", "Subtotal"])
           self.carrinho_table.verticalHeader().setVisible(False)
           self.carrinho_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
           self.carrinho_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
           self.carrinho_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
           self.carrinho_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
           self.carrinho_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
           self.carrinho_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
           self.carrinho_table.setAlternatingRowColors(True)
           cart_layout.addWidget(self.carrinho_table)

           # --- Total e Botão Finalizar ---
           total_layout = QHBoxLayout()
           self.total_label = QLabel("Total: R$ 0.00")
           self.total_label.setStyleSheet("font-weight: bold; font-size: 14pt;")
           total_layout.addWidget(self.total_label)
           total_layout.addStretch() # Empurra botão para direita
           self.finalizar_button = QPushButton("Finalizar Venda"); self.finalizar_button.clicked.connect(self.finalizar_venda_local)
           self.finalizar_button.setStyleSheet("padding: 8px 15px; background-color: #28a745; color: white; font-weight: bold;")
           total_layout.addWidget(self.finalizar_button)
           cart_layout.addLayout(total_layout)

           layout.addWidget(cart_frame, 1, 2, 1, 2) # Ocupa 2 colunas

           # Ajustes de Stretch
           layout.setRowStretch(2, 1) # Linha abaixo dos frames pode esticar
           layout.setColumnStretch(0, 1)
           layout.setColumnStretch(1, 1)
           layout.setColumnStretch(2, 1)
           layout.setColumnStretch(3, 1)

           self.update_products_combo() # Carrega produtos no combo

       def update_products_combo(self):
           current_text = self.produto_combo.currentText()
           self.produto_combo.clear()
           # Adiciona apenas produtos com estoque > 0 e ordena por nome
           available_products = sorted(
               [p for p in self.main_window.products if p.get('stock', 0) > 0],
               key=lambda x: x.get('name', '')
           )
           for product in available_products:
               # Armazena o ID do produto junto com o nome para fácil acesso
               self.produto_combo.addItem(product['name'], userData=product['id'])

           index = self.produto_combo.findText(current_text)
           if index >= 0:
               self.produto_combo.setCurrentIndex(index)
           elif self.produto_combo.count() > 0:
               self.produto_combo.setCurrentIndex(0)

       def adicionar_ao_carrinho_local(self):
           selected_index = self.produto_combo.currentIndex()
           if selected_index < 0: return # Nenhum item selecionado

           product_id = self.produto_combo.itemData(selected_index) # Pega o ID armazenado
           product_name = self.produto_combo.currentText()
           quantity = self.quantidade_spinbox.value()
           if quantity <= 0: return

           # Encontra dados do produto usando o ID
           product_data = next((p for p in self.main_window.products if p.get('id') == product_id), None)
           if not product_data:
               QMessageBox.warning(self, "Erro", f"Dados do produto '{product_name}' (ID: {product_id}) não encontrados."); return

           # Verifica estoque ANTES de adicionar
           estoque_disponivel = product_data.get('stock', 0)
           quantidade_no_carrinho = sum(item['quantidade'] for item in self.carrinho_local if item['produto_id'] == product_id)

           if estoque_disponivel < quantidade_no_carrinho + quantity:
               QMessageBox.warning(self, "Estoque Insuficiente", f"Estoque de {product_name}: {estoque_disponivel}.\nNo carrinho: {quantidade_no_carrinho}. Pedido: {quantity}.")
               return

           price = product_data.get('price', 0.0)
           # Atualiza ou adiciona item no carrinho local
           item_exists = False
           for item in self.carrinho_local:
               if item['produto_id'] == product_id:
                   item['quantidade'] += quantity
                   item_exists = True
                   break
           if not item_exists:
               self.carrinho_local.append({
                   'produto_id': product_id, # Guarda ID para consistência
                   'produto_nome': product_name,
                   'quantidade': quantity,
                   'preco_unit': price
               })

           self.atualizar_carrinho_local()
           self.quantidade_spinbox.setValue(1) # Reseta quantidade

       def atualizar_carrinho_local(self):
           self.carrinho_table.setRowCount(0) # Limpa tabela
           total_venda = 0.0
           for i, item in enumerate(self.carrinho_local):
               self.carrinho_table.insertRow(i)
               subtotal = item['quantidade'] * item['preco_unit']
               total_venda += subtotal

               self.carrinho_table.setItem(i, 0, QTableWidgetItem(item['produto_nome']))
               self.carrinho_table.setItem(i, 1, QTableWidgetItem(str(item['quantidade'])))
               self.carrinho_table.setItem(i, 2, QTableWidgetItem(f"R$ {item['preco_unit']:.2f}"))

               subtotal_item = QTableWidgetItem(f"R$ {subtotal:.2f}")
               subtotal_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
               self.carrinho_table.setItem(i, 3, subtotal_item)

           # self.carrinho_table.resizeColumnsToContents() # Não necessário com ResizeMode
           self.total_label.setText(f"Total: R$ {total_venda:.2f}")

       def finalizar_venda_local(self):
           if not self.carrinho_local:
               QMessageBox.information(self, "Carrinho Vazio", "Adicione itens ao carrinho primeiro.")
               return

           total = sum(item['quantidade'] * item['preco_unit'] for item in self.carrinho_local)
           metodos_pagamento = ["Dinheiro", "Cartão Débito", "Cartão Crédito", "PIX", "Outro"]
           metodo_pagamento, ok = QInputDialog.getItem(self, "Método de Pagamento",
                                                     f"Total: R$ {total:.2f}\nSelecione o método:",
                                                     metodos_pagamento, 0, False) # editable=False

           if ok and metodo_pagamento:
               # Prepara itens para o histórico (usando nomes e preços atuais)
               itens_venda = [
                   {'produto': item['produto_nome'], 'quantidade': item['quantidade'], 'preco': item['preco_unit']}
                   for item in self.carrinho_local
               ]
               # Chama a função central da main_window para registrar
               self.main_window.registrar_venda_historico(total, metodo_pagamento, itens_venda)

               QMessageBox.information(self, "Sucesso", "Venda registrada no histórico!")
               self.carrinho_local = [] # Limpa o carrinho local
               self.atualizar_carrinho_local() # Atualiza a tabela (fica vazia) e o total
               self.update_products_combo() # Atualiza o combo (estoque pode ter mudado)
           elif ok and not metodo_pagamento: # Caso aconteça de alguma forma
               QMessageBox.warning(self, "Erro", "Método de pagamento não selecionado.")
           # else: (Se clicou Cancelar, não faz nada)
