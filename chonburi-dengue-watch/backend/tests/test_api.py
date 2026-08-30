from fastapi.testclient import TestClient

from app.database import connection, init_db
from app.main import app, risk_for

client = TestClient(app)
init_db()


def test_high_risk_by_case_count():
    assert risk_for(35, 20)[0] == "high"


def test_medium_risk_by_growth():
    assert risk_for(12, 8)[0] == "medium"


def test_low_risk():
    assert risk_for(8, 8)[0] == "low"


def test_csv_upload_summary():
    csv = (
        "record_date,district,actual_cases,rainfall,temperature,humidity\n"
        "2024-01-01,พัทยา,10,20,30,60\n"
        "2024-01-02,พัทยา,15,30,31,65\n"
        "2024-01-03,ศรีราชา,12,25,29,70\n"
        "2024-01-04,ศรีราชา,8,15,28,55\n"
    ).encode('utf-8')
    response = client.post('/api/upload-csv', files={'file': ('sample.csv', csv, 'text/csv')})
    assert response.status_code == 200
    data = response.json()
    assert data['summary']['total_cases'] == 45
    assert data['summary']['cleaned_rows'] == 4
    assert len(data['preview']) == 4
    assert 'chart_data' in data
    assert data['chart_data'][0]['value'] == 10
    assert 'trend' in data['analytics']
    assert 'heatmap' in data['analytics']
    assert data['analytics']['trend'][0]['label'] == '2024-01-01'
    assert data['analytics']['heatmap'][0]['district'] in {'พัทยา', 'ศรีราชา'}


def test_dashboard_includes_live_timestamp():
    response = client.get('/api/dashboard')
    assert response.status_code == 200
    data = response.json()
    assert 'updated_at' in data
    assert 'T' in data['updated_at']


def test_websocket_is_available():
    with client.websocket_connect('/ws') as websocket:
        message = websocket.receive_json()
        assert 'updated_at' in message
        assert message['event'] == 'dashboard'


def test_prediction_rejects_unknown_weather():
    response = client.post('/api/predict', json={
        'district': 'เมืองชลบุรี', 'record_date': '2026-08-30',
        'weather_condition': 'พายุที่ระบบไม่รู้จัก', 'rainfall': 20,
        'temperature': 30, 'humidity': 70, 'wind_speed': 8,
        'previous_cases': 5,
    })
    assert response.status_code == 422


def test_csv_rejects_invalid_numeric_values():
    csv = b'record_date,district,actual_cases,rainfall,temperature,humidity\n2024-01-01,A,abc,20,30,60\n'
    response = client.post('/api/upload-csv', files={'file': ('invalid.csv', csv, 'text/csv')})
    assert response.status_code == 400


def test_reset_requires_admin_token(monkeypatch):
    monkeypatch.setattr('app.main.ADMIN_TOKEN', 'test-secret')
    assert client.delete('/api/observations').status_code == 403
    assert client.delete('/api/observations', headers={'X-Admin-Token': 'wrong'}).status_code == 403


def test_dashboard_summary_uses_latest_row_from_every_district():
    init_db()
    with connection() as db:
        db.execute('DELETE FROM observations')
        for index in range(90):
            db.execute(
                '''INSERT INTO observations (district, record_date, period_type, actual_cases,
                   weather_condition, rainfall, temperature, humidity, wind_speed,
                   predicted_cases, risk_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                ('เมืองชลบุรี', f'2025-{(index // 28) + 1:02d}-{(index % 28) + 1:02d}', 'weekly', index,
                 'แจ่มใส', 1, 30, 60, 5, index, 'low'),
            )
        db.execute(
            '''INSERT INTO observations (district, record_date, period_type, actual_cases,
               weather_condition, rainfall, temperature, humidity, wind_speed,
               predicted_cases, risk_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            ('ศรีราชา', '2024-01-01', 'weekly', 7, 'แจ่มใส', 1, 30, 60, 5, 8, 'medium'),
        )
    data = client.get('/api/dashboard?limit=80').json()
    assert data['summary']['reporting_districts'] == 2
    assert any(row['district'] == 'ศรีราชา' for row in data['alerts'])
