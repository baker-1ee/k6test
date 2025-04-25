import pandas as pd

def calculate_test_duration(df: pd.DataFrame) -> dict:
    """
    DataFrame 에서 'timestamp' 컬럼을 기준 으로 테스트 시작/종료 시각 및 총 소요 시간(초)을 계산

    Returns:
        {
            "start": 시작 시각 (timestamp),
            "end": 종료 시각 (timestamp),
            "seconds": 총 테스트 시간 (int, 초 단위)
        }
    """
    if "timestamp" not in df.columns:
        raise ValueError("DataFrame에 'timestamp' 컬럼이 없습니다.")

    start_time = df["timestamp"].min()
    end_time = df["timestamp"].max()
    duration = int((end_time - start_time).total_seconds())

    return {
        "start": start_time,
        "end": end_time,
        "seconds": duration
    }


def format_test_duration_title(test_duration: dict) -> str:
    duration_text = format_duration(test_duration['seconds'] * 1000)
    return f'{test_duration['start'].strftime("%Y.%m.%d %H:%M:%S")} ~ {test_duration['end'].strftime("%H:%M:%S")}, duration : {duration_text}'


def format_duration(ms: float) -> str:
    try:
        ms = float(ms)
    except (ValueError, TypeError):
        return "N/A"
    if ms >= 60_000:
        minutes = int(ms // 60_000)
        seconds = int((ms % 60_000) // 1000)
        return f"{minutes}m" if seconds == 0 else f"{minutes}m {seconds}s"
    elif ms >= 1000:
        return f"{ms / 1000:.2f}s"
    else:
        return f"{int(ms)}ms"


def format_bytes(value: float) -> str:
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "N/A"
    units = [("MB", 1024 ** 2), ("KB", 1024), ("B", 1)]
    for unit, factor in units:
        if value >= factor:
            return f"{value / factor:,.1f} {unit}"
    return "0 B"


def format_ratio(success: int, total: int) -> float:
    if total == 0:
        return 0
    ratio = (success / total) * 100
    return int(ratio) if ratio in (0, 100) else round(ratio, 1)


def determine_interval_seconds(duration_sec: int) -> int:
    if duration_sec <= 600:
        return 5
    elif duration_sec <= 1800:
        return 10
    elif duration_sec <= 3600:
        return 20
    else:
        return 30