# LongPort Data Downloader (GUI Version)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)
![LongPort SDK](https://img.shields.io/badge/SDK-LongPort-orange)

[English](#english) | [中文](#chinese)

<a name="english"></a>

## English

A stock historical data downloader tool developed based on the [LongPort Python SDK](https://github.com/longportapp/openapi-python). Built with PyQt6 for a user-friendly GUI, it supports resumable downloads, data deduplication, and saves data in CSV format.

### Features

- **GUI Interface**: Intuitive operation, no coding required to download data.
- **Multi-Period Support**: Supports 1-Min, 5-Min, 15-Min, 30-Min, 60-Min, Day, Week, Month, and other candlestick periods.
- **Flexible Data Range**: Custom start and end dates.
- **Auto Deduplication**: Automatically handles duplicate data during downloading to ensure accuracy.
- **Real-time Feedback**: Displays download progress bar and detailed execution logs.
- **CSV Export**: Saves data in universal CSV format for easy analysis (compatible with Pandas, Excel, etc.).

### Requirements

- Python 3.8+
- LongPort Account & Open Platform Permissions (App Key, App Secret, Access Token)

### Installation

1. Clone this repository or download source code:
   ```bash
   git clone https://github.com/Start-0-0-1/LongPort-Data-Downloader.git
   cd LongPort-Data-Downloader
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

1. Run the program:
   ```bash
   python datadownloader_gui.py
   ```

2. **Configure API**:
   - Enter your LongPort App Key, App Secret, and Access Token in the "API Config" section.
   - Click "Test Connection" to verify.

3. **Set Download Parameters**:
   - **Symbol**: Enter the stock symbol (e.g., `NVDL.US`, `AAPL.US`, `700.HK`).
   - **Period**: Select the candlestick timeframe.
   - **Date Range**: Select start and end dates.
   - **Save Path**: Choose the folder to save CSV files.

4. **Start Download**:
   - Click "Start Download".
   - The program will fetch data and save it automatically.
   - Filename example: `NVDL_US_Min_1_20240101_to_20260116.csv`

### License

This project is licensed under the [MIT License](LICENSE).

### Author

**JIANG JINGZHE**

If you have any questions or suggestions, please contact:

- Email: [contact@jiangjingzhe.com](mailto:contact@jiangjingzhe.com)
- WeChat: jiangjingzhe_2004

---

<a name="chinese"></a>

## 中文

这是一个基于 [LongPort Python SDK](https://github.com/longportapp/openapi-python) 开发的股票历史数据下载工具。采用 PyQt6 构建图形用户界面，支持断点续传、数据去重，并保存为 CSV 格式。

### 功能特点

- **图形化界面**：直观的操作界面，无需编写代码即可下载数据。
- **多周期支持**：支持 1分钟、5分钟、15分钟、30分钟、1小时、日K、周K、月K 等多种K线周期。
- **灵活的时间范围**：自定义开始和结束日期。
- **自动去重**：下载过程中自动处理重复数据，确保数据准确性。
- **实时进度反馈**：显示下载进度条和详细的运行日志。
- **CSV导出**：将数据保存为通用的 CSV 格式，方便后续分析（如 Pandas、Excel 等）。

### 环境要求

- Python 3.8+
- LongPort 账户及开放平台权限 (App Key, App Secret, Access Token)

### 安装步骤

1. 克隆本项目或下载源码：
   ```bash
   git clone https://github.com/Start-0-0-1/LongPort-Data-Downloader.git
   cd LongPort-Data-Downloader
   ```

2. 安装依赖库：
   ```bash
   pip install -r requirements.txt
   ```

### 使用方法

1. 运行程序：
   ```bash
   python datadownloader_gui.py
   ```

2. **配置 API**：
   - 在界面的 "API 配置" 区域输入您的 LongPort App Key, App Secret 和 Access Token。
   - 点击 "测试连接" 确保配置正确。

3. **设置下载参数**：
   - **股票代码**：输入要下载的股票代码（如 `NVDL.US`, `AAPL.US`, `700.HK`）。
   - **K线精度**：选择时间周期。
   - **日期范围**：选择开始日期和结束日期。
   - **保存路径**：选择保存 CSV 文件的文件夹。

4. **开始下载**：
   - 点击 "开始下载" 按钮。
   - 程序将自动获取数据并在完成后保存文件。
   - 文件名格式示例：`NVDL_US_Min_1_20240101_to_20260116.csv`

### 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

### 作者

**JIANG JINGZHE**

如果您有任何问题或建议，欢迎通过以下方式联系：

- Email: [contact@jiangjingzhe.com](mailto:contact@jiangjingzhe.com)
- WeChat: jiangjingzhe_2004

---
*Disclaimer: This tool is for educational and research purposes only. Investment involves risk, please act cautiously.*
*注意：本工具仅供学习和研究使用，投资有风险，入市需谨慎。*
