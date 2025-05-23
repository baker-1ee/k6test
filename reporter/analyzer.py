import pandas as pd
import numpy as np
from functools import reduce
from utils import format_duration, format_bytes, format_ratio

def calculate_counts_summary(df: pd.DataFrame, metric_name: str, duration_sec: int) -> dict:
    """
    특정 metric_name 에 대해 총 건수(total)를 계산
    """
    filtered = df[df["metric_name"] == metric_name]

    if filtered.empty:
        return {"total": 0}

    return {
        "total": len(filtered)
    }

def calculate_durations_summary(df: pd.DataFrame, metric: str) -> dict:
    """
    주어진 metric_name 에 대해 avg, min, max, p50, p90, p95, p99 값을 계산 해서 dict 로 반환
    """
    df_filtered = df[df["metric_name"] == metric]

    if df_filtered.empty:
        print(f"[WARN] No data for metric: {metric}")
        return {}

    values = df_filtered["metric_value"]
    result = {
        "avg": values.mean(),
        "min": values.min(),
        "max": values.max(),
        "p50": np.percentile(values, 50),
        "p90": np.percentile(values, 90),
        "p95": np.percentile(values, 95),
        "p99": np.percentile(values, 99),
    }
    result = {k: format_duration(v) for k, v in result.items()}
    return result


def calculate_total_transfer_summary(df: pd.DataFrame, duration_sec: int) -> dict:
    """
    data_sent, data_received 총량과 초당 전송량 요약을 dict 로 반환
    """
    if df.empty:
        return {}

    data_received_total = df[df["metric_name"] == "data_received"]["metric_value"].sum()
    data_sent_total = df[df["metric_name"] == "data_sent"]["metric_value"].sum()

    data_received_per_sec = data_received_total / duration_sec if duration_sec else 0
    data_sent_per_sec = data_sent_total / duration_sec if duration_sec else 0

    return {
        "data_received_total": format_bytes(data_received_total),
        "data_received_per_sec": f"{format_bytes(data_received_per_sec)}/s",
        "data_sent_total": format_bytes(data_sent_total),
        "data_sent_per_sec": f"{format_bytes(data_sent_per_sec)}/s",
    }


def generate_time_binned_vus_summary(df: pd.DataFrame, interval_sec: int = 5) -> pd.DataFrame:
    """
    timestamp 기준 interval_sec 간격 으로 VUs 시계열 샘플링
    """
    if df.empty:
        return pd.DataFrame()

    df_vus = df[df["metric_name"] == "vus"].copy()
    df_vus["bucket"] = df_vus["timestamp"].dt.floor(f"{interval_sec}s")

    return (
        df_vus.sort_values("timestamp")
        .groupby("bucket", as_index=False)
        .first()[["bucket", "metric_value"]]
        .rename(columns={"bucket": "timestamp", "metric_value": "vus"})
    )


def generate_time_binned_tps(df: pd.DataFrame, interval_sec: int = 10) -> pd.DataFrame:
    """
    interval_sec 간격 으로 성공 TPS(Time per Second) 시계열 데이터 생성
    """
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "tps"])

    # 필요한 메트릭 만 추출
    reqs = df[df["metric_name"] == "http_reqs"].copy()
    fails = df[(df["metric_name"] == "http_req_failed") & (df["metric_value"] == 1)].copy()

    # 시간 구간 정리
    reqs["interval"] = reqs["timestamp"].dt.floor(f"{interval_sec}s")
    fails["interval"] = fails["timestamp"].dt.floor(f"{interval_sec}s")

    # 각 구간별 요청 수
    req_counts = reqs.groupby("interval").size().reset_index(name="req_count")
    fail_counts = fails.groupby("interval").size().reset_index(name="fail_count")

    # 성공 TPS 계산
    merged = pd.merge(req_counts, fail_counts, on="interval", how="left")
    merged["fail_count"] = merged["fail_count"].fillna(0).astype(int)
    merged["success_count"] = merged["req_count"] - merged["fail_count"]
    merged["tps"] = (merged["success_count"] / interval_sec).round(2)
    merged = merged.rename(columns={"interval": "timestamp"})

    return merged[["timestamp", "tps"]]


