import pandas as pd
from utils import format_test_duration_title, format_card_value

def generate_card(title, data: dict, icon="📊") -> str:
    """
    카드 하나를 HTML 로 변환
    Args:
        title: 카드 제목
        data: 표시할 dict 데이터
        icon: 카드에 붙일 이모지 아이콘
    """
    rows = ''.join(
        f'<tr><td style="text-align:left;"><b>{key}</b></td><td style="text-align:right;">{value}</td></tr>'
        for key, value in data.items()
    )

    return f"""
    <div class="card">
        <div class="card-title">{icon} {title}</div>
        <table>{rows}</table>
    </div>
    """

def generate_error_card(errors_text: str) -> str:
    """
    errors_text 를 받아서 에러 카드 HTML 을 반환
    만약 errors_text 가 "-" 이면 빈 문자열("") 반환
    """
    if not errors_text or errors_text == "-":
        return ""

    return f"""
    <div class="section-gap">
        <div class="card-full">
            <div class="card-title">❗ 에러 요약</div>
            <div style="padding: 1rem; white-space: pre-wrap;">{errors_text}</div>
        </div>
    </div>
    """

def generate_detail_table(df, title="상세 테이블") -> str:
    if df.empty:
        return f"<div class='card-full'><div class='card-title'>{title}</div><p>데이터 없음</p></div>"

    headers = ''.join(f"<th>{col}</th>" for col in df.columns)
    rows = ''
    for _, row in df.iterrows():
        ratio = float(row.get("ratio", 100))  # ratio 컬럼 없을 수도 있으니까 기본값 100

        if ratio == 100:
            color = "green"
        elif ratio < 100:
            color = "orangered"
        elif ratio <= 75:
            color = "darkred"

        # <tr style> 에 색상 적용
        row_html = ''.join(f"<td>{row[col]}</td>" for col in df.columns)
        rows += f'<tr style="color: {color};">{row_html}</tr>'

    return f"""
    <div class="card-full">
        <div class="card-title">{title}</div>
        <table>
            <thead><tr>{headers}</tr></thead>
            <tbody>{rows}</tbody>
        </table>
    </div>
    """

def generate_chartjs_vus_chart(df_vus_timeseries: pd.DataFrame) -> str:
    """
    Chart.js를 이용 해서 VU(Virtual Users) 시계열 그래프 HTML 코드 생성
    Args:
        df_vus_timeseries: 'timestamp', 'vus' 컬럼을 가진 DataFrame
    Returns:
        VU 시계열 Chart.js HTML 코드
    """
    if df_vus_timeseries.empty:
        return "<p>VU 데이터가 없습니다.</p>"

    labels = df_vus_timeseries["timestamp"].dt.strftime("%H:%M:%S").tolist()
    vus_data = df_vus_timeseries["vus"].astype(int).tolist()

    chart_js = f"""
    <div class="card-full">
        <div class="card-title">👥 가상 사용자(VU) 시계열</div>
        <canvas id="vusChart" height="60"></canvas>
    </div>
    <script>
    const vusCtx = document.getElementById('vusChart').getContext('2d');
    new Chart(vusCtx, {{
        type: 'line',
        data: {{
            labels: {labels},
            datasets: [{{
                label: 'VUs',
                data: {vus_data},
                borderColor: 'rgba(255, 159, 64, 0.8)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                fill: false,
                tension: 0.1,
                pointRadius: 2
            }}]
        }},
        options: {{
            responsive: true,
            plugins: {{
                title: {{
                    display: true,
                    text: 'VU(가상 사용자) 시계열'
                }},
                legend: {{
                    display: false
                }}
            }},
            scales: {{
                x: {{
                    title: {{
                        display: true,
                        text: '시간'
                    }}
                }},
                y: {{
                    title: {{
                        display: true,
                        text: '사용자 수'
                    }},
                    beginAtZero: true,
                    ticks: {{
                        precision: 0
                    }}
                }}
            }}
        }}
    }});
    </script>
    """

    return chart_js


