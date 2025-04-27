from pathlib import Path
from datetime import datetime

import parser, data_processor, html_writer, csv_writer


def generate_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def print_summary_to_console(data: dict):
    print("\n===== HTTP 요청 요약 =====")
    for key, value in data["summary_http_request"].items():
        print(f"{key:20}: {value}")

    print("\n===== HTTP 요청 Duration 요약 (ms) =====")
    for key, value in data["summary_http_req_duration"].items():
        print(f"{key:20}: {value}")

    print("\n===== Iteration Duration 요약 (ms) =====")
    for key, value in data["summary_iteration_duration"].items():
        print(f"{key:20}: {value}")

    print("\n===== 네트워크 사용량 요약 =====")
    for key, value in data["summary_network_usage"].items():
        print(f"{key:20}: {value}")


def main(input_path: str):
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"[ERROR] File not found: {input_file}")
        return
    timestamp = generate_timestamp()
    stem = input_file.stem  # 'stg_load_test'
    html_output = Path("out") / f"{stem}_{timestamp}.html"
    csv_output_dir = Path("out")

    print(f"[INFO] Parsing CSV: {input_path}")
    df = parser.load_csv(input_path)

    print(f"[INFO] Processing data...")
    processed = data_processor.process_data(df)

    print(f"[INFO] Writing HTML report to: {html_output}")
    html_writer.generate_report(html_output, processed)

    print(f"[INFO] Writing detail CSV files to: {csv_output_dir}")
    csv_writer.export_detail_tables_to_csv(csv_output_dir, f"{stem}_{timestamp}", processed)

    print("[DONE] Report generation complete.")

    print_summary_to_console(processed)


if __name__ == "__main__":
    # arg_parser = argparse.ArgumentParser()
    # arg_parser.add_argument("input", help="Input CSV file path")
    # args = arg_parser.parse_args()
    #
    # main(args.input)
    main('../k6/out/stg-cloud-be-load.csv')
