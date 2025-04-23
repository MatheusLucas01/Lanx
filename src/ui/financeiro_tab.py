 # src/ui/financeiro_tab.py
import os
import json
from datetime import datetime, timedelta
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                                 QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
                                 QFrame, QDateEdit, QFileDialog, QHeaderView)
from PyQt6.QtCore import Qt, QDateTime, QDate, QTime
from PyQt6.QtGui import QFont

class FinanceiroTab(QWidget):
        def __init__(self, main_window):
            super().__init__()
            self.main_window = main_window
            self.filtered_sales_data = [] # Armazena os dados filtrados para exportação
            self.current_report_total = 0.0 # Armazena o total do último relatório gerado

            layout = QVBoxLayout(self)
            layout.setSpacing(15)
            layout.setContentsMargins(15, 15, 15, 15) # Margens menores

            title_label = QLabel("Relatório de Vendas")
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #343a40;")
            layout.addWidget(title_label)

            # --- Filtros ---
            filter_frame = QFrame()
            # filter_frame.setFrameShape(QFrame.Shape.StyledPanel) # Opcional: borda
            filter_layout = QHBoxLayout(filter_frame)
            filter_layout.setContentsMargins(0, 5, 0, 5)

            filter_layout.addWidget(QLabel("Período:"))
            self.period_combo = QComboBox()
            self.period_combo.addItems(["Hoje", "Ontem", "Esta Semana", "Este Mês", "Período Específico"])
            self.period_combo.currentIndexChanged.connect(self.toggle_date_edits)
            filter_layout.addWidget(self.period_combo)

            self.start_label = QLabel(" De:")
            self.start_label.setVisible(False)
            self.start_date_edit = QDateEdit(QDate.currentDate())
            self.start_date_edit.setCalendarPopup(True); self.start_date_edit.setDisplayFormat("dd/MM/yyyy")
            self.start_date_edit.setVisible(False); self.start_date_edit.setFixedWidth(120)

            self.end_label = QLabel(" Até:")
            self.end_label.setVisible(False)
            self.end_date_edit = QDateEdit(QDate.currentDate())
            self.end_date_edit.setCalendarPopup(True); self.end_date_edit.setDisplayFormat("dd/MM/yyyy")
            self.end_date_edit.setVisible(False); self.end_date_edit.setFixedWidth(120)

            filter_layout.addWidget(self.start_label); filter_layout.addWidget(self.start_date_edit)
            filter_layout.addWidget(self.end_label); filter_layout.addWidget(self.end_date_edit)

            self.generate_button = QPushButton("Gerar Relatório")
            self.generate_button.setStyleSheet("padding: 5px 10px;")
            self.generate_button.clicked.connect(self.generate_report)
            filter_layout.addWidget(self.generate_button)

            self.export_button = QPushButton("Exportar Excel")
            self.export_button.setStyleSheet("padding: 5px 10px; background-color: #196F3D; color: white;")
            self.export_button.clicked.connect(self.export_to_excel)
            self.export_button.setEnabled(False) # Começa desabilitado
            filter_layout.addWidget(self.export_button)

            filter_layout.addStretch()
            layout.addWidget(filter_frame)

            # --- Tabela de Vendas ---
            self.sales_report_table = QTableWidget()
            self.sales_report_table.setColumnCount(5)
            self.sales_report_table.setHorizontalHeaderLabels(["Data/Hora", "Produtos Vendidos", "Qtd Itens", "Método Pgto", "Total (R$)"])
            self.sales_report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.sales_report_table.setAlternatingRowColors(True)
            self.sales_report_table.verticalHeader().setVisible(False)
            self.sales_report_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            self.sales_report_table.setStyleSheet("""
                QTableWidget { border: 1px solid #ccc; }
                QHeaderView::section { background-color: #eee; padding: 4px; border: 1px solid #ccc; font-weight: bold; }
            """)
            # Ajuste de tamanho das colunas
            header = self.sales_report_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Data/Hora
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Produtos
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Qtd
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Pgto
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Total
            layout.addWidget(self.sales_report_table, 1) # Ocupa espaço vertical

            # --- Totais do Relatório ---
            totals_layout = QHBoxLayout()
            totals_layout.addStretch()
            totals_layout.addWidget(QLabel("Total Vendas no Período:"))
            self.total_periodo_label = QLabel("R$ 0.00")
            self.total_periodo_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #28a745;")
            totals_layout.addWidget(self.total_periodo_label)
            layout.addLayout(totals_layout)

            self.toggle_date_edits(0) # Ajusta visibilidade inicial dos seletores de data

        def toggle_date_edits(self, index):
            show_dates = (self.period_combo.currentText() == "Período Específico")
            self.start_label.setVisible(show_dates)
            self.start_date_edit.setVisible(show_dates)
            self.end_label.setVisible(show_dates)
            self.end_date_edit.setVisible(show_dates)

        def get_date_range(self):
            """Retorna a data/hora inicial e final (QDateTime) com base na seleção."""
            period = self.period_combo.currentText()
            today = QDate.currentDate()
            start_date = today
            end_date = today

            if period == "Hoje":
                pass
            elif period == "Ontem":
                start_date = today.addDays(-1); end_date = start_date
            elif period == "Esta Semana":
                # Semana começa na Segunda (ISO 8601 week date system)
                start_date = today.addDays(-(today.dayOfWeek() - 1))
                end_date = today
            elif period == "Este Mês":
                start_date = QDate(today.year(), today.month(), 1)
                end_date = today
            elif period == "Período Específico":
                start_date = self.start_date_edit.date()
                end_date = self.end_date_edit.date()
                if start_date > end_date:
                    QMessageBox.warning(self, "Datas Inválidas", "A data inicial não pode ser posterior à data final.")
                    return None, None

            # Cria QDateTime com início e fim do dia
            start_dt = QDateTime(start_date, QTime(0, 0, 0, 0))
            end_dt = QDateTime(end_date, QTime(23, 59, 59, 999))

            return start_dt, end_dt

        def generate_report(self):
            """Lê vendas.json, filtra, preenche a tabela e loga erros detalhadamente."""
            print("--- Iniciando generate_report ---")
            self.sales_report_table.setRowCount(0)
            total_periodo = 0.0
            self.filtered_sales_data = [] # Limpa dados anteriores
            self.export_button.setEnabled(False)

            print("--- Obtendo intervalo de datas...")
            start_dt, end_dt = self.get_date_range()
            if start_dt is None or end_dt is None:
                print("--- Erro: Intervalo de datas inválido.")
                return

            print(f"--- Intervalo: {start_dt.toString(Qt.DateFormat.ISODate)} a {end_dt.toString(Qt.DateFormat.ISODate)}")
            sales_file = self.main_window.SALES_FILE
            print(f"--- Lendo arquivo: {sales_file}")

            try:
                if os.path.exists(sales_file):
                    with open(sales_file, "r", encoding='utf-8') as f:
                        sales_data = json.load(f)
                    print(f"--- Arquivo lido. {len(sales_data)} registros encontrados.")

                    # --- Filtragem ---
                    print("--- Iniciando filtragem...")
                    for sale_index, sale in enumerate(sales_data):
                        try:
                            if 'data' not in sale: continue
                            sale_dt_str = sale['data']
                            if not isinstance(sale_dt_str, str): continue

                            sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODate)
                            if not sale_dt.isValid(): sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODateWithMs)
                            if not sale_dt.isValid(): continue # Pula se data inválida

                            if start_dt <= sale_dt <= end_dt:
                                if 'total' not in sale or not isinstance(sale.get('total'), (int, float)):
                                    sale['total'] = 0.0 # Garante que total existe e é numérico
                                self.filtered_sales_data.append(sale)

                        except Exception as e_filter:
                            print(f"--- ERRO ao processar registro {sale_index} na filtragem: {e_filter}\nRegistro: {sale}")

                    print(f"--- Filtragem concluída. {len(self.filtered_sales_data)} registros no período.")

                    # --- Ordenação (mais recentes primeiro) ---
                    if self.filtered_sales_data:
                        print("--- Iniciando ordenação...")
                        try:
                            self.filtered_sales_data.sort(
                                key=lambda x: QDateTime.fromString(x.get('data', ''), Qt.DateFormat.ISODate) if QDateTime.fromString(x.get('data', ''), Qt.DateFormat.ISODate).isValid() else QDateTime.fromString(x.get('data', ''), Qt.DateFormat.ISODateWithMs),
                                reverse=True
                            )
                            print("--- Ordenação concluída.")
                        except Exception as e_sort:
                            print(f"--- ERRO durante a ordenação: {e_sort}. Tabela não ordenada.")

                    # --- População da Tabela ---
                    print("--- Iniciando população da tabela...")
                    for row, sale in enumerate(self.filtered_sales_data):
                        try:
                            self.sales_report_table.insertRow(row)

                            sale_dt_display_str = sale.get('data', 'Inválida')
                            sale_dt_display = QDateTime.fromString(sale_dt_display_str, Qt.DateFormat.ISODate)
                            if not sale_dt_display.isValid(): sale_dt_display = QDateTime.fromString(sale_dt_display_str, Qt.DateFormat.ISODateWithMs)
                            display_date = sale_dt_display.toString("dd/MM/yyyy HH:mm:ss") if sale_dt_display.isValid() else sale_dt_display_str
                            self.sales_report_table.setItem(row, 0, QTableWidgetItem(display_date))

                            items_list = sale.get('itens', [])
                            if not isinstance(items_list, list): items_list = []
                            item_names = [f"{item.get('produto','N/A')} ({item.get('quantidade', 0)})" for item in items_list]
                            self.sales_report_table.setItem(row, 1, QTableWidgetItem(", ".join(item_names)))

                            total_items_count = sum(item.get('quantidade', 0) for item in items_list if isinstance(item.get('quantidade'), int))
                            self.sales_report_table.setItem(row, 2, QTableWidgetItem(str(total_items_count)))

                            self.sales_report_table.setItem(row, 3, QTableWidgetItem(sale.get('metodo_pagamento', 'N/A')))

                            total_sale = sale.get('total', 0.0)
                            total_item = QTableWidgetItem(f"{total_sale:.2f}")
                            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                            self.sales_report_table.setItem(row, 4, total_item)

                            total_periodo += total_sale

                        except Exception as e_table:
                            print(f"--- ERRO ao popular linha {row} da tabela: {e_table}\nRegistro: {sale}")
                            # Adiciona linha de erro na tabela
                            try:
                                self.sales_report_table.insertRow(row)
                                error_item = QTableWidgetItem(f"Erro ao carregar dados da venda: {e_table}")
                                error_item.setForeground(Qt.GlobalColor.red)
                                self.sales_report_table.setItem(row, 0, error_item)
                                self.sales_report_table.setSpan(row, 0, 1, self.sales_report_table.columnCount())
                            except Exception as e_table_err: print(f"--- ERRO ao adicionar linha de erro: {e_table_err}")

                    print(f"--- População da tabela concluída. {self.sales_report_table.rowCount()} linhas.")

                else:
                    print(f"--- Arquivo {sales_file} não encontrado.")
                    QMessageBox.information(self, "Arquivo Não Encontrado", f"O arquivo de histórico de vendas ({os.path.basename(sales_file)}) não foi encontrado.")

            except json.JSONDecodeError as e_json:
                print(f"--- ERRO CRÍTICO: Falha ao decodificar JSON de {sales_file}: {e_json}")
                QMessageBox.critical(self, "Erro de Arquivo", f"O arquivo de vendas ({os.path.basename(sales_file)}) parece corrompido.\n\nDetalhe: {e_json}")
            except Exception as e_main:
                print(f"--- ERRO CRÍTICO INESPERADO: {e_main}")
                QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro inesperado ao gerar o relatório:\n{e_main}")

            # --- Finalização ---
            # self.sales_report_table.resizeColumnsToContents() # Já tratado com ResizeMode
            print("--- Atualizando total e botão exportar...")
            self.total_periodo_label.setText(f"R$ {total_periodo:.2f}")
            self.current_report_total = total_periodo # Armazena para exportação
            self.export_button.setEnabled(len(self.filtered_sales_data) > 0)
            print("--- Fim de generate_report ---")

        def load_data(self):
            """Método chamado quando a aba se torna visível."""
            print("Carregando dados da Aba Financeiro...")
            self.generate_report() # Gera o relatório com os filtros padrões

        def export_to_excel(self):
            """Exporta os dados do relatório atual (self.filtered_sales_data) para Excel."""
            if not self.filtered_sales_data:
                QMessageBox.information(self, "Sem Dados", "Gere um relatório com dados antes de exportar.")
                return

            print("--- Preparando dados para exportação Excel...")
            data_for_export = []
            for sale in self.filtered_sales_data:
                # Re-parsear data para garantir formato consistente na exportação
                sale_dt_str = sale.get('data', '')
                sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODate)
                if not sale_dt.isValid(): sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODateWithMs)
                # Exportar como string formatada ou datetime object (pandas lida bem com datetime)
                # date_obj = sale_dt.toPython() if sale_dt.isValid() else None # Opção 1: objeto datetime
                date_str_excel = sale_dt.toString("dd/MM/yyyy HH:mm:ss") if sale_dt.isValid() else sale_dt_str # Opção 2: string

                items_list = sale.get('itens', [])
                items_str = ", ".join([f"{item.get('produto','N/A')} ({item.get('quantidade',0)})" for item in items_list])
                qtd_total = sum(item.get('quantidade', 0) for item in items_list if isinstance(item.get('quantidade'), int))

                data_for_export.append({
                    "Data/Hora": date_str_excel, # Usando string formatada
                    "Produtos Vendidos": items_str,
                    "Qtd Itens": qtd_total,
                    "Método Pgto": sale.get('metodo_pagamento', 'N/A'),
                    # Garantir que o total é numérico para o pandas
                    "Total (R$)": float(sale.get('total', 0.0))
                })

            try:
                df = pd.DataFrame(data_for_export)
                print(f"--- DataFrame criado com {len(df)} linhas.")

                # --- Adiciona linha de Total ---
                # Calcula o total a partir do DataFrame para garantir consistência
                total_do_periodo_df = df['Total (R$)'].sum()
                print(f"--- Total calculado pelo DataFrame: R$ {total_do_periodo_df:.2f} (Comparar com self.current_report_total: {self.current_report_total:.2f})")

                # Cria linha de espaço e linha de total
                spacer_row = pd.DataFrame([{}], columns=df.columns) # Linha vazia
                total_row_data = {col: [""] for col in df.columns} # Preenche com vazio
                total_row_data["Produtos Vendidos"] = ["TOTAL DO PERÍODO:"] # Texto na coluna de produtos
                total_row_data["Total (R$)"] = [total_do_periodo_df]     # Valor total
                total_row = pd.DataFrame(total_row_data, columns=df.columns)

                # Concatena
                df_final = pd.concat([df, spacer_row, total_row], ignore_index=True)
                print("--- Linha de total adicionada ao DataFrame.")

            except ImportError:
                 QMessageBox.critical(self, "Erro de Dependência", "A biblioteca 'pandas' é necessária para exportar.\nInstale com: pip install pandas")
                 return
            except Exception as e_df:
                QMessageBox.critical(self, "Erro ao Preparar Dados", f"Erro ao criar DataFrame para exportação:\n{e_df}")
                return

            # --- Salva no Excel ---
            print("--- Solicitando local para salvar o arquivo Excel...")
            default_filename = f"Relatorio_Vendas_{QDate.currentDate().toString('yyyyMMdd')}.xlsx"
            # Tenta salvar na pasta Downloads, se não existir, salva no home do usuário
            download_path = os.path.join(os.path.expanduser("~"), "Downloads")
            if not os.path.exists(download_path): download_path = os.path.expanduser("~")
            save_dir = os.path.join(download_path) # Diretório onde salvar

            filePath, _ = QFileDialog.getSaveFileName(
                self, "Salvar Relatório Excel", os.path.join(save_dir, default_filename),
                "Arquivos Excel (*.xlsx);;Todos os Arquivos (*)"
            )

            if filePath:
                if not filePath.lower().endswith('.xlsx'): filePath += '.xlsx'
                try:
                    print(f"--- Salvando DataFrame em: {filePath}")
                    # Salva o DataFrame final (com linha de total)
                    df_final.to_excel(filePath, index=False, sheet_name="RelatorioVendas")
                    QMessageBox.information(self, "Exportação Concluída", f"Relatório salvo com sucesso em:\n{filePath}")
                    print("--- Exportação Excel concluída com sucesso.")
                except ImportError:
                     QMessageBox.critical(self, "Erro de Dependência", "A biblioteca 'openpyxl' é necessária para salvar em .xlsx.\nInstale com: pip install openpyxl")
                     print("--- ERRO: Dependência 'openpyxl' não encontrada.")
                except Exception as e_save:
                    QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o arquivo Excel:\n{e_save}\n\nVerifique permissões ou se o arquivo está aberto.")
                    print(f"--- ERRO ao salvar Excel: {e_save}")
            else:
                print("--- Exportação Excel cancelada pelo usuário.")
