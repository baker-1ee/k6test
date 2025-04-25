import argparse
from pathlib import Path
from datetime import datetime

import utils, parser, analyzer, html_writer, csv_writer


def generate_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")


def main(input_path: str):
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"[ERROR] File not found: {input_file}")
        return

    timestamp = generate_timestamp()
    stem = input_file.stem  # 'stg_load_test'

    html_output = Path("out") / f"{stem}_{timestamp}.html"
    csv_output = Path("out") / f"{stem}_{timestamp}.csv"

    print(f"[INFO] Parsing CSV: {input_path}")
    df = parser.load_csv(input_path)

    print(f"[INFO] Analyzing summary data...")
    # 테스트 수행 시간 계산
    test_duration = utils.calculate_test_duration(df)

    df_total_req_duration = analyzer.calculate_durations_summary(df, 'http_req_duration')
    df_total_req_failures = analyzer.calculate_failures_summary(df)
    df_total_iteration_duration = analyzer.calculate_durations_summary(df, 'iteration_duration')
    df_total_data_sent = analyzer.calculate_total_transfer(df, 'data_sent')
    df_total_data_received = analyzer.calculate_total_transfer(df, 'data_received')
    df_total = analyzer.merge_summary([df_total_req_duration, df_total_req_failures, df_total_iteration_duration, df_total_data_sent, df_total_data_received])

    print(f"[INFO] Analyzing detail data...")
    df_req_duration = analyzer.calculate_durations(df, 'http_req_duration')
    df_req_failures = analyzer.calculate_failures(df)
    df_detail = analyzer.merge(df_req_duration, df_req_failures)


    print(f"[INFO] Writing HTML report to: {html_output}")
    html_writer.generate_report(html_output, test_duration, df_total, df_detail)
    #
    # print(f"[INFO] Writing CSV summary to: {csv_output}")
    # csv_writer.generate_report(stats, csv_output)
    #
    # print("[DONE] Report generation complete.")


if __name__ == "__main__":
    # arg_parser = argparse.ArgumentParser()
    # arg_parser.add_argument("input", help="Input CSV file path")
    # args = arg_parser.parse_args()
    #
    # main(args.input)
    main('../k6/out/stg-cloud-fe-stress.csv')