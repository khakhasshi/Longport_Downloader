# LongPort数据下载器 - Textual TUI版本
import os
import sys
import time
import threading
from datetime import datetime, date, timedelta

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import (
    Header, Footer, Static, Input, Button, Select,
    ProgressBar, Log, Label, Rule,
)
from textual.worker import Worker, get_current_worker
from textual import work

from longport.openapi import QuoteContext, Config, Period, AdjustType
import pandas as pd


# K线精度选项
PERIOD_OPTIONS: list[tuple[str, Period]] = [
    ("1分钟", Period.Min_1),
    ("5分钟", Period.Min_5),
    ("15分钟", Period.Min_15),
    ("30分钟", Period.Min_30),
    ("1小时", Period.Min_60),
    ("1天", Period.Day),
    ("1周", Period.Week),
    ("1月", Period.Month),
]


class DataDownloaderTUI(App):
    """LongPort 股票数据下载器 - TUI版本"""

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        padding: 1 2;
    }

    .section-title {
        text-style: bold;
        color: $accent;
        margin-top: 1;
        margin-bottom: 0;
    }

    .form-row {
        layout: horizontal;
        height: 3;
        margin-bottom: 0;
    }

    .form-label {
        width: 16;
        content-align-vertical: middle;
        padding-top: 1;
    }

    .form-input {
        width: 1fr;
    }

    #period-select {
        width: 1fr;
    }

    .button-bar {
        layout: horizontal;
        height: 3;
        margin-top: 1;
        margin-bottom: 1;
        align: center middle;
    }

    .button-bar Button {
        margin: 0 1;
    }

    #btn-test {
        background: $primary;
    }

    #btn-download {
        background: $success;
    }

    #btn-stop {
        background: $error;
    }

    #progress-bar {
        margin: 0 0 1 0;
    }

    #status-label {
        height: 1;
        margin-bottom: 1;
        color: $text-muted;
    }

    #log-view {
        height: 1fr;
        min-height: 8;
        border: solid $primary;
    }
    """

    BINDINGS = [
        ("q", "quit", "退出"),
        ("ctrl+l", "clear_log", "清除日志"),
        ("ctrl+t", "test_conn", "测试连接"),
        ("ctrl+d", "do_download", "开始下载"),
    ]

    TITLE = "LongPort 股票数据下载器"

    def __init__(self):
        super().__init__()
        self._downloading = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            # ---------- API 配置 ----------
            yield Static("── API 配置 ──", classes="section-title")

            with Horizontal(classes="form-row"):
                yield Label("App Key:", classes="form-label")
                yield Input(
                    value="your_app_key_here",
                    id="app-key",
                    classes="form-input",
                )

            with Horizontal(classes="form-row"):
                yield Label("App Secret:", classes="form-label")
                yield Input(
                    value="your_app_secret_here",
                    password=True,
                    id="app-secret",
                    classes="form-input",
                )

            with Horizontal(classes="form-row"):
                yield Label("Access Token:", classes="form-label")
                yield Input(
                    value="your_access_token_here",
                    password=True,
                    id="access-token",
                    classes="form-input",
                )

            # ---------- 下载设置 ----------
            yield Static("── 下载设置 ──", classes="section-title")

            with Horizontal(classes="form-row"):
                yield Label("股票代码:", classes="form-label")
                yield Input(
                    value="NVDL.US",
                    placeholder="例如: NVDL.US, AAPL.US, 700.HK",
                    id="symbol",
                    classes="form-input",
                )

            with Horizontal(classes="form-row"):
                yield Label("K线精度:", classes="form-label")
                yield Select(
                    options=PERIOD_OPTIONS,
                    value=Period.Min_1,
                    id="period-select",
                )

            with Horizontal(classes="form-row"):
                yield Label("开始日期:", classes="form-label")
                yield Input(
                    value="2024-01-01",
                    placeholder="YYYY-MM-DD",
                    id="start-date",
                    classes="form-input",
                )

            with Horizontal(classes="form-row"):
                yield Label("结束日期:", classes="form-label")
                yield Input(
                    value=date.today().isoformat(),
                    placeholder="YYYY-MM-DD",
                    id="end-date",
                    classes="form-input",
                )

            with Horizontal(classes="form-row"):
                yield Label("保存路径:", classes="form-label")
                yield Input(
                    value=os.getcwd(),
                    id="save-path",
                    classes="form-input",
                )

            # ---------- 按钮 ----------
            with Horizontal(classes="button-bar"):
                yield Button("测试连接", id="btn-test", variant="primary")
                yield Button("开始下载", id="btn-download", variant="success")
                yield Button("停止下载", id="btn-stop", variant="error", disabled=True)
                yield Button("清除日志", id="btn-clear", variant="default")

            # ---------- 进度 & 日志 ----------
            yield ProgressBar(total=100, show_eta=True, id="progress-bar")
            yield Label("准备就绪", id="status-label")
            yield Log(id="log-view", highlight=True, auto_scroll=True)

        yield Footer()

    # ──────────────── 辅助方法 ────────────────

    def _get_config_data(self) -> dict:
        return {
            "app_key": self.query_one("#app-key", Input).value,
            "app_secret": self.query_one("#app-secret", Input).value,
            "access_token": self.query_one("#access-token", Input).value,
        }

    def _parse_date(self, input_id: str) -> date:
        text = self.query_one(f"#{input_id}", Input).value.strip()
        return datetime.strptime(text, "%Y-%m-%d").date()

    def _log(self, message: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        log_widget = self.query_one("#log-view", Log)
        log_widget.write_line(f"[{ts}] {message}")

    def _set_status(self, text: str) -> None:
        self.query_one("#status-label", Label).update(text)

    # ──────────────── 按钮事件 ────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-test":
            self.action_test_conn()
        elif btn_id == "btn-download":
            self.action_do_download()
        elif btn_id == "btn-stop":
            self._stop_download()
        elif btn_id == "btn-clear":
            self.action_clear_log()

    # ──────────────── 连接测试 ────────────────

    def action_test_conn(self) -> None:
        self._test_connection()

    @work(thread=True)
    def _test_connection(self) -> None:
        self.call_from_thread(self._log, "正在测试 API 连接...")
        try:
            cfg = self._get_config_data()
            config = Config(
                app_key=cfg["app_key"],
                app_secret=cfg["app_secret"],
                access_token=cfg["access_token"],
            )
            ctx = QuoteContext(config)

            symbol = self.query_one("#symbol", Input).value or "AAPL.US"
            end_d = date.today()
            start_d = end_d - timedelta(days=1)

            ctx.history_candlesticks_by_date(
                symbol, Period.Day, AdjustType.NoAdjust, start_d, end_d
            )

            self.call_from_thread(self._log, "✓ API 连接测试成功!")
            self.call_from_thread(self._set_status, "连接测试成功")
        except Exception as e:
            self.call_from_thread(self._log, f"✗ API 连接测试失败: {e}")
            self.call_from_thread(self._set_status, "连接测试失败")

    # ──────────────── 下载逻辑 ────────────────

    def action_do_download(self) -> None:
        if self._downloading:
            self._log("已有正在进行的下载任务")
            return
        self._start_download()

    @work(thread=True, exclusive=True, group="download")
    def _start_download(self) -> None:
        worker = get_current_worker()

        # 解析参数
        try:
            cfg = self._get_config_data()
            symbol = self.query_one("#symbol", Input).value.strip()
            if not symbol:
                self.call_from_thread(self._log, "请输入股票代码")
                return

            start_date = self._parse_date("start-date")
            end_date = self._parse_date("end-date")

            if start_date >= end_date:
                self.call_from_thread(self._log, "开始日期必须早于结束日期")
                return

            save_path = self.query_one("#save-path", Input).value.strip()
            if not os.path.isdir(save_path):
                self.call_from_thread(self._log, f"保存路径不存在: {save_path}")
                return

            period: Period = self.query_one("#period-select", Select).value

        except Exception as e:
            self.call_from_thread(self._log, f"参数解析失败: {e}")
            return

        # 开始下载
        self._downloading = True
        self.call_from_thread(self._set_downloading_ui, True)
        self.call_from_thread(self._log, f"开始下载 {symbol} 数据...")

        try:
            config = Config(
                app_key=cfg["app_key"],
                app_secret=cfg["app_secret"],
                access_token=cfg["access_token"],
            )
            ctx = QuoteContext(config)

            all_data: list[dict] = []
            current_date = start_date
            total_days = (end_date - start_date).days + 1
            current_day = 0

            while current_date <= end_date:
                if worker.is_cancelled:
                    self.call_from_thread(self._log, "下载已被用户停止")
                    break

                current_day += 1
                next_date = current_date + timedelta(days=1)

                pct = int(current_day / total_days * 100)
                self.call_from_thread(self._update_progress, pct, f"正在下载 {current_date} ({current_day}/{total_days})")

                try:
                    resp = ctx.history_candlesticks_by_date(
                        symbol, period, AdjustType.NoAdjust,
                        current_date, next_date,
                    )

                    if resp and len(resp) > 0:
                        for candle in resp:
                            all_data.append({
                                "timestamp": candle.timestamp,
                                "open": candle.open,
                                "high": candle.high,
                                "low": candle.low,
                                "close": candle.close,
                                "volume": candle.volume,
                                "turnover": candle.turnover,
                                "trade_session": str(candle.trade_session),
                            })
                        self.call_from_thread(self._log, f"    ✓ {current_date} 成功获取 {len(resp)} 条记录")
                    else:
                        self.call_from_thread(self._log, f"    ⚠ {current_date} 无数据")

                except Exception as e:
                    self.call_from_thread(self._log, f"    ✗ 获取 {current_date} 数据失败: {e}")
                    if "out of minute kline begin date" in str(e):
                        self.call_from_thread(self._log, "    ⚠ 该日期超出可用数据范围，继续下一天...")

                time.sleep(0.3)
                current_date = next_date

            # 保存
            if all_data and not worker.is_cancelled:
                self.call_from_thread(self._log, f"总共下载了 {len(all_data)} 条原始记录")
                self.call_from_thread(self._log, "正在进行数据去重...")

                df = pd.DataFrame(all_data)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                original_count = len(df)
                df = df.drop_duplicates(subset=["timestamp"], keep="first")
                removed = original_count - len(df)

                if removed > 0:
                    self.call_from_thread(self._log, f"去重完成: 删除了 {removed} 条重复记录")
                else:
                    self.call_from_thread(self._log, "未发现重复记录")

                df = df.sort_values("timestamp")

                period_str = str(period).split(".")[-1] if "." in str(period) else str(period)
                filename = os.path.join(
                    save_path,
                    f"{symbol.replace('.', '_')}_{period_str}_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv",
                )
                df.to_csv(filename, index=False)

                msg = (
                    f"✓ 数据下载完成!\n"
                    f"✓ 保存到: {filename}\n"
                    f"✓ 去重后共 {len(df)} 条记录\n"
                    f"✓ 时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}"
                )
                for line in msg.split("\n"):
                    self.call_from_thread(self._log, line)
                self.call_from_thread(self._set_status, "下载完成")
            elif not all_data:
                self.call_from_thread(self._log, "未获取到任何数据")
                self.call_from_thread(self._set_status, "下载完成 (无数据)")

        except Exception as e:
            self.call_from_thread(self._log, f"下载失败: {e}")
            self.call_from_thread(self._set_status, "下载失败")
        finally:
            self._downloading = False
            self.call_from_thread(self._set_downloading_ui, False)

    def _stop_download(self) -> None:
        if self._downloading:
            self.workers.cancel_group(self, "download")
            self._log("正在取消下载...")

    # ──────────────── UI更新 ────────────────

    def _set_downloading_ui(self, downloading: bool) -> None:
        self.query_one("#btn-download", Button).disabled = downloading
        self.query_one("#btn-stop", Button).disabled = not downloading
        if not downloading:
            self.query_one("#progress-bar", ProgressBar).update(total=100, progress=0)

    def _update_progress(self, pct: int, message: str) -> None:
        self.query_one("#progress-bar", ProgressBar).update(total=100, progress=pct)
        self._set_status(message)

    # ──────────────── Action ────────────────

    def action_clear_log(self) -> None:
        self.query_one("#log-view", Log).clear()

    def action_quit(self) -> None:
        if self._downloading:
            self.workers.cancel_group(self, "download")
        self.exit()


def main():
    app = DataDownloaderTUI()
    app.run()


if __name__ == "__main__":
    main()
