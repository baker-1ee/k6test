import pandas as pd
import numpy as np
from functools import reduce
from typing import List


def calculate_durations_summary(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """
    특정 metric_name 에 대해 전체 기준 통계 분석 (group 없이 전체 집계)
    """
    df_filtered = df[df["metric_name"] == metric]

    if df_filtered.empty:
        print(f"[WARN] No data for metric: {metric}")
        return pd.DataFrame(columns=[
            "metric", "count", "avg", "min", "max", "p50", "p90", "p95", "p99"
        ])

    values = df_filtered["metric_value"]

    summary = {
        "metric": metric,
        "count": len(values),
        "avg": values.mean(),
        "min": values.min(),
        "max": values.max(),
        "p50": np.percentile(values, 50),
        "p90": np.percentile(values, 90),
        "p95": np.percentile(values, 95),
        "p99": np.percentile(values, 99),
    }

    return pd.DataFrame([summary])


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


def calculate_failures_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    http_req_failed 가 1인 요청 전체에 대해 실패 횟수 및 에러 요약 문자열 생성
    """
    failed_df = df[df["metric_name"] == "http_req_failed"]

    if failed_df.empty:
        return pd.DataFrame(columns=["metric", "failures", "errors"])

    # 전체 실패 수 합계
    total_failures = int(failed_df["metric_value"].sum())

    # 전체 error 종류별 count
    error_summary_df = (
        failed_df[failed_df["error"].notna()]
        .groupby("error")
        .size()
        .reset_index(name="count")
    )

    # 에러 문자열 조합
    error_summary = ", ".join(f"{row['error']}({row['count']})" for _, row in error_summary_df.iterrows())

    return pd.DataFrame([{
        "metric": "http_req_failed",
        "failures": total_failures,
        "errors": error_summary if error_summary else "-"
    }])


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