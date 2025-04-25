# charts.py
import pandas as pd

def generate_chartjs_latency_chart(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p>No latency trend data available.</p>"

    labels = df["timestamp"].dt.strftime("%H:%M:%S").tolist()
    datasets = []
    colors = {
        "avg": "rgba(0, 200, 83, 0.6)",
        "min": "rgba(255, 235, 59, 0.6)",
        "max": "rgba(244, 67, 54, 0.6)",
        "p50": "rgba(100, 181, 246, 0.4)",
        "p90": "rgba(66, 165, 245, 0.5)",
        "p95": "rgba(30, 136, 229, 0.6)",
        "p99": "rgba(21, 101, 192, 0.7)"
    }

    for col, color in colors.items():
        if col in df.columns:
            datasets.append(f'''
            {{
                label: '{col}',
                data: {df[col].round(2).tolist()},
                borderColor: '{color}',
                backgroundColor: '{color}',
                fill: false,
                tension: 0.1,
                pointRadius: 2
            }}''')

    return f'''
    <div class="card-full">
        <div class="card-title">📈 HTTP request latency</div>
        <canvas id="latencyChart" height="100"></canvas>
    </div>
    <script>
    const ctx = document.getElementById('latencyChart').getContext('2d');
    new Chart(ctx, {{
        type: 'line',
        data: {{
            labels: {labels},
            datasets: [{','.join(datasets)}]
        }},
        options: {{
            responsive: true,
            interaction: {{ mode: 'index', intersect: false }},
            plugins: {{
                title: {{ display: true, text: 'HTTP request latency' }},
                legend: {{ position: 'top' }}
            }},
            scales: {{
                x: {{ title: {{ display: true, text: 'time' }} }},
                y: {{ title: {{ display: true, text: 'latency (ms)' }} }}
            }}
        }}
    }});
    </script>
    '''

def generate_chartjs_vus_chart(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p>No VUs data available.</p>"

    df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")
    labels = df["time"].tolist()
    data = df["vus"].tolist()

    return f'''
    <div class="card-full">
        <div class="card-title">👥 VU (Virtual User)</div>
        <canvas id="vusChart" height="60"></canvas>
    </div>
    <script>
    const vusCtx = document.getElementById('vusChart').getContext('2d');
    new Chart(vusCtx, {{
        type: 'line',
        data: {{ labels: {labels}, datasets: [{{
            label: 'VUs',
            data: {data},
            borderColor: 'rgba(255, 159, 64, 0.8)',
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            fill: false,
            tension: 0.1,
            pointRadius: 2
        }}] }},
        options: {{
            responsive: true,
            plugins: {{
                title: {{ display: true, text: 'VU(virtual user)' }},
                legend: {{ display: false }}
            }},
            scales: {{
                x: {{ title: {{ display: true, text: '시간' }} }},
                y: {{
                    title: {{ display: true, text: '사용자 수' }},
                    beginAtZero: true,
                    ticks: {{ precision: 0 }}
                }}
            }}
        }}
    }});
    </script>
    '''
