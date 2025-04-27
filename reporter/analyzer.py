import pandas as pd
import numpy as np
from functools import reduce
from typing import List

def calculate_counts_summary(df: pd.DataFrame, metric_name: str, duration_sec: int) -> dict:
    """
    특정 metric_name 에 대해 총 건수(total)와 TPS 를 계산
    """
    filtered = df[df["metric_name"] == metric_name]

    if filtered.empty or duration_sec <= 0:
        return {"total": 0, "tps": 0}

    total_count = len(filtered)
    tps = round(total_count / duration_sec, 2)

    return {
        "total": total_count,
        "tps": tps
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
    return {
        "avg": values.mean(),
        "min": values.min(),
        "max": values.max(),
        "p50": np.percentile(values, 50),
        "p90": np.percentile(values, 90),
        "p95": np.percentile(values, 95),
        "p99": np.percentile(values, 99),
    }


def calculate_total_transfer_summary(df: pd.DataFrame, duration_sec: int) -> dict:
    """
    data_sent, data_received 총량과 초당 전송량 요약을 dict 로 반환
    """
    total_received = df[df["metric_name"] == "data_received"]["metric_value"].sum()
    total_sent = df[df["metric_name"] == "data_sent"]["metric_value"].sum()

    received_per_sec = total_received / duration_sec if duration_sec > 0 else 0
    sent_per_sec = total_sent / duration_sec if duration_sec > 0 else 0

    return {
        "data_received": {
            "total": total_received,
            "per_sec": received_per_sec,
        },
        "data_sent": {
            "total": total_sent,
            "per_sec": sent_per_sec,
        }
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



def calculate_durations(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """
    특정 metric_name 에 대해 URL 별 통계 분석
    """
    df_filtered = df[df["metric_name"] == metric]

    if df_filtered.empty:
        print(f"[WARN] No data for metric: {metric}")
        return pd.DataFrame()

    # 그룹 기준: URL
    group = df_filtered.groupby("url")["metric_value"]

    result = group.agg([
        ("count", "count"),
        ("avg", "mean"),
        ("min", "min"),
        ("max", "max"),
        ("p50", lambda x: np.percentile(x, 50)),
        ("p90", lambda x: np.percentile(x, 90)),
        ("p95", lambda x: np.percentile(x, 95)),
        ("p99", lambda x: np.percentile(x, 99)),
    ]).reset_index()

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


def calculate_failures(df: pd.DataFrame) -> pd.DataFrame:
    """
    http_req_failed 가 1인 요청만 필터링 하여 url 별 실패 횟수 합산
    """
    failed_df = df[df["metric_name"] == "http_req_failed"]
    if failed_df.empty:
        return pd.DataFrame(columns=["url", "failures", "errors"])

    # 1. URL 별 실패 수 합산
    failure_counts = (
        failed_df.groupby("url")["metric_value"]
        .sum()
        .reset_index()
        .rename(columns={"metric_value": "failures"})
    )

    # 2. URL + error 별 count
    error_summary_df = (
        failed_df[failed_df["error"].notna()]
        .groupby(["url", "error"])
        .size()
        .reset_index(name="count")
    )

    # 3. errors 문자열 조합
    def summarize_errors(sub_df):
        return ", ".join(f"{row['error']}({row['count']})" for _, row in sub_df.iterrows())

    errors = (
        error_summary_df
        .groupby("url")
        .apply(summarize_errors)
        .reset_index(name="errors")
    )

    # 4. 실패 수 + 에러 요약 merge
    result = failure_counts.merge(errors, on="url", how="left")
    result["errors"] = result["errors"].fillna("-")

    return result


def calculate_total_transfer(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """
    data_sent 또는 data_received 메트릭 에 대해 전체 합계 계산
    """
    df_filtered = df[df["metric_name"] == metric]

    if df_filtered.empty:
        print(f"[WARN] No data for metric: {metric}")
        return pd.DataFrame(columns=["metric", "total"])

    total = df_filtered["metric_value"].sum()

    return pd.DataFrame([{
        "metric": metric,
        "total": total
    }])


def calculate_error_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    error 필드가 있는 행을 분석 하여 error 별 발생 횟수 집계
    """
    error_df = df[(df["metric_name"] == "error") & (df["error"].notna())]
    if error_df.empty:
        return pd.DataFrame(columns=["error_type", "count"])

    summary = error_df["error"].value_counts().reset_index()
    summary.columns = ["error_type", "count"]
    return summary


def merge(*dfs: pd.DataFrame) -> pd.DataFrame:
    """
    여러 DataFrame 을 url 기준 으로 순차 병합

    :param dfs: 병합할 DataFrame 들
    :return: 병합된 단일 DataFrame
    """
    merged = reduce(lambda left, right: pd.merge(left, right, on="url", how="outer"), dfs)
    return merged


def merge_summary(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    """
    여러 1-row 요약 DataFrame 을 병합 하되, 각 row 의 'metric' 값을 prefix 로 컬럼명 붙임
    """
    renamed_dfs = []

    for df in dfs:
        if df.empty:
            continue

        # metric 이름 추출
        metric = df["metric"].iloc[0] if "metric" in df.columns else "unknown"

        # 'metric' 컬럼 제외 후, 나머지 컬럼에 prefix 붙이기
        renamed = df.drop(columns=["metric"], errors="ignore")
        renamed.columns = [f"{metric}_{col}" for col in renamed.columns]

        renamed_dfs.append(renamed.reset_index(drop=True))

    if not renamed_dfs:
        return pd.DataFrame()

    # 좌우로 병합
    merged = renamed_dfs[0]
    for df in renamed_dfs[1:]:
        merged = merged.join(df, how="outer")

    return merged
