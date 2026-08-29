from app.main import risk_for


def test_high_risk_by_case_count():
    assert risk_for(35, 20)[0] == "high"


def test_medium_risk_by_growth():
    assert risk_for(12, 8)[0] == "medium"


def test_low_risk():
    assert risk_for(8, 8)[0] == "low"
