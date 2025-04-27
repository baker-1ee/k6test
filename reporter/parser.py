import pandas as pd
from pathlib import Path
from typing import Union


def load_csv(path: Union[str, Path]) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"[ERROR] File not found: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"[ERROR] Failed to parse CSV: {e}")

    # 핵심 컬럼 타입 정제
    df["metric_value"] = pd.to_numeric(df["metric_value"], errors="coerce")
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.tz_convert("Asia/Seoul")

    # NaN 행 제거
    df = df.dropna(subset=["metric_name", "metric_value", "timestamp"])

    # 필요한 열만 남기기
    keep_columns = [
        "metric_name",      # 어떤 메트릭 인지 (http_req_duration 등)
        "timestamp",        # 시분초
        "metric_value",     # 수치값
        "check",            # checks 이름
        "url",              # 요청 URL
        "status",           # HTTP 상태 코드
        "error"             # 에러 내용
    ]
    df = df[[col for col in keep_columns if col in df.columns]]

    return df