def generate_time_binned_latency_summary(df: pd.DataFrame, interval_sec: int = 5) -> pd.DataFrame:
    """
    timestamp 기준 interval_sec 간격 으로 latency 통계 (avg, min, max, p50, p90, p95, p99) 생성
    """
    if df.empty:
        return pd.DataFrame()

    df_latency = df[df["metric_name"] == "http_req_duration"].copy()
    df_latency["bucket"] = df_latency["timestamp"].dt.floor(f"{interval_sec}s")

    return (
        df_latency.groupby("bucket")["metric_value"]
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

def generate_latency_detail_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    URL 별로 전체 요청수, 성공수, 실패수, 성공률, avg, min, max, p50, p90, p95, p99, errors 통계를 계산해서 반환
    """
    if df.empty:
        return pd.DataFrame()

    # 1. 전체 요청수 (http_reqs)
    df_reqs = df[df["metric_name"] == "http_reqs"]
    total_reqs = df_reqs.groupby("url")["metric_value"].count().reset_index(name="total")

    # 2. 실패 요청수 (http_req_failed, metric_value == 1 인 것)
    df_failed = df[(df["metric_name"] == "http_req_failed") & (df["metric_value"] == 1)]
    failed_reqs = df_failed.groupby("url")["metric_value"].count().reset_index(name="fail")

    # 3. latency (http_req_duration)
    df_latency = df[df["metric_name"] == "http_req_duration"]
    latency_summary = df_latency.groupby("url")["metric_value"].agg(
        avg="mean",
        min="min",
        max="max",
        p50=lambda x: np.percentile(x, 50),
        p90=lambda x: np.percentile(x, 90),
        p95=lambda x: np.percentile(x, 95),
        p99=lambda x: np.percentile(x, 99),
    ).reset_index()

    # 4. URL별 errors 요약 추가
    df_errors = df[(df["metric_name"] == "http_req_failed") & (df["error"].notna())]
    if not df_errors.empty:
        error_summary = (
            df_errors
            .groupby("url")["error"]
            .apply(lambda x: ", ".join(f"{err}({cnt})" for err, cnt in x.value_counts().items()))
            .reset_index()
            .rename(columns={"error": "errors"})
        )
    else:
        error_summary = pd.DataFrame(columns=["url", "errors"])

    # 5. 합치기
    result = (
        total_reqs
        .merge(failed_reqs, on="url", how="left")
        .merge(latency_summary, on="url", how="left")
        .merge(error_summary, on="url", how="left")
    )

    result["fail"] = result["fail"].fillna(0).astype(int)
    result["ok"] = result["total"] - result["fail"]
    result["ratio"] = result.apply(lambda row: format_ratio(row["ok"], row["total"]) if row["total"] > 0 else 0, axis=1)
    result = result.drop(columns=["ok"])

    # 6. 숫자 포맷 정리
    latency_cols = ["avg", "min", "max", "p50", "p90", "p95", "p99"]
    result[latency_cols] = result[latency_cols].round(0).astype(int)

    # 7. 열 순서 재정렬
    result = result[["url", "total", "fail", "ratio", "avg", "min", "max", "p50", "p90", "p95", "p99", "errors"]]
    result["errors"] = result["errors"].fillna("-")
    return result


def generate_check_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    checks metric 에 대해 check 별로 total, success, fail 집계
    """
    if df.empty:
        return pd.DataFrame()

    checks_df = df[df["metric_name"] == "checks"]

    if checks_df.empty:
        return pd.DataFrame(columns=["check", "total", "fail", "ratio"])

    result = (
        checks_df
        .groupby("check", as_index=False)
        .agg(
            total=('metric_value', 'count'),
            success=('metric_value', 'sum'),
        )
        .assign(success=lambda x: x["success"].astype(int))
    )
    result["fail"] = result["total"] - result["success"]
    result["ratio"] = result.apply(lambda row: format_ratio(row["success"], row["total"]), axis=1)
    result = result.drop(columns=["success"])

    # 정렬
    result = result.sort_values(by="check", ascending=True).reset_index(drop=True)

    return result


def calculate_failures_summary(df: pd.DataFrame) -> dict:
    """
    http_req_failed 메트릭 기준 으로
    실패 수(failures), 성공 수(successes), 성공률(success_rate), 에러 요약(errors) 계산 하여 dict 로 반환
    """
    failed_df = df[df["metric_name"] == "http_req_failed"]

    if failed_df.empty:
        return {
            "failures": 0,
            "successes": 0,
            "success_rate": 0.0,
            "errors": "-"
        }

    # 실패 건수 (metric_value == 1 인 행 수)
    failures = int(failed_df["metric_value"].sum())

    # 전체 요청 수 (http_req_failed 행 전체 개수)
    total = len(failed_df)

    # 성공 건수
    successes = total - failures

    # 성공률
    success_rate = round((successes / total) * 100, 2) if total > 0 else 0.0

    # 전체 error 종류별 count
    error_summary_df = (
        failed_df[failed_df["error"].notna()]
        .groupby("error")
        .size()
        .reset_index(name="count")
    )

    # 에러 문자열 조합
    error_summary = ", ".join(f"{row['error']}({row['count']})" for _, row in error_summary_df.iterrows())

    return {
        "failures": failures,
        "successes": successes,
        "success_rate": success_rate,
        "errors": error_summary if error_summary else "-"
    }

def merge(*dfs: pd.DataFrame) -> pd.DataFrame:
    """
    여러 DataFrame 을 url 기준 으로 순차 병합

    :param dfs: 병합할 DataFrame 들
    :return: 병합된 단일 DataFrame
    """
    merged = reduce(lambda left, right: pd.merge(left, right, on="url", how="outer"), dfs)
    return merged

