import utils
import analyzer
import pandas as pd

def process_data(df):
    """
    전체 DataFrame(df)을 받아서,
    HTML/CSV 출력을 위해 필요한 데이터 묶음을 dict 형태로 반환.
    """
    # 테스트 시간
    test_duration = utils.calculate_test_duration(df)

    # HTTP 요청 요약
    http_reqs = analyzer.calculate_counts_summary(df, 'http_reqs', test_duration["seconds"])
    http_req_failed = analyzer.calculate_failures_summary(df)
    iterations = analyzer.calculate_counts_summary(df, 'iterations', test_duration["seconds"])
    vus_min = df[df["metric_name"] == "vus"]["metric_value"].min()
    vus_max = df[df["metric_name"] == "vus"]["metric_value"].max()

    summary_http_request = {
        "total_reqs": http_reqs.get("total", 0),
        "tps": http_reqs.get("tps", 0),
        "failed_reqs": http_req_failed.get("failures", 0),
        "success_reqs": http_req_failed.get("successes", 0),
        "success_rate": http_req_failed.get("success_rate", 0),
        "iterations": iterations.get("total", 0),
        "iterations/sec": iterations.get("tps", 0),
        "vus_min": int(vus_min) if not pd.isna(vus_min) else 0,
        "vus_max": int(vus_max) if not pd.isna(vus_max) else 0,
    }

    # HTTP Request Error 요약
    summary_http_errors = http_req_failed.get("errors", "-")

    # HTTP Request Duration 요약
    summary_http_req_duration = analyzer.calculate_durations_summary(df, 'http_req_duration')

    # Iteration Duration 요약
    summary_iteration_duration = analyzer.calculate_durations_summary(df, 'iteration_duration')

    # Network Usage 요약
    summary_network_usage = analyzer.calculate_total_transfer_summary(df, test_duration["seconds"])

    # VU 시계열 데이터
    interval_sec = utils.determine_interval_seconds(test_duration["seconds"])
    chart_vus_timeseries = analyzer.generate_time_binned_vus_summary(df, interval_sec)

    # HTTP Request Latency 시계열 데이터
    chart_latency_timeseries = analyzer.generate_time_binned_latency_summary(df, interval_sec)

    # URL 별 통계 테이블
    detail_latency_table = analyzer.generate_latency_detail_summary(df)

    # checks 결과 요약
    detail_check_table = analyzer.generate_check_summary(df)

    return {
        "test_duration": test_duration,
        "summary_http_request": summary_http_request,
        "summary_http_req_duration": summary_http_req_duration,
        "summary_iteration_duration": summary_iteration_duration,
        "summary_network_usage": summary_network_usage,
        "summary_http_errors": summary_http_errors,
        "chart_vus_timeseries": chart_vus_timeseries,
        "chart_latency_timeseries": chart_latency_timeseries,
        "detail_table": detail_latency_table,
        "detail_check_table": detail_check_table
    }
