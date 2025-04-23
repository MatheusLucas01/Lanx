from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
                                QFrame, QSpacerItem, QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QDate, QDateTime
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from collections import defaultdict
import json
import os

   # Configuração global do pyqtgraph (fundo branco, eixos pretos)
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class Dashboard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        print("--- Dashboard c/ Gráficos: __init__ chamado ---")
        self.main_window = main_window # Referência à janela principal para acessar dados
        self.setStyleSheet("background-color: #f8f9fa;") # Fundo claro para o conteúdo do dashboard
        self.setMinimumSize(800, 600)

        # --- Layout Principal ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(20)

        # --- Título ---
        title_label = QLabel(f"Resumo e Desempenho - {QDate.currentDate().toString('dd/MM/yyyy')}")
        title_font = QFont(); title_font.setPointSize(18); title_font.setBold(True)
        title_label.setFont(title_font); title_label.setStyleSheet("color: #343a40; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(title_label)

        # --- Frame para os Indicadores ---
        metrics_frame = QFrame(); metrics_frame.setFrameShape(QFrame.Shape.StyledPanel)
        metrics_frame.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 8px; border: 1px solid #dee2e6; }") # Fundo branco com borda
        metrics_layout = QGridLayout(metrics_frame)
        metrics_layout.setContentsMargins(20, 20, 20, 20); metrics_layout.setSpacing(15)
        self.main_layout.addWidget(metrics_frame)

        label_font = QFont(); label_font.setPointSize(12)
        value_font = QFont(); value_font.setPointSize(16); value_font.setBold(True)

        total_sales_title = QLabel("Total de Vendas Hoje:"); total_sales_title.setFont(label_font)
        sales_count_title = QLabel("Número de Vendas Hoje:"); sales_count_title.setFont(label_font)
        avg_ticket_title = QLabel("Ticket Médio Hoje:"); avg_ticket_title.setFont(label_font)

        self.total_sales_value = QLabel("R$ 0.00"); self.total_sales_value.setFont(value_font); self.total_sales_value.setStyleSheet("color: #28a745;")
        self.sales_count_value = QLabel("0"); self.sales_count_value.setFont(value_font); self.sales_count_value.setStyleSheet("color: #17a2b8;")
        self.avg_ticket_value = QLabel("R$ 0.00"); self.avg_ticket_value.setFont(value_font); self.avg_ticket_value.setStyleSheet("color: #ffc107;")

        metrics_layout.addWidget(total_sales_title, 0, 0); metrics_layout.addWidget(self.total_sales_value, 0, 1, alignment=Qt.AlignmentFlag.AlignRight)
        metrics_layout.addWidget(sales_count_title, 1, 0); metrics_layout.addWidget(self.sales_count_value, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        metrics_layout.addWidget(avg_ticket_title, 2, 0); metrics_layout.addWidget(self.avg_ticket_value, 2, 1, alignment=Qt.AlignmentFlag.AlignRight)

        # --- Layout para os Gráficos ---
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        self.main_layout.addLayout(charts_layout, 1) # O '1' faz os gráficos expandirem

        # --- Gráfico 1: Vendas por Método de Pagamento (Hoje) ---
        self.payment_chart_widget = pg.PlotWidget()
        self.payment_chart_widget.setTitle("Vendas por Pagamento (Hoje)", color='k', size='12pt')
        self.payment_chart_widget.setLabel('left', 'Nº de Vendas', color='k')
        self.payment_chart_widget.setLabel('bottom', 'Método', color='k')
        self.payment_chart_widget.showGrid(x=False, y=True, alpha=0.3)
        self.payment_chart_widget.getAxis('bottom').setTextPen('k')
        self.payment_chart_widget.getAxis('left').setTextPen('k')
        self.payment_chart_widget.getViewBox().setBackgroundColor("#ffffff") # Fundo branco explícito
        charts_layout.addWidget(self.payment_chart_widget)

        # --- Gráfico 2: Total de Vendas por Dia (Últimos 7 Dias) ---
        self.revenue_chart_widget = pg.PlotWidget()
        self.revenue_chart_widget.setTitle("Vendas por Dia (Últimos 7 Dias)", color='k', size='12pt')
        self.revenue_chart_widget.setLabel('left', 'Total (R$)', color='k')
        self.revenue_chart_widget.setLabel('bottom', 'Data', color='k')
        self.revenue_chart_widget.showGrid(x=False, y=True, alpha=0.3)
        self.revenue_chart_widget.getAxis('bottom').setTextPen('k')
        self.revenue_chart_widget.getAxis('left').setTextPen('k')
        self.revenue_chart_widget.getViewBox().setBackgroundColor("#ffffff") # Fundo branco explícito
        charts_layout.addWidget(self.revenue_chart_widget)

        print("--- Dashboard c/ Gráficos: __init__ concluído ---")

    def update_summary(self):
           """Lê vendas.json e atualiza os indicadores e gráficos."""
           print("--- Dashboard c/ Gráficos: Iniciando update_summary ---")
           today_qdate = QDate.currentDate()
           today_str_iso = today_qdate.toString(Qt.DateFormat.ISODate)
           print(f"--- Dashboard: Data de hoje para comparação: {today_str_iso}")

           total_sales_today = 0.0
           sales_count_today = 0
           payment_counts = defaultdict(int) # Para contar métodos de pagamento de hoje
           daily_revenue = defaultdict(float) # Para somar vendas dos últimos 7 dias

           start_date_7_days = today_qdate.addDays(-6)
           date_range_str = [start_date_7_days.addDays(i).toString(Qt.DateFormat.ISODate) for i in range(7)]
           for date_str in date_range_str:
               daily_revenue[date_str] = 0.0

           print(f"--- Dashboard: Intervalo para gráfico de receita: {start_date_7_days.toString(Qt.DateFormat.ISODate)} a {today_str_iso}")

           sales_data = []
           display_total = "R$ 0.00"; display_count = "0"; display_avg_ticket = "R$ 0.00"

           try:
               # Acessa o caminho do arquivo através da instância main_window
               sales_file_path = self.main_window.SALES_FILE
               print(f"--- Dashboard: Tentando ler o arquivo: {sales_file_path}")
               if os.path.exists(sales_file_path):
                   with open(sales_file_path, "r", encoding='utf-8') as f:
                       sales_data = json.load(f)
                   print(f"--- Dashboard: Arquivo lido. {len(sales_data)} registros encontrados.")

                   for index, sale in enumerate(sales_data):
                       try:
                           if 'data' not in sale: continue
                           sale_dt_str = sale['data']
                           current_sale_total = sale.get('total', 0.0)
                           payment_method = sale.get('metodo_pagamento', 'N/A')

                           if not isinstance(current_sale_total, (int, float)): current_sale_total = 0.0

                           sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODate)
                           if not sale_dt.isValid(): sale_dt = QDateTime.fromString(sale_dt_str, Qt.DateFormat.ISODateWithMs)

                           if sale_dt.isValid():
                               sale_date_str_iso = sale_dt.date().toString(Qt.DateFormat.ISODate)

                               if sale_date_str_iso == today_str_iso:
                                   total_sales_today += current_sale_total
                                   sales_count_today += 1
                                   payment_counts[payment_method] += 1

                               if sale_date_str_iso in daily_revenue:
                                   daily_revenue[sale_date_str_iso] += current_sale_total

                       except Exception as e_inner:
                           print(f"--- ERRO (Registro {index}): Erro ao processar venda individual: {e_inner} - Registro: {sale}")

                   print("--- Dashboard: Iteração concluída.")

                   display_total = f"R$ {total_sales_today:.2f}"
                   display_count = str(sales_count_today)
                   if sales_count_today > 0:
                       avg_ticket = total_sales_today / sales_count_today
                       display_avg_ticket = f"R$ {avg_ticket:.2f}"
                   else:
                       display_avg_ticket = "R$ 0.00"

               else:
                   print(f"--- Dashboard: Arquivo {sales_file_path} não encontrado.")

           except json.JSONDecodeError as e:
               print(f"--- ERRO CRÍTICO: Falha ao decodificar JSON: {e}")
               QMessageBox.critical(self, "Erro de Arquivo", f"O arquivo de vendas ({os.path.basename(sales_file_path)}) parece corrompido.")
           except Exception as e_outer:
               print(f"--- ERRO INESPERADO em update_summary: {e_outer}")

           print(f"--- Dashboard: Atualizando labels. Total: {display_total}, Contagem: {display_count}, Ticket Médio: {display_avg_ticket}")
           self.total_sales_value.setText(display_total)
           self.sales_count_value.setText(display_count)
           self.avg_ticket_value.setText(display_avg_ticket)

           print(f"--- Dashboard: Atualizando gráfico de pagamentos. Dados: {dict(payment_counts)}")
           self.update_payment_chart(payment_counts)

           print(f"--- Dashboard: Atualizando gráfico de receita diária. Dados: {dict(daily_revenue)}")
           self.update_revenue_chart(daily_revenue)

           print("--- Dashboard c/ Gráficos: update_summary concluído ---")

    def update_payment_chart(self, payment_data):
           self.payment_chart_widget.clear()
           if not payment_data:
               text = pg.TextItem("Sem dados de pagamento hoje", color='gray', anchor=(0.5, 0.5))
               self.payment_chart_widget.addItem(text)
               self.payment_chart_widget.getAxis('bottom').setTicks(None)
               self.payment_chart_widget.getAxis('left').setTicks(None)
               return

           methods = list(payment_data.keys())
           counts = list(payment_data.values())
           x_values = list(range(len(methods)))

           bars = pg.BarGraphItem(x=x_values, height=counts, width=0.6, brush='b')
           self.payment_chart_widget.addItem(bars)

           ticks = [(i, methods[i]) for i in x_values]
           axis_bottom = self.payment_chart_widget.getAxis('bottom')
           axis_bottom.setTicks([ticks])
           axis_bottom.setStyle(tickTextOffset=10)
           axis_bottom.setTickFont(QFont("Arial", 10))

           max_count = max(counts) if counts else 1
           self.payment_chart_widget.setYRange(0, max_count * 1.1)
           self.payment_chart_widget.setXRange(-0.5, len(methods) - 0.5)

    def update_revenue_chart(self, revenue_data):
           self.revenue_chart_widget.clear()
           if not revenue_data or all(v == 0 for v in revenue_data.values()):
               text = pg.TextItem("Sem dados de receita no período", color='gray', anchor=(0.5, 0.5))
               self.revenue_chart_widget.addItem(text)
               self.revenue_chart_widget.getAxis('bottom').setTicks(None)
               self.revenue_chart_widget.getAxis('left').setTicks(None)
               return

           sorted_dates = sorted(revenue_data.keys())
           totals = [revenue_data[date_str] for date_str in sorted_dates]
           x_values = list(range(len(sorted_dates)))

           bars = pg.BarGraphItem(x=x_values, height=totals, width=0.6, brush='g')
           self.revenue_chart_widget.addItem(bars)

           ticks = []
           for i, date_str_iso in enumerate(sorted_dates):
               qdate = QDate.fromString(date_str_iso, Qt.DateFormat.ISODate)
               if qdate.isValid():
                   ticks.append((i, qdate.toString("dd/MM")))
               else:
                   ticks.append((i, "Inválida"))

           axis_bottom = self.revenue_chart_widget.getAxis('bottom')
           axis_bottom.setTicks([ticks])
           axis_bottom.setStyle(tickTextOffset=10)
           axis_bottom.setTickFont(QFont("Arial", 10))

           max_revenue = max(totals) if totals else 1
           self.revenue_chart_widget.setYRange(0, max_revenue * 1.1)
           self.revenue_chart_widget.setXRange(-0.5, len(sorted_dates) - 0.5)
