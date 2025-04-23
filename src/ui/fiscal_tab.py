# src/ui/fiscal_tab.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem,
                                QSizePolicy)
from PyQt6.QtCore import Qt

class FiscalTab(QWidget):
       def __init__(self): # Não precisa de main_window por enquanto
           super().__init__()
           layout = QVBoxLayout(self)

           title_label = QLabel("Módulo Fiscal (Simulado)")
           title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
           layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

           gerar_nfe_btn = QPushButton("Gerar Nota Fiscal Eletrônica (NF-e) - Simulado")
           gerar_nfce_btn = QPushButton("Gerar Nota Fiscal de Consumidor Eletrônica (NFC-e) - Simulado")
           consultar_impostos_btn = QPushButton("Consultar Impostos - Simulado")

           # Adicionar ações (placeholders) se os botões forem clicados
           gerar_nfe_btn.clicked.connect(lambda: self.show_placeholder_message("NF-e"))
           gerar_nfce_btn.clicked.connect(lambda: self.show_placeholder_message("NFC-e"))
           consultar_impostos_btn.clicked.connect(lambda: self.show_placeholder_message("Consulta de Impostos"))

           layout.addWidget(gerar_nfe_btn)
           layout.addWidget(gerar_nfce_btn)
           layout.addWidget(consultar_impostos_btn)

           # Adiciona um espaçador para empurrar os botões para cima
           layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

       def show_placeholder_message(self, feature_name):
           from PyQt6.QtWidgets import QMessageBox # Import local para evitar dependência circular se usado em outro lugar
           QMessageBox.information(self, "Funcionalidade Simulada",
                                   f"A funcionalidade '{feature_name}' ainda não foi implementada.\n"
                                   "Aqui ocorreria a integração com o sistema fiscal.")