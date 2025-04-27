from pathlib import Path
from datetime import datetime

import parser, data_processor, html_writer


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

    print(f"[INFO] Parsing CSV: {input_path}")
    df = parser.load_csv(input_path)

    print(f"[INFO] Processing data...")
    processed = data_processor.process_data(df)

    print(f"[INFO] Writing HTML report to: {html_output}")
    html_writer.generate_report(html_output, processed)

    # csv_output = Path("out") / f"{stem}_{timestamp}.csv"
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
    main('../k6/out/stg-cloud-be-load.csv')
