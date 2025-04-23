 # src/ui/pos_interface.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                 QTableWidget, QTableWidgetItem, QMessageBox, QDialog,
                                 QFrame, QGridLayout, QHeaderView, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

    # Import relativo do diálogo de pagamento que está na mesma pasta 'ui'
from .payment_dialog import PaymentDialog

class POSInterface(QWidget):
        def __init__(self, main_window, products_data):
            super().__init__()
            self.main_window = main_window # Para registrar venda, acessar produtos, etc.
            self.products_list = products_data # Recebe a lista de produtos carregada
            self.current_sale_items = [] # Itens no carrinho atual do POS
            self.last_highlighted_row = -1 # Para destacar a última linha adicionada

            # self.setWindowTitle("Ponto de Venda (Caixa)") # Título já está no header
            self.setStyleSheet("background-color: #f0f4f8;") # Fundo geral

            main_layout = QHBoxLayout(self); main_layout.setSpacing(15)
            main_layout.setContentsMargins(10, 10, 10, 10)

            # --- PAINEL ESQUERDO (Itens da Venda) ---
            left_panel = QFrame(); left_panel.setObjectName("posLeftPanel")
            left_panel.setStyleSheet("background-color: white; border-radius: 8px;")
            left_panel_layout = QVBoxLayout(left_panel); left_panel_layout.setContentsMargins(15, 15, 15, 15)
            sale_label = QLabel("Itens da Venda Atual"); sale_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #343a40; margin-bottom: 10px;"); left_panel_layout.addWidget(sale_label)

            self.sale_table = QTableWidget()
            self.sale_table.setColumnCount(4)
            self.sale_table.setHorizontalHeaderLabels(["Produto", "Qtd", "Preço Unit.", "Subtotal"])
            self.sale_table.verticalHeader().setVisible(False)
            self.sale_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.sale_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
            self.sale_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.sale_table.setShowGrid(False)
            self.sale_table.setAlternatingRowColors(True)
            self.sale_table.setStyleSheet("""
                QTableWidget { border: 1px solid #e0e5ec; border-radius: 5px; gridline-color: transparent; background-color: white; alternate-background-color: #f8fafd; selection-background-color: #cfe2ff; selection-color: #1a2b4d; font-size: 10pt; }
                QTableWidget::item { padding: 8px 5px; border-bottom: 1px solid #e8edf3; }
                QHeaderView::section:horizontal { background-color: #eaf2f8; padding: 8px 5px; border: none; border-bottom: 2px solid #c5d9ed; font-weight: bold; color: #34495e; font-size: 10pt; }
                QHeaderView::section:vertical { border: none; }
                QTableCornerButton::section { background-color: #eaf2f8; border: none; }
            """)
            header = self.sale_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Produto estica
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) # Qtd
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Preço Unit
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Subtotal
            left_panel_layout.addWidget(self.sale_table, 1) # Tabela ocupa espaço

            # --- Total ---
            total_frame = QFrame(); total_frame.setFrameShape(QFrame.Shape.NoFrame)
            total_layout = QHBoxLayout(total_frame); total_layout.setContentsMargins(0, 5, 0, 0) # Sem margens verticais
            total_layout.addStretch()
            total_text_label = QLabel("TOTAL:")
            total_text_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #dc3545; margin-right: 5px;")
            self.total_value_label = QLabel("R$ 0.00")
            self.total_value_label.setStyleSheet("font-size: 22pt; font-weight: bold; color: #dc3545;")
            total_layout.addWidget(total_text_label); total_layout.addWidget(self.total_value_label)
            left_panel_layout.addWidget(total_frame)

            main_layout.addWidget(left_panel, 3) # Painel esquerdo ocupa 3/5 da largura

            # --- PAINEL DIREITO (Atalhos e Ações) ---
            right_panel = QWidget()
            right_panel_layout = QVBoxLayout(right_panel); right_panel_layout.setSpacing(15); right_panel_layout.setContentsMargins(0, 0, 0, 0)

            frame_style = "QFrame { background-color: white; border-radius: 8px; border: 1px solid #dfe6f0; padding: 15px; }"

            # -- Sub-Painel de Atalhos --
            shortcuts_frame = QFrame(); shortcuts_frame.setObjectName("posShortcutsFrame")
            shortcuts_frame.setStyleSheet(frame_style)
            shortcuts_layout = QVBoxLayout(shortcuts_frame)
            shortcuts_title = QLabel("Atalhos Rápidos"); shortcuts_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #343a40; margin-bottom: 10px;"); shortcuts_layout.addWidget(shortcuts_title)

            # Grid para os botões de atalho
            self.shortcuts_grid_layout = QGridLayout(); self.shortcuts_grid_layout.setSpacing(8)
            shortcuts_layout.addLayout(self.shortcuts_grid_layout)
            shortcuts_layout.addStretch() # Empurra botões para cima
            right_panel_layout.addWidget(shortcuts_frame, 1) # Atalhos expandem verticalmente

            # -- Sub-Painel de Ações Finais --
            actions_frame = QFrame(); actions_frame.setObjectName("posActionsFrame")
            actions_frame.setStyleSheet(frame_style)
            actions_layout = QVBoxLayout(actions_frame); actions_layout.setSpacing(10)

            # Botão Remover Item (adicional, útil)
            self.remove_item_button = QPushButton("Remover Item Selecionado (Del)")
            self.remove_item_button.setStyleSheet("background-color: #ffc107; color: black; padding: 8px; font-size: 10pt; border: none; border-radius: 5px;")
            self.remove_item_button.setShortcut("Del") # Atalho Delete
            self.remove_item_button.clicked.connect(self.remove_selected_item)
            actions_layout.addWidget(self.remove_item_button)

            # Botão Finalizar
            self.finalize_button = QPushButton("Finalizar Venda (F12)"); # Mudado para F12 (Enter pode ser usado em outros lugares)
            self.finalize_button.setObjectName("primaryButton");
            self.finalize_button.setStyleSheet("QPushButton#primaryButton { background-color: #28a745; color: white; padding: 12px; font-size: 12pt; border: none; border-radius: 5px; font-weight: bold; } QPushButton#primaryButton:hover { background-color: #218838; }")
            self.finalize_button.setShortcut("F12"); self.finalize_button.clicked.connect(self.finalize_sale)
            actions_layout.addWidget(self.finalize_button)

            # Botão Cancelar
            self.cancel_button = QPushButton("Cancelar Venda (F3)")
            self.cancel_button.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; font-size: 10pt; border: none; border-radius: 5px;")
            self.cancel_button.setShortcut("F3"); self.cancel_button.clicked.connect(self.cancel_sale)
            actions_layout.addWidget(self.cancel_button)
            right_panel_layout.addWidget(actions_frame)

            main_layout.addWidget(right_panel, 2) # Painel direito ocupa 2/5 da largura

            self.populate_shortcuts() # Cria os botões de atalho

        def update_products(self, new_products_list):
            """Atualiza a lista interna de produtos e repopula atalhos."""
            print("DEBUG POS: Atualizando lista de produtos e repopulando atalhos...")
            self.products_list = new_products_list
            self.populate_shortcuts()

        def populate_shortcuts(self):
            """Cria e adiciona botões de atalho DINAMICAMENTE ao grid layout."""
            print("DEBUG POS: Populando atalhos...")

            # Limpa botões antigos
            while self.shortcuts_grid_layout.count():
                child = self.shortcuts_grid_layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()

            col_count = 3 ; row, col = 0, 0
            shortcut_button_style = """
                QPushButton { background-color: #eaf2f8; color: #34495e; border: 1px solid #c5d9ed; padding: 10px 5px; font-size: 9pt; font-weight: bold; text-align: center; border-radius: 4px; min-height: 60px; /* Altura mínima */ }
                QPushButton:hover { background-color: #d4e6f1; border-color: #aed6f1; }
                QPushButton:pressed { background-color: #aed6f1; }
                QPushButton:disabled { background-color: #e9ecef; color: #adb5bd; border-color: #dee2e6; }
            """

            # Filtra produtos válidos (dicionário, nome, estoque > 0) e ordena
            products_for_shortcuts = sorted(
                [p for p in self.products_list if isinstance(p, dict) and p.get('name') and p.get('stock', 0) > 0],
                key=lambda x: x.get('name', '')
            )
            print(f"DEBUG POS: {len(products_for_shortcuts)} produtos com estoque para atalhos.")

            if not products_for_shortcuts:
                no_stock_label = QLabel("Nenhum produto com\nestoque disponível."); no_stock_label.setAlignment(Qt.AlignmentFlag.AlignCenter); no_stock_label.setStyleSheet("color: grey; font-style: italic;"); self.shortcuts_grid_layout.addWidget(no_stock_label, 0, 0, 1, col_count); return

            for product_data in products_for_shortcuts:
                product_name = product_data.get('name', 'N/A')
                stock_count = product_data.get('stock', 0)
                price = product_data.get('price', 0.0)
                # Quebra nome longo em duas linhas (tenta no primeiro espaço)
                display_name = product_name.replace(" ", "\n", 1)

                button = QPushButton(display_name)
                button.setToolTip(f"Adicionar {product_name}\nPreço: R$ {price:.2f}\nEstoque: {stock_count}")
                button.setStyleSheet(shortcut_button_style)

                if product_name != 'N/A':
                    # Conecta usando lambda para passar o nome correto
                    button.clicked.connect(lambda checked, name=product_name: self.add_item_from_shortcut(name))
                else:
                    button.setEnabled(False) # Desabilita se nome for inválido

                self.shortcuts_grid_layout.addWidget(button, row, col)
                col += 1
                if col >= col_count: col = 0; row += 1
            print("DEBUG POS: Botões de atalho populados.")

        def add_item_from_shortcut(self, product_name):
            """Adiciona um item (qtd=1) ao carrinho a partir de um atalho."""
            print(f"DEBUG POS: Atalho clicado: {product_name}")
            quantidade = 1

            # Encontra o produto na lista ATUALIZADA
            found_product = next((p for p in self.products_list if isinstance(p, dict) and p.get('name') == product_name), None)
            if not found_product:
                 QMessageBox.warning(self, "Erro Atalho", f"Produto '{product_name}' não encontrado nos dados atuais."); return

            # Verifica estoque
            stock_disponivel = found_product.get('stock', 0)
            # Calcula quanto já está no carrinho ATUAL
            qtd_no_carrinho = 0
            item_index = -1
            for idx, item in enumerate(self.current_sale_items):
                if item['produto'] == product_name:
                    qtd_no_carrinho = item['quantidade']
                    item_index = idx
                    break

            if stock_disponivel < qtd_no_carrinho + quantidade:
                QMessageBox.warning(self, "Estoque Insuficiente", f"Estoque de {product_name}: {stock_disponivel}.\nNo carrinho: {qtd_no_carrinho}. Pedido: {quantidade}."); return

            preco_unit = found_product.get('price', 0.0)

            if item_index != -1: # Item já existe no carrinho
                self.current_sale_items[item_index]['quantidade'] += quantidade
            else: # Item novo
                self.current_sale_items.append({'produto': product_name, 'quantidade': quantidade, 'preco_unit': preco_unit})

            self.update_sale_table() # Atualiza a tabela e o total

        def remove_selected_item(self):
            """Remove o item selecionado da tabela de venda."""
            selected_rows = self.sale_table.selectionModel().selectedRows()
            if not selected_rows:
                QMessageBox.warning(self, "Nenhum Item Selecionado", "Selecione um item na tabela para remover.")
                return

            selected_row_index = selected_rows[0].row() # Pega o índice da linha
            if 0 <= selected_row_index < len(self.current_sale_items):
                removed_item = self.current_sale_items.pop(selected_row_index)
                print(f"DEBUG POS: Item removido: {removed_item['produto']}")
                self.update_sale_table() # Atualiza tabela e total
            else:
                 print(f"ERRO POS: Índice de linha selecionada ({selected_row_index}) inválido.")

        def update_sale_table(self):
            """Atualiza a tabela de itens da venda e o total."""
            # Limpa estilo da linha anterior, se houver
            if self.last_highlighted_row >= 0 and self.last_highlighted_row < self.sale_table.rowCount():
                for col in range(self.sale_table.columnCount()):
                    item = self.sale_table.item(self.last_highlighted_row, col)
                    if item: item.setBackground(QColor(Qt.GlobalColor.transparent)) # Reseta fundo

            self.sale_table.setRowCount(0) # Limpa antes de repopular
            total_carrinho = 0.0

            for row, item_data in enumerate(self.current_sale_items):
                self.sale_table.insertRow(row)
                product_name = item_data['produto']
                quantity = item_data['quantidade']
                price_unit = item_data.get('preco_unit', 0.0)
                subtotal = quantity * price_unit
                total_carrinho += subtotal

                col_produto = QTableWidgetItem(product_name)
                col_qtd = QTableWidgetItem(str(quantity)); col_qtd.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                col_preco = QTableWidgetItem(f"R${price_unit:.2f}"); col_preco.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                col_subtotal = QTableWidgetItem(f"R${subtotal:.2f}"); col_subtotal.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                self.sale_table.setItem(row, 0, col_produto)
                self.sale_table.setItem(row, 1, col_qtd)
                self.sale_table.setItem(row, 2, col_preco)
                self.sale_table.setItem(row, 3, col_subtotal)

                # Destaca a última linha adicionada
                if row == len(self.current_sale_items) - 1:
                    for col in range(self.sale_table.columnCount()):
                        table_item = self.sale_table.item(row, col)
                        if table_item: table_item.setBackground(QColor("#e6f7ff")) # Azul bem claro
                    self.last_highlighted_row = row
                else:
                     self.last_highlighted_row = -1 # Reseta se não for a última

            self.total_value_label.setText(f"R$ {total_carrinho:.2f}") # Atualiza o total

            if self.sale_table.rowCount() > 0: self.sale_table.scrollToBottom()

        def finalize_sale(self):
            """Inicia o processo de finalização da venda."""
            if not self.current_sale_items:
                QMessageBox.information(self, "Carrinho Vazio", "Adicione itens antes de finalizar."); return

            total = sum(item['preco_unit'] * item['quantidade'] for item in self.current_sale_items)

            # Usa o diálogo customizado
            payment_dialog = PaymentDialog(total, self) # Passa o total e o parent
            result = payment_dialog.exec() # Mostra o diálogo

            if result == QDialog.DialogCode.Accepted:
                metodo_pagamento = payment_dialog.get_selected_method()
                # A validação no diálogo já garante que metodo_pagamento não é None aqui

                print(f"DEBUG POS: Venda finalizada. Total: R${total:.2f}, Método: {metodo_pagamento}")
                # Prepara os itens para o histórico (nome, qtd, preço unitário da venda)
                itens_para_historico = [
                    {'produto': i['produto'], 'quantidade': i['quantidade'], 'preco': i['preco_unit']}
                    for i in self.current_sale_items
                ]
                # Chama o método central da main_window para registrar e atualizar estoque
                self.main_window.registrar_venda_historico(total, metodo_pagamento, itens_para_historico)

                QMessageBox.information(self, "Sucesso", f"Venda finalizada com sucesso!\nTotal: R${total:.2f}\nMétodo: {metodo_pagamento}")

                # Limpa o carrinho e reseta a interface do POS
                self.current_sale_items = []
                self.update_sale_table() # Limpa tabela e total
            else:
                print("DEBUG POS: Finalização da venda cancelada pelo usuário.")

        def cancel_sale(self):
            """Cancela a venda atual, limpando o carrinho."""
            if not self.current_sale_items: return # Não faz nada se carrinho vazio

            reply = QMessageBox.question(self, 'Cancelar Venda',
                                         'Tem certeza que deseja limpar todos os itens do carrinho?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No) # Padrão é não
            if reply == QMessageBox.StandardButton.Yes:
                self.current_sale_items = []
                self.update_sale_table() # Limpa a tabela e o total
                QMessageBox.information(self, "Venda Cancelada", "Os itens foram removidos do carrinho.")
