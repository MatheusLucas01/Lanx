# src/ui/payment_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                 QMessageBox, QGridLayout, QLineEdit, QDialogButtonBox,
                                 QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDoubleValidator

class PaymentDialog(QDialog):
        def __init__(self, total_amount, parent=None):
            super().__init__(parent)
            self.selected_method = None
            self.total_amount = total_amount
            self.setWindowTitle("Confirmar Pagamento")
            self.setMinimumWidth(450)
            self.setModal(True)

            self.setStyleSheet("""
                QDialog { background-color: #f8f9fa; border-radius: 8px; }
                QLabel#totalLabel { font-size: 24px; font-weight: bold; color: #dc3545; margin-bottom: 5px; }
                QLabel#infoLabel { font-size: 16px; color: #495057; margin-bottom: 15px; }
                QPushButton#paymentButton { font-size: 14px; padding: 12px 20px; margin: 5px; border: 1px solid #ced4da; border-radius: 5px; background-color: white; min-width: 100px; }
                QPushButton#paymentButton:hover { background-color: #e9ecef; border-color: #adb5bd; }
                QPushButton#paymentButton:pressed { background-color: #dee2e6; }
                QPushButton#paymentButton:checked { background-color: #007bff; color: white; border-color: #0056b3; font-weight: bold; }
                QWidget#cashPaymentFields { margin-top: 15px; border-top: 1px solid #dee2e6; padding-top: 15px; }
                QLabel#changeLabel { font-size: 16px; font-weight: bold; color: #28a745; margin-top: 5px; }
                QLineEdit#receivedAmountInput { font-size: 14px; padding: 8px; border: 1px solid #ced4da; border-radius: 4px; }
                QDialogButtonBox QPushButton { padding: 8px 25px; font-size: 14px; border-radius: 5px; min-width: 80px;}
                QDialogButtonBox QPushButton[text="Confirmar"] { background-color: #28a745; color: white; }
                QDialogButtonBox QPushButton[text="Cancelar"] { background-color: #6c757d; color: white; }
            """)

            layout = QVBoxLayout(self); layout.setSpacing(15); layout.setContentsMargins(25, 25, 25, 25)

            total_label = QLabel(f"Total a Pagar: R$ {self.total_amount:.2f}"); total_label.setObjectName("totalLabel"); total_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(total_label)
            info_label = QLabel("Selecione o método de pagamento:"); info_label.setObjectName("infoLabel"); info_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(info_label)

            payment_methods_layout = QGridLayout(); payment_methods_layout.setSpacing(10)
            methods = ["Dinheiro", "Cartão Débito", "Cartão Crédito", "PIX"]; self.payment_buttons = {}
            positions = [(i, j) for i in range(2) for j in range(2)] # 2x2 grid
            for position, name in zip(positions, methods):
                button = QPushButton(name); button.setObjectName("paymentButton"); button.setCheckable(True)
                button.clicked.connect(lambda checked, b=button, n=name: self.on_payment_method_selected(checked, b, n))
                payment_methods_layout.addWidget(button, position[0], position[1]); self.payment_buttons[name] = button
            layout.addLayout(payment_methods_layout)

            # --- Campos para Pagamento em Dinheiro (Inicialmente Ocultos) ---
            self.cash_payment_widget = QWidget(); self.cash_payment_widget.setObjectName("cashPaymentFields")
            cash_layout = QGridLayout(self.cash_payment_widget)
            cash_layout.setContentsMargins(0, 0, 0, 0); cash_layout.setSpacing(10)

            cash_layout.addWidget(QLabel("Valor Recebido (R$):"), 0, 0)
            self.received_amount_input = QLineEdit(); self.received_amount_input.setObjectName("receivedAmountInput")
            # Validador para aceitar apenas números e vírgula/ponto decimal
            self.received_amount_input.setValidator(QDoubleValidator(0.00, 99999.99, 2))
            self.received_amount_input.setPlaceholderText("0,00")
            self.received_amount_input.textChanged.connect(self.calculate_change)
            cash_layout.addWidget(self.received_amount_input, 0, 1)

            cash_layout.addWidget(QLabel("Troco (R$):"), 1, 0)
            self.change_label = QLabel("0.00"); self.change_label.setObjectName("changeLabel")
            cash_layout.addWidget(self.change_label, 1, 1)
            layout.addWidget(self.cash_payment_widget); self.cash_payment_widget.setVisible(False)

            # --- Botões OK/Cancelar ---
            self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Confirmar")
            self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
            # Botão OK começa desabilitado até um método ser selecionado
            self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
            self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
            layout.addWidget(self.button_box)

            self.setLayout(layout)

        def on_payment_method_selected(self, checked, button, name):
            if checked:
                self.selected_method = name
                is_cash = (name == "Dinheiro")
                self.cash_payment_widget.setVisible(is_cash)
                if is_cash:
                    self.received_amount_input.setFocus(); self.received_amount_input.selectAll()
                self.calculate_change() # Recalcula troco (pode zerar se não for dinheiro)
                # Desmarca outros
                for method_name, btn in self.payment_buttons.items():
                    if btn != button: btn.setChecked(False)
                # Habilita botão OK
                self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            else:
                # Se desmarcar o botão ativo, nenhum método está selecionado
                self.selected_method = None
                self.cash_payment_widget.setVisible(False)
                self.calculate_change() # Zera troco
                # Desabilita botão OK
                self.button_box.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

        def calculate_change(self):
            if self.selected_method == "Dinheiro" and self.cash_payment_widget.isVisible():
                try:
                    received_text = self.received_amount_input.text().replace(',', '.')
                    if not received_text: received_text = "0"
                    received_amount = float(received_text)

                    if received_amount >= self.total_amount:
                        change = received_amount - self.total_amount
                        self.change_label.setText(f"{change:.2f}")
                        self.change_label.setStyleSheet("color: #28a745; font-size: 16px; font-weight: bold;") # Verde
                    else:
                        change = self.total_amount - received_amount
                        self.change_label.setText(f"Faltam R$ {change:.2f}")
                        self.change_label.setStyleSheet("color: #dc3545; font-size: 14px; font-weight: bold;") # Vermelho
                except ValueError:
                    self.change_label.setText("Valor inválido")
                    self.change_label.setStyleSheet("color: #ffc107; font-size: 14px; font-weight: bold;") # Amarelo
                except Exception as e:
                    print(f"Erro cálculo troco: {e}"); self.change_label.setText("Erro")
                    self.change_label.setStyleSheet("color: #dc3545; font-size: 14px; font-weight: bold;")
            else:
                self.change_label.setText("0.00")
                self.change_label.setStyleSheet("color: #28a745; font-size: 16px; font-weight: bold;")

        def accept(self):
            # Validação já feita em on_payment_method_selected para habilitar o botão
            # Validação extra para o caso de Dinheiro e valor insuficiente
            if self.selected_method == "Dinheiro":
                try:
                    received_text = self.received_amount_input.text().replace(',', '.')
                    if not received_text: received_text = "0"
                    received_amount = float(received_text)

                    if received_amount < self.total_amount:
                        QMessageBox.warning(self, "Valor Insuficiente",
                                            f"O valor recebido (R$ {received_amount:.2f}) é menor que o total a pagar (R$ {self.total_amount:.2f}).")
                        self.received_amount_input.setFocus(); self.received_amount_input.selectAll()
                        return # Não fecha o diálogo
                except ValueError:
                     QMessageBox.warning(self, "Valor Inválido", "O valor recebido não é um número válido.")
                     self.received_amount_input.setFocus(); self.received_amount_input.selectAll()
                     return # Não fecha
                except Exception as e:
                     print(f"Erro validação accept: {e}"); QMessageBox.critical(self, "Erro", "Erro ao validar valor recebido.")
                     return

            super().accept() # Fecha o diálogo com status OK

        def get_selected_method(self):
            return self.selected_method