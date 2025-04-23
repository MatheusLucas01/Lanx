# src/ui/estoque_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget,
                                QTableWidgetItem, QMessageBox, QInputDialog, QSpacerItem,
                                QSizePolicy, QHeaderView)
from PyQt6.QtCore import Qt

class EstoqueTab(QWidget):
       def __init__(self, main_window):
           super().__init__()
           self.main_window = main_window # Para acessar self.main_window.products, etc.
           layout = QVBoxLayout(self)

           title_label = QLabel("Gerenciamento de Estoque")
           title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
           layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

           self.estoque_table = QTableWidget()
           self.estoque_table.setColumnCount(3) # Produto, Quantidade Atual, Ação
           self.estoque_table.setHorizontalHeaderLabels(["Produto", "Quantidade Atual", "Ações"])
           self.estoque_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
           self.estoque_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
           self.estoque_table.verticalHeader().setVisible(False)
           self.estoque_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Nome do produto estica
           self.estoque_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
           self.estoque_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
           self.estoque_table.setAlternatingRowColors(True)
           layout.addWidget(self.estoque_table)

           self.load_estoque() # Carrega dados iniciais

           layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

       def load_estoque(self):
           print("DEBUG [EstoqueTab]: Carregando estoque...")
           self.estoque_table.setRowCount(0)
           # Ordena os produtos por nome para exibição na tabela
           sorted_products = sorted(self.main_window.products, key=lambda p: p.get('name', ''))

           for row, product in enumerate(sorted_products):
               self.estoque_table.insertRow(row)
               product_name = product.get('name', 'N/A')
               stock_value = product.get('stock', 0)
               product_id = product.get('id') # Precisamos do ID para o diálogo

               self.estoque_table.setItem(row, 0, QTableWidgetItem(product_name))
               # Alinha a quantidade à direita para melhor visualização
               stock_item = QTableWidgetItem(str(stock_value))
               stock_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
               self.estoque_table.setItem(row, 1, stock_item)

               # Botão de Ajuste
               adjust_button = QPushButton("Ajustar Estoque")
               # Passa o ID e nome para a função lambda
               adjust_button.clicked.connect(lambda checked, p_id=product_id, p_name=product_name: self.show_adjust_dialog(p_id, p_name))
               self.estoque_table.setCellWidget(row, 2, adjust_button)

           # self.estoque_table.resizeColumnsToContents() # Não é mais necessário com setSectionResizeMode

       def show_adjust_dialog(self, product_id, product_name):
           # Encontra o produto na lista principal usando o ID
           product = next((p for p in self.main_window.products if p.get('id') == product_id), None)
           if not product:
               QMessageBox.warning(self, "Erro", f"Produto com ID {product_id} não encontrado.")
               return

           current_stock = product.get('stock', 0)
           nova_qtd, ok = QInputDialog.getInt(self, "Ajustar Estoque",
                                            f"Nova quantidade para '{product_name}':\n(Atual: {current_stock})",
                                            current_stock, 0, 99999) # Valor inicial, min, max

           if ok: # Se o usuário clicou em OK
               found = False
               for i, p in enumerate(self.main_window.products):
                    if p.get('id') == product_id:
                        self.main_window.products[i]['stock'] = nova_qtd
                        found = True
                        break
               if found:
                   self.main_window.save_products_to_file() # Salva a alteração
                   self.load_estoque() # Recarrega a tabela
                   QMessageBox.information(self, "Sucesso", f"Estoque de '{product_name}' ajustado para {nova_qtd}.")
                   # Informa a main_window para atualizar o POS se necessário
                   if hasattr(self.main_window, 'update_pos_shortcuts'):
                       self.main_window.update_pos_shortcuts()
               else:
                    QMessageBox.critical(self, "Erro", "Erro ao encontrar o produto para atualizar o estoque após o diálogo.")