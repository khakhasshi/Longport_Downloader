# LongPort数据下载器 - PyQt6 GUI版本
import sys
import os
from datetime import datetime, date, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QDateEdit, QFileDialog, QTextEdit,
                             QProgressBar, QMessageBox, QGroupBox, QFormLayout,
                             QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QIcon
from longport.openapi import QuoteContext, Config, Period, AdjustType
import pandas as pd
import time

class DataDownloaderThread(QThread):
    """数据下载线程"""
    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    log_updated = pyqtSignal(str)
    download_finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, config_data, symbol, start_date, end_date, period, save_path):
        super().__init__()
        self.config_data = config_data
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.period = period
        self.save_path = save_path
        self.ctx = None
        
    def run(self):
        try:
            # 初始化连接
            self.log_updated.emit("正在初始化连接...")
            config = Config(
                app_key=self.config_data['app_key'],
                app_secret=self.config_data['app_secret'],
                access_token=self.config_data['access_token']
            )
            self.ctx = QuoteContext(config)
            
            # 开始下载
            self.log_updated.emit(f"开始下载 {self.symbol} 数据...")
            all_data = self.download_data()
            
            if all_data:
                self.log_updated.emit(f"总共下载了 {len(all_data)} 条原始记录")
                
                # 去重和保存
                self.log_updated.emit("正在进行数据去重...")
                clean_data = self.remove_duplicates(all_data)
                
                # 保存文件
                df = pd.DataFrame(clean_data)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # 获取Period的字符串表示
                period_str = str(self.period).split('.')[-1] if '.' in str(self.period) else str(self.period)
                
                filename = os.path.join(
                    self.save_path,
                    f"{self.symbol.replace('.', '_')}_"
                    f"{period_str}_"
                    f"{self.start_date.strftime('%Y%m%d')}_to_"
                    f"{self.end_date.strftime('%Y%m%d')}.csv"
                )
                
                df.to_csv(filename, index=False)
                
                message = (f"✓ 数据下载完成!\n"
                          f"✓ 保存到: {filename}\n"
                          f"✓ 去重后共 {len(df)} 条记录\n"
                          f"✓ 时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
                
                self.log_updated.emit(message)
                self.download_finished.emit(True, filename)
            else:
                self.download_finished.emit(False, "未获取到任何数据")
                
        except Exception as e:
            error_msg = f"下载失败: {str(e)}"
            self.log_updated.emit(error_msg)
            self.download_finished.emit(False, error_msg)
    
    def download_data(self):
        """下载数据"""
        all_data = []
        current_date = self.start_date
        total_days = (self.end_date - self.start_date).days + 1
        current_day = 0
        
        while current_date <= self.end_date:
            current_day += 1
            next_date = current_date + timedelta(days=1)
            
            try:
                self.progress_updated.emit(current_day, total_days, f"正在下载 {current_date} 的数据...")
                
                # 获取单天数据
                resp = self.ctx.history_candlesticks_by_date(
                    self.symbol,
                    self.period,
                    AdjustType.NoAdjust,
                    current_date,
                    next_date
                )
                
                if resp and len(resp) > 0:
                    day_data = []
                    for candle in resp:
                        day_data.append({
                            'timestamp': candle.timestamp,
                            'open': candle.open,
                            'high': candle.high,
                            'low': candle.low,
                            'close': candle.close,
                            'volume': candle.volume,
                            'turnover': candle.turnover,
                            'trade_session': str(candle.trade_session)
                        })
                    
                    all_data.extend(day_data)
                    self.log_updated.emit(f"    ✓ {current_date} 成功获取 {len(resp)} 条记录")
                else:
                    self.log_updated.emit(f"    ⚠ {current_date} 无数据")
                    
            except Exception as e:
                self.log_updated.emit(f"    ✗ 获取 {current_date} 数据失败: {str(e)}")
                if "out of minute kline begin date" in str(e):
                    self.log_updated.emit("    ⚠ 该日期超出可用数据范围，继续下一天...")
            
            time.sleep(0.3)
            current_date = next_date
        
        return all_data
    
    def remove_duplicates(self, data):
        """去除重复数据"""
        if not data:
            return data
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        original_count = len(df)
        df = df.drop_duplicates(subset=['timestamp'], keep='first')
        removed_count = original_count - len(df)
        
        if removed_count > 0:
            self.log_updated.emit(f"去重完成: 删除了 {removed_count} 条重复记录")
        else:
            self.log_updated.emit("未发现重复记录")
        
        df = df.sort_values('timestamp')
        return df.to_dict('records')

class DataDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("LongPort 股票数据下载器")
        self.setGeometry(100, 100, 800, 700)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title_label = QLabel("LongPort 股票数据下载器")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # API配置组
        api_group = QGroupBox("API 配置")
        api_layout = QFormLayout()
        
        self.app_key_edit = QLineEdit()
        self.app_key_edit.setText("your_app_key_here")
        api_layout.addRow("App Key:", self.app_key_edit)
        
        self.app_secret_edit = QLineEdit()
        self.app_secret_edit.setText("your_app_secret_here")
        self.app_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("App Secret:", self.app_secret_edit)
        
        self.access_token_edit = QLineEdit()
        self.access_token_edit.setText("your_access_token_here")
        self.access_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("Access Token:", self.access_token_edit)
        
        api_group.setLayout(api_layout)
        main_layout.addWidget(api_group)
        
        # 下载设置组
        download_group = QGroupBox("下载设置")
        download_layout = QFormLayout()
        
        # 股票代码
        self.symbol_edit = QLineEdit()
        self.symbol_edit.setText("NVDL.US")
        self.symbol_edit.setPlaceholderText("例如: NVDL.US, AAPL.US, 700.HK")
        download_layout.addRow("股票代码:", self.symbol_edit)
        
        # K线精度
        self.period_combo = QComboBox()
        self.period_combo.addItem("1分钟", Period.Min_1)
        self.period_combo.addItem("5分钟", Period.Min_5)
        self.period_combo.addItem("15分钟", Period.Min_15)
        self.period_combo.addItem("30分钟", Period.Min_30)
        self.period_combo.addItem("1小时", Period.Min_60)
        self.period_combo.addItem("1天", Period.Day)
        self.period_combo.addItem("1周", Period.Week)
        self.period_combo.addItem("1月", Period.Month)
        download_layout.addRow("K线精度:", self.period_combo)
        
        # 开始日期
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate(2024, 1, 1))
        self.start_date_edit.setCalendarPopup(True)
        download_layout.addRow("开始日期:", self.start_date_edit)
        
        # 结束日期
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        download_layout.addRow("结束日期:", self.end_date_edit)
        
        # 保存路径
        path_layout = QHBoxLayout()
        self.save_path_edit = QLineEdit()
        self.save_path_edit.setText(os.getcwd())
        path_layout.addWidget(self.save_path_edit)
        
        self.browse_button = QPushButton("浏览...")
        self.browse_button.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.browse_button)
        
        download_layout.addRow("保存路径:", path_layout)
        
        download_group.setLayout(download_layout)
        main_layout.addWidget(download_group)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.test_connection_button = QPushButton("测试连接")
        self.test_connection_button.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_connection_button)
        
        self.download_button = QPushButton("开始下载")
        self.download_button.clicked.connect(self.start_download)
        button_layout.addWidget(self.download_button)
        
        self.stop_button = QPushButton("停止下载")
        self.stop_button.clicked.connect(self.stop_download)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        main_layout.addWidget(self.status_label)
        
        # 日志输出
        log_group = QGroupBox("下载日志")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # 清除日志按钮
        self.clear_log_button = QPushButton("清除日志")
        self.clear_log_button.clicked.connect(self.clear_log)
        log_layout.addWidget(self.clear_log_button)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
    def browse_folder(self):
        """选择保存文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择保存文件夹", self.save_path_edit.text())
        if folder:
            self.save_path_edit.setText(folder)
    
    def test_connection(self):
        """测试API连接"""
        try:
            config = Config(
                app_key=self.app_key_edit.text(),
                app_secret=self.app_secret_edit.text(),
                access_token=self.access_token_edit.text()
            )
            ctx = QuoteContext(config)
            
            # 尝试获取一个简单的数据来测试连接
            symbol = self.symbol_edit.text() or "AAPL.US"
            end_date = date.today()
            start_date = end_date - timedelta(days=1)
            
            resp = ctx.history_candlesticks_by_date(
                symbol,
                Period.Day,
                AdjustType.NoAdjust,
                start_date,
                end_date
            )
            
            QMessageBox.information(self, "连接测试", "✓ API连接测试成功!")
            self.add_log("✓ API连接测试成功!")
            
        except Exception as e:
            QMessageBox.critical(self, "连接测试", f"✗ API连接测试失败:\n{str(e)}")
            self.add_log(f"✗ API连接测试失败: {str(e)}")
    
    def start_download(self):
        """开始下载"""
        # 验证输入
        if not self.symbol_edit.text():
            QMessageBox.warning(self, "输入错误", "请输入股票代码")
            return
        
        if not os.path.exists(self.save_path_edit.text()):
            QMessageBox.warning(self, "路径错误", "保存路径不存在")
            return
        
        qstart_date = self.start_date_edit.date()
        qend_date = self.end_date_edit.date()
        start_date = date(qstart_date.year(), qstart_date.month(), qstart_date.day())
        end_date = date(qend_date.year(), qend_date.month(), qend_date.day())
        
        if start_date >= end_date:
            QMessageBox.warning(self, "日期错误", "开始日期必须早于结束日期")
            return
        
        # 准备配置数据
        config_data = {
            'app_key': self.app_key_edit.text(),
            'app_secret': self.app_secret_edit.text(),
            'access_token': self.access_token_edit.text()
        }
        
        symbol = self.symbol_edit.text()
        period = self.period_combo.currentData()
        save_path = self.save_path_edit.text()
        
        # 创建并启动下载线程
        self.download_thread = DataDownloaderThread(
            config_data, symbol, start_date, end_date, period, save_path
        )
        
        # 连接信号
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.log_updated.connect(self.add_log)
        self.download_thread.download_finished.connect(self.download_finished)
        
        # 更新UI状态
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(100)
        self.status_label.setText("正在下载...")
        
        # 启动线程
        self.download_thread.start()
    
    def stop_download(self):
        """停止下载"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()
            self.add_log("下载已被用户停止")
            self.download_finished(False, "下载已停止")
    
    def update_progress(self, current, total, message):
        """更新进度"""
        percentage = int((current / total) * 100)
        self.progress_bar.setValue(percentage)
        self.status_label.setText(f"{message} ({current}/{total})")
    
    def add_log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def clear_log(self):
        """清除日志"""
        self.log_text.clear()
    
    def download_finished(self, success, message):
        """下载完成"""
        # 更新UI状态
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("下载完成")
            QMessageBox.information(self, "下载完成", message)
        else:
            self.status_label.setText("下载失败")
            QMessageBox.critical(self, "下载失败", message)

def main():
    app = QApplication(sys.argv)
    window = DataDownloaderGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
