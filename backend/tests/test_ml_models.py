"""Week-8 and Week-11 QA: ML model training, accuracy targets, and prediction ranges."""
from __future__ import annotations

from app.ml import features, registry
from app.ml.predict import predict_account_health, score_open_deals


def test_all_three_models_trained():
    assert registry.model_exists("win_scorer")
    assert registry.model_exists("revenue_forecaster")
    assert registry.model_exists("health_classifier")


def test_win_scorer_metadata_and_target():
    _, meta = registry.load_model("win_scorer")
    assert meta["metric"] == "AUC-ROC"
    assert meta["algorithm"] in {"LogisticRegression", "RandomForest", "GradientBoosting"}
    # On seeded synthetic data with real signal the scorer should clear its target.
    assert meta["metric_value"] > 0.75, f"AUC below target: {meta}"
    assert meta["meets_target"] is True


def test_revenue_forecaster_metadata():
    _, meta = registry.load_model("revenue_forecaster")
    assert meta["metric"] == "MAPE"
    assert meta["algorithm"] in {"LinearRegression", "GradientBoosting"}
    assert meta["metric_value"] >= 0.0


def test_health_classifier_metadata_and_target():
    _, meta = registry.load_model("health_classifier")
    assert meta["metric"] == "F1-Score"
    assert meta["algorithm"] in {"DecisionTree", "RandomForest", "GradientBoosting"}
    assert meta["metric_value"] > 0.75, f"F1 below target: {meta}"
    assert meta["meets_target"] is True


def test_predictions_within_valid_ranges(db_session):
    from app import models

    scored = score_open_deals(db_session)
    assert scored["scored"] > 0
    for deal in db_session.query(models.Deal).filter(models.Deal.predicted_win_prob.isnot(None)):
        assert 0.0 <= deal.predicted_win_prob <= 1.0
        assert deal.predicted_revenue >= 0.0


def test_account_health_classification(db_session):
    res = predict_account_health(db_session)
    assert res["classified"] > 0
    assert isinstance(res["breakdown"], dict)
    assert len(res["breakdown"]) > 0


def test_feature_frame_has_expected_columns(db_session):
    df = features.build_deal_frame(db_session)
    for col in features.ALL_FEATURES:
        assert col in df.columns
    assert not df.empty


def test_account_feature_frame_has_expected_columns(db_session):
    df = features.build_account_frame(db_session)
    for col in features.HEALTH_FEATURES:
        assert col in df.columns
    assert not df.empty

