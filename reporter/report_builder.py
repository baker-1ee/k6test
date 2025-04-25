from typing import Dict
import pandas as pd
from charts import generate_chartjs_latency_chart, generate_chartjs_vus_chart
from utils import determine_interval_seconds
import numpy as np


def generate_time_binned_latency_summary(df: pd.DataFrame, interval_sec: int = 5) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["bucket"] = df["timestamp"].dt.floor(f"{interval_sec}s")
    summary_df = (
        df.groupby("bucket")["metric_value"]
        .agg(
            avg="mean",
            min="min",
            max="max",
            p50=lambda x: np.percentile(x, 50),
            p90=lambda x: np.percentile(x, 90),
            p95=lambda x: np.percentile(x, 95),
            p99=lambda x: np.percentile(x, 99),
        )
        .reset_index()
        .rename(columns={"bucket": "timestamp"})
    )
    return summary_df


def generate_time_binned_vus_summary(df: pd.DataFrame, interval_sec: int = 5) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    df = df.copy()
    df["bucket"] = df["timestamp"].dt.floor(f"{interval_sec}s")
    summary_df = (
        df.sort_values("timestamp")
        .groupby("bucket", as_index=False)
        .first()[["bucket", "metric_value"]]
        .rename(columns={"bucket": "timestamp", "metric_value": "vus"})
    )
    return summary_df


def generate_html_report(
        report_title: str,
        sum_http: Dict,
        stats: Dict,
        network_summary: Dict,
        check_summary: pd.DataFrame,
        df_req_duration: pd.DataFrame,
        duration_secs: int,
        df_vus: pd.DataFrame,
) -> str:

    def format_cell(value):
        if isinstance(value, float):
            return str(int(value)) if value.is_integer() else f"{value:.1f}"
        return str(value)

    def dict_to_html_table(title, data, icon="📊"):
        rows = ''.join(f'<tr><td><b>{k}</b></td><td>{v}</td></tr>' for k, v in data.items())
        return f'''
        <div class="card">
            <div class="card-title">{icon} {title}</div>
            <table>{rows}</table>
        </div>
        '''

    def stats_to_html_table(metric_name, metric_data):
        rows = ''.join(f'<tr><td><b>{stat}</b></td><td>{value}</td></tr>' for stat, value in metric_data.items())
        return f'''
        <div class="card">
            <div class="card-title">🕐 Iteration duration (ms)</div>
            <table>
                <tr><td colspan="2"><b>{metric_name}</b></td></tr>
                {rows}
            </table>
        </div>
        '''

    def get_ratio_color_style(ratio: float) -> str:
        if ratio < 50:
            return 'color: #CC0000;'  # 진한 빨강
        elif ratio < 90:
            return 'color: #FF3300;'  # 밝은 빨강
        elif ratio < 100:
            return 'color: #CC6600;'  # 주황
        else:
            return 'color: #33AA33;'     # 기본 회색

    def check_summary_to_html(df):
        headers = ''.join(f'<th>{col}</th>' for col in df.columns)
        rows = ''
        for _, row in df.iterrows():
            ratio = row.get("ratio", 0) if pd.notnull(row.get("ratio")) else 0
            style = get_ratio_color_style(ratio)
            row_html = ''.join(f'<td>{format_cell(row[col])}</td>' for col in df.columns)
            rows += f'<tr style="{style}">{row_html}</tr>'

        return f'''
        <div class="card-full">
            <div class="card-title">✅ Check Result Detail</div>
            <table>
                <thead><tr>{headers}</tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        '''

    interval_sec = determine_interval_seconds(duration_secs)
    latency_trend_df = generate_time_binned_latency_summary(df_req_duration, interval_sec)
    vus_trend_df = generate_time_binned_vus_summary(df_vus, interval_sec)

    latency_chart_html = generate_chartjs_latency_chart(latency_trend_df)
    vus_chart_html = generate_chartjs_vus_chart(vus_trend_df)

    cards = [
        dict_to_html_table("HTTP request", sum_http, icon="📊"),
        stats_to_html_table("http_req_duration", stats.get("http_req_duration", {})),
        stats_to_html_table("iteration_duration", stats.get("iteration_duration", {})),
        dict_to_html_table("Network Usage", network_summary, icon="📡"),
    ]

    check_result_html = check_summary_to_html(check_summary)

    html = f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>K6 Performance Test Report</title>
        <script src="assets/js/chart.min.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; background: #fff; color: #000; padding: 2rem; }}
            h1 {{ font-size: 2rem; margin-bottom: 2rem; text-align: center; }}
            h3 {{ text-align: right; }}
            .container {{ display: flex; gap: 1rem; margin-bottom: 2rem; }}
            .section-gap {{ margin-bottom: 2rem; }}
            .card, .card-full {{ background: #f9f9f9; padding: 1rem; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.4); }}
            .card {{ flex: 1; }}
            .card-title {{ background: #dbefff; padding: 0.5rem 1rem; font-weight: bold; border-radius: 8px 8px 0 0; margin: -1rem -1rem 1rem -1rem; font-size: 1rem; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ text-align: right; padding: 0.5rem; border-bottom: 1px solid #444; font-size: 0.85rem; }}
            td:first-child {{ text-align: left; }}
            th {{ text-align: center; background-color: #dbefff; }}
        </style>
    </head>
    <body>
        <h1>K6 Performance Test Report</h1>
        <h3>{report_title}</h3>
        <div class="container">
            {cards[0]}{cards[1]}{cards[2]}{cards[3]}
        </div>
        <div class="section-gap">
            {vus_chart_html}
        </div>
        <div class="section-gap">
            {latency_chart_html}
        </div>
        <div class="section-gap">
            {check_result_html}
        </div>
    </body>
    </html>
    '''
    return html
