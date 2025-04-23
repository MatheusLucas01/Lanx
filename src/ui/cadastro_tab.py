# src/ui/cadastro_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
                                QMessageBox, QFrame, QGridLayout, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class CadastroTab(QWidget):
       def __init__(self, main_window):
           super().__init__()
           self.main_window = main_window # Para acessar self.main_window.products, etc.
           self.selected_product_id = None
           layout = QVBoxLayout(self)
           layout.setSpacing(15)

           # --- Formulário ---
           form_frame = QFrame()
           form_frame.setFrameShape(QFrame.Shape.StyledPanel)
           form_layout = QGridLayout(form_frame)
           form_layout.setSpacing(10)
           form_layout.addWidget(QLabel("Nome:*"), 0, 0)
           self.name_input = QLineEdit()
           form_layout.addWidget(self.name_input, 0, 1)
           form_layout.addWidget(QLabel("Descrição:"), 1, 0)
           self.description_input = QLineEdit()
           form_layout.addWidget(self.description_input, 1, 1)
           form_layout.addWidget(QLabel("Preço:*"), 0, 2)
           self.price_input = QDoubleSpinBox()
           self.price_input.setDecimals(2); self.price_input.setMinimum(0.0); self.price_input.setMaximum(99999.99); self.price_input.setPrefix("R$ ")
           form_layout.addWidget(self.price_input, 0, 3)
           form_layout.addWidget(QLabel("Categoria:"), 1, 2)
           self.category_combo = QComboBox()
           self.category_combo.addItems(["Lanche", "Bebida", "Sobremesa", "Outros"])
           form_layout.addWidget(self.category_combo, 1, 3)
           form_layout.addWidget(QLabel("Estoque Inicial:*"), 2, 0)
           self.stock_input = QSpinBox()
           self.stock_input.setMinimum(0); self.stock_input.setMaximum(9999)
           form_layout.addWidget(self.stock_input, 2, 1)
           # form_layout.addWidget(QLabel("Imagem (opcional):"), 2, 2) # Simplificado, removido por ora
           # self.image_input = QLineEdit()
           # form_layout.addWidget(self.image_input, 2, 3)
           layout.addWidget(form_frame)

           # --- Botões ---
           button_layout = QHBoxLayout()
           button_style = """ QPushButton { padding: 8px 15px; font-size: 14px; border-radius: 4px; } QPushButton:hover { background-color: #e0e0e0; } """
           self.new_button = QPushButton("Novo"); self.new_button.setStyleSheet(button_style); self.new_button.clicked.connect(self.clear_form)
           button_layout.addWidget(self.new_button)
           self.save_button = QPushButton("Salvar"); self.save_button.setStyleSheet(button_style + "QPushButton { background-color: #28a745; color: white; } QPushButton:hover { background-color: #218838; }"); self.save_button.clicked.connect(self.save_product)
           button_layout.addWidget(self.save_button)
           self.delete_button = QPushButton("Excluir"); self.delete_button.setStyleSheet(button_style + "QPushButton { background-color: #dc3545; color: white; } QPushButton:hover { background-color: #c82333; }"); self.delete_button.setEnabled(False); self.delete_button.clicked.connect(self.delete_product)
           button_layout.addWidget(self.delete_button)
           button_layout.addStretch()
           layout.addLayout(button_layout)

           # --- Pesquisa e Tabela ---
           search_layout = QHBoxLayout()
           search_layout.addWidget(QLabel("Pesquisar:"))
           self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Digite nome ou categoria..."); self.search_input.textChanged.connect(self.filter_table)
           search_layout.addWidget(self.search_input)
           layout.addLayout(search_layout)
           self.products_table = QTableWidget()
           self.products_table.setColumnCount(6) # ID (oculto), Nome, Preço, Categoria, Estoque, Descrição
           self.products_table.setHorizontalHeaderLabels(["ID", "Nome", "Preço", "Categoria", "Estoque", "Descrição"])
           self.products_table.setColumnHidden(0, True)
           self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
           self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
           self.products_table.verticalHeader().setVisible(False)
           self.products_table.setAlternatingRowColors(True)
           self.products_table.itemSelectionChanged.connect(self.on_table_item_selection_changed)
           layout.addWidget(self.products_table)

           self.load_products_to_table()

       def load_products_to_table(self):
           # Acessa a lista de produtos através da referência à janela principal
           if not hasattr(self.main_window, 'products'):
               print("ERRO [CadastroTab]: main_window não tem atributo 'products'")
               return

           search_term = self.search_input.text().lower()
           self.products_table.setRowCount(0)
           products_to_display = [
               p for p in self.main_window.products
               if not search_term or search_term in p.get('name', '').lower() or search_term in p.get('category', '').lower()
           ]
           for row, product in enumerate(products_to_display):
               self.products_table.insertRow(row)
               id_item = QTableWidgetItem(str(product.get('id', '')))
               id_item.setData(Qt.ItemDataRole.UserRole, product.get('id')) # Armazena ID
               self.products_table.setItem(row, 0, id_item)
               self.products_table.setItem(row, 1, QTableWidgetItem(product.get('name', 'N/A')))
               self.products_table.setItem(row, 2, QTableWidgetItem(f"R$ {product.get('price', 0.0):.2f}"))
               self.products_table.setItem(row, 3, QTableWidgetItem(product.get('category', 'N/A')))
               self.products_table.setItem(row, 4, QTableWidgetItem(str(product.get('stock', 0))))
               self.products_table.setItem(row, 5, QTableWidgetItem(product.get('description', '')))
           self.products_table.resizeColumnsToContents()

       def on_table_item_selection_changed(self):
           selected_items = self.products_table.selectedItems()
           if not selected_items:
               self.clear_form(); self.delete_button.setEnabled(False); return

           selected_row = self.products_table.currentRow()
           if selected_row < 0 or selected_row >= self.products_table.rowCount():
                self.clear_form(); self.delete_button.setEnabled(False); return

           id_item = self.products_table.item(selected_row, 0)
           if id_item is None:
                self.clear_form(); self.delete_button.setEnabled(False); return

           product_id = id_item.data(Qt.ItemDataRole.UserRole) # Pega ID armazenado
           if product_id is None:
               self.clear_form(); self.delete_button.setEnabled(False); return

           self.selected_product_id = product_id
           # Encontra o produto na lista da main_window
           product_data = next((p for p in self.main_window.products if p.get('id') == product_id), None)
           if product_data:
               self.name_input.setText(product_data.get('name', ''))
               self.description_input.setText(product_data.get('description', ''))
               self.price_input.setValue(product_data.get('price', 0.0))
               self.category_combo.setCurrentText(product_data.get('category', 'Outros'))
               self.stock_input.setValue(product_data.get('stock', 0))
               self.stock_input.setEnabled(False) # Não edita estoque aqui
               # self.image_input.setText(product_data.get('image', '')) # Removido
               self.delete_button.setEnabled(True)
           else:
               print(f"AVISO [CadastroTab]: Produto com ID {product_id} não encontrado na lista principal.")
               self.clear_form()

       def save_product(self):
           name = self.name_input.text().strip(); description = self.description_input.text().strip()
           price = self.price_input.value(); category = self.category_combo.currentText()
           stock = self.stock_input.value(); # image = self.image_input.text().strip() # Removido

           if not name or price <= 0:
               QMessageBox.warning(self, "Campos Obrigatórios", "Nome e Preço (maior que zero) são obrigatórios."); return

           product_data = {'name': name, 'description': description, 'price': price, 'category': category, 'stock': stock } #'image': image,

           if self.selected_product_id is None: # Novo produto
               product_data['id'] = self.main_window.get_next_product_id() # Pega ID da main_window
               product_data['stock'] = stock # Usa o estoque inicial digitado
               self.main_window.products.append(product_data)
               QMessageBox.information(self, "Sucesso", f"Produto '{name}' adicionado!")
           else: # Editando produto existente
               product_data['id'] = self.selected_product_id
               found = False
               for i, p in enumerate(self.main_window.products):
                   if p.get('id') == self.selected_product_id:
                       product_data['stock'] = p['stock'] # *** IMPORTANTE: Mantém o estoque atual ao editar ***
                       self.main_window.products[i] = product_data
                       found = True
                       break
               if found:
                   QMessageBox.information(self, "Sucesso", f"Produto '{name}' atualizado!")
               else:
                   QMessageBox.critical(self, "Erro", "Erro ao encontrar o produto para atualizar."); return

           self.main_window.save_products_to_file() # Salva através da main_window
           self.load_products_to_table()
           self.clear_form()

       def clear_form(self):
           self.selected_product_id = None; self.name_input.clear(); self.description_input.clear()
           self.price_input.setValue(0.0); self.category_combo.setCurrentIndex(0)
           self.stock_input.setValue(0); self.stock_input.setEnabled(True) # Habilita estoque para novos produtos
           # self.image_input.clear() # Removido
           self.products_table.clearSelection(); self.delete_button.setEnabled(False); self.name_input.setFocus()

       def delete_product(self):
           if self.selected_product_id is None: return

           product_to_delete = next((p for p in self.main_window.products if p.get('id') == self.selected_product_id), None)
           if not product_to_delete:
               QMessageBox.critical(self, "Erro", "Produto não encontrado para exclusão."); self.clear_form(); return

           reply = QMessageBox.question(self, 'Confirmar Exclusão', f"Excluir '{product_to_delete.get('name', 'N/A')}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
           if reply == QMessageBox.StandardButton.Yes:
               self.main_window.products.remove(product_to_delete)
               self.main_window.save_products_to_file()
               QMessageBox.information(self, "Sucesso", f"Produto '{product_to_delete.get('name', 'N/A')}' excluído.")
               self.load_products_to_table()
               self.clear_form()

       def filter_table(self):
           self.load_products_to_table() # Apenas recarrega a tabela com o filtro atual