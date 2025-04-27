from pathlib import Path


def export_detail_tables_to_csv(output_dir: Path, stem: str, data: dict):
    """
    detail_table, detail_check_table 을 각각 CSV로 저장
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    detail_table_file = output_dir / f"{stem}_detail_table.csv"
    detail_check_table_file = output_dir / f"{stem}_detail_check_table.csv"

    data["detail_table"].to_csv(detail_table_file, index=False, encoding="utf-8-sig")
    data["detail_check_table"].to_csv(detail_check_table_file, index=False, encoding="utf-8-sig")

    print(f"[DONE] 상세 테이블 저장 완료: {detail_table_file}")
    print(f"[DONE] 체크 테이블 저장 완료: {detail_check_table_file}")