def generate_chartjs_latency_chart(df_latency_timeseries: pd.DataFrame) -> str:
    """
    Chart.js를 이용 해서 HTTP Request Latency 시계열 그래프 HTML 코드 생성
    Args:
        df_latency_timeseries: 'timestamp', 'avg', 'min', 'max', 'p50', 'p90', 'p95', 'p99' 컬럼을 가진 DataFrame
    Returns:
        HTTP 요청 지연 시계열 Chart.js HTML 코드
    """
    if df_latency_timeseries.empty:
        return "<p>Latency 데이터가 없습니다.</p>"

    labels = df_latency_timeseries["timestamp"].dt.strftime("%H:%M:%S").tolist()

    colors = {
        "avg": "rgba(0, 200, 83, 0.6)",        # 초록 (평균)
        "min": "rgba(255, 235, 59, 0.6)",      # 노랑 (최소)
        "max": "rgba(244, 67, 54, 0.6)",       # 빨강 (최대)
        "p50": "rgba(100, 181, 246, 0.4)",     # 연한 파랑 (50 퍼센타일)
        "p90": "rgba(66, 165, 245, 0.5)",      # 중간 파랑 (90 퍼센타일)
        "p95": "rgba(30, 136, 229, 0.6)",      # 진한 파랑 (95 퍼센타일)
        "p99": "rgba(21, 101, 192, 0.7)"       # 아주 진한 파랑 (99 퍼센타일)
    }

    datasets = []
    for col, color in colors.items():
        if col in df_latency_timeseries.columns:
            datasets.append(f"""
            {{
                label: '{col}',
                data: {df_latency_timeseries[col].astype(int).tolist()},
                borderColor: '{color}',
                backgroundColor: '{color}',
                fill: false,
                tension: 0.1,
                pointRadius: 2
            }}
            """)

    chart_js = f"""
    <div class="card-full">
        <div class="card-title">📈 HTTP 요청 지연 시계열</div>
        <canvas id="latencyChart" height="100"></canvas>
    </div>
    <script>
    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    new Chart(latencyCtx, {{
        type: 'line',
        data: {{
            labels: {labels},
            datasets: [{','.join(datasets)}]
        }},
        options: {{
            responsive: true,
            interaction: {{
                mode: 'index',
                intersect: false
            }},
            plugins: {{
                title: {{
                    display: true,
                    text: 'HTTP 요청 지연 시계열'
                }},
                legend: {{
                    position: 'top'
                }}
            }},
            scales: {{
                x: {{
                    title: {{
                        display: true,
                        text: '시간'
                    }}
                }},
                y: {{
                    title: {{
                        display: true,
                        text: '지연 시간 (ms)'
                    }}
                }}
            }}
        }}
    }});
    </script>
    """

    return chart_js


def generate_report(output_path, data: dict):
    """
    최종 HTML Report 생성
    Args:
        output_path: 저장할 HTML 파일 경로
        data: process_data()의 결과 dict
    """

    # 카드별 로 준비
    card_http_summary = generate_card("HTTP 요청 요약", data["summary_http_request"], icon="📊")
    card_http_req_duration = generate_card("HTTP 요청 Duration (ms)", data["summary_http_req_duration"], icon="🕐")
    card_iteration_duration = generate_card("Iteration Duration (ms)", data["summary_iteration_duration"], icon="🕐")
    card_network_usage = generate_card("네트워크 사용량", data["summary_network_usage"], icon="📡")
    card_errors_html = generate_error_card(data["summary_http_errors"])

    # 시계열 차트 준비
    chart_vus = generate_chartjs_vus_chart(data["chart_vus_timeseries"])
    chart_latency = generate_chartjs_latency_chart(data["chart_latency_timeseries"])

    # 디테일 테이블 준비
    detail_latency_table_html = generate_detail_table(data["detail_table"], title="📈 URL 별 지연 시간 요약")
    detail_check_table_html = generate_detail_table(data["detail_check_table"], title="✅ Check 결과 요약")

    # 최종 HTML 조합
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>K6 성능 테스트 리포트</title>
        <script src="assets/js/chart.min.js"></script>
        <link rel="stylesheet" href="assets/css/style.css">
    </head>
    <body>
        <h1>K6 Performance Test Report</h1>
        <h3>{format_test_duration_title(data["test_duration"])}</h3>
        
        <div class="container">
            {card_http_summary}
            {card_http_req_duration}
            {card_iteration_duration}
            {card_network_usage}
        </div>
        
            {card_errors_html}

        <div class="section-gap">
            {chart_vus}
        </div>

        <div class="section-gap">
            {chart_latency}
        </div>

        <div class="section-gap">
            {detail_latency_table_html}
        </div>

        <div class="section-gap">
            {detail_check_table_html}
        </div>
    </body>
    </html>
    """

    output_path.write_text(html_content, encoding="utf-8")
    print(f"[DONE] HTML 리포트 생성 완료: {output_path}")
