# LongPort Data Downloader (GUI Version)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green)
![LongPort SDK](https://img.shields.io/badge/SDK-LongPort-orange)

这是一个基于 [LongPort Python SDK](https://github.com/longportapp/openapi-python) 开发的股票历史数据下载工具。采用 PyQt6 构建图形用户界面，支持断点续传、数据去重，并保存为 CSV 格式。

## 功能特点

- **图形化界面**：直观的操作界面，无需编写代码即可下载数据。
- **多周期支持**：支持 1分钟、5分钟、15分钟、30分钟、1小时、日K、周K、月K 等多种K线周期。
- **灵活的时间范围**：自定义开始和结束日期。
- **自动去重**：下载过程中自动处理重复数据，确保数据准确性。
- **实时进度反馈**：显示下载进度条和详细的运行日志。
- **CSV导出**：将数据保存为通用的 CSV 格式，方便后续分析（如 Pandas、Excel 等）。

## 环境要求

- Python 3.8+
- LongPort 账户及开放平台权限 (App Key, App Secret, Access Token)

## 安装步骤

1. 克隆本项目或下载源码：
   ```bash
   git clone https://github.com/Start-0-0-1/LongPort-Data-Downloader.git
   cd LongPort-Data-Downloader
   ```

2. 安装依赖库：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

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

## 许可证

本项目采用 [MIT 许可证](LICENSE) 开源。

## 作者

**JIANG JINGZHE**

如果您有任何问题或建议，欢迎通过以下方式联系：

- Email: [contact@jiangjingzhe.com](mailto:contact@jiangjingzhe.com)
- WeChat: jiangjingzhe_2004

---
*注意：本工具仅供学习和研究使用，投资有风险，入市需谨慎。*
