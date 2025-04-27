from typing import Union
from pathlib import Path

import pandas as pd

from report_builder import generate_html_report
from utils import format_test_duration_title

def _get_value(df: pd.DataFrame, key: str, default="0") -> str:
    """
    숫자 값을 콤마가 포함된 문자열 로 반환 (UI 출력용)
    """
    if key in df.columns:
        try:
            return f"{int(df.iloc[0][key]):,}"
        except (ValueError, TypeError):
            return default
    return default


def _get_raw_value(df: pd.DataFrame, key: str, default=0.0) -> float:
    """
    숫자 값을 그대로 float 으로 반환 (계산용)
    """
    if key in df.columns:
        try:
            return float(df.iloc[0][key])
        except (ValueError, TypeError):
            return default
    return default

def _tps(df, duration):
    try:
        count = int(df["http_reqs_count"].iloc[0])
        return f"{round(count / duration, 2):,}/s"
    except:
        return "N/A"

def _success_count(df):
    try:
        total = int(df["http_reqs_count"].iloc[0])
        failed = int(df["http_req_failed_failures"].iloc[0])
        return f"{total - failed:,}"
    except:
        return "N/A"

def _success_rate(df):
    try:
        total = int(df["http_reqs_count"].iloc[0])
        failed = int(df["http_req_failed_failures"].iloc[0])
        rate = ((total - failed) / total) * 100
        return f"{rate:.1f}%"
    except:
        return "N/A"

def _iters_per_sec(df, duration):
    try:
        count = int(df["iterations_count"].iloc[0])
        return f"{round(count / duration, 2)}/s"
    except:
        return "N/A"

def _extract_metric_stats(df: pd.DataFrame, metric: str) -> dict:
    keys = ["avg", "min", "max", "p50", "p90", "p95", "p99"]
    result = {}
    for key in keys:
        col = f"{metric}_{key}"
        if col in df.columns:
            result[key] = int(df.iloc[0][col])
    return result


def generate_report(output_path: Union[str, Path], processed: dict):
    """
    기존 generate_html_report() 호출을 위한 변환 함수
    """
    test_duration = processed["test_duration"]
    df_total = processed["df_total"]
    df_detail = processed["df_detail"]

    # 1. 제목 포맷팅
    report_title = format_test_duration_title(test_duration)

    # 2. HTTP Summary 추출
    sum_http = {
        "total_reqs": _get_value(df_total, "http_reqs_count"),
        "tps": _tps(df_total, test_duration["seconds"]),
        "failed_reqs": _get_value(df_total, "http_req_failed_failures"),
        "success_reqs": _success_count(df_total),
        "success_rate": _success_rate(df_total),
        "iterations": _get_value(df_total, "iterations_count"),
        "iterations/sec": _iters_per_sec(df_total, test_duration["seconds"]),
        "vus_min": _get_value(df_total, "vus_min"),
        "vus_max": _get_value(df_total, "vus_max"),
    }

    # 3. Duration Stats
    stats = {
        "http_req_duration": _extract_metric_stats(df_total, "http_req_duration"),
        "iteration_duration": _extract_metric_stats(df_total, "iteration_duration"),
    }

    # 4. Network Summary
    data_received = float(_get_raw_value(df_total, "data_received_total", '0'))
    data_sent = float(_get_raw_value(df_total, "data_sent_total", '0'))
    duration = test_duration["seconds"]
    from utils import format_bytes

    network_summary = {
        "data_received": f"{format_bytes(data_received)}  {format_bytes(data_received / duration)}/s",
        "data_sent": f"{format_bytes(data_sent)}  {format_bytes(data_sent / duration)}/s",
    }

    # 5. Check Summary = df_detail + ratio
    df_checks = df_detail.copy()
    if "failures" in df_checks.columns and "http_reqs_count" in df_total.columns:
        df_checks["total"] = df_checks.get("failures", 0) + _get_value(df_total, "http_reqs_count", 0)
        df_checks["ok"] = df_checks["total"] - df_checks.get("failures", 0)
        from utils import format_ratio
        df_checks["ratio"] = df_checks.apply(lambda row: format_ratio(row.get("ok", 0), row.get("total", 0)), axis=1)

    html = generate_html_report(
        report_title=report_title,
        sum_http=sum_http,
        stats=stats,
        network_summary=network_summary,
        check_summary=df_checks,
        df_req_duration=df_detail,
        duration_secs=duration,
        df_vus=pd.DataFrame()  # optional
    )

    from pathlib import Path
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"[DONE] Report saved: {output_path}")
