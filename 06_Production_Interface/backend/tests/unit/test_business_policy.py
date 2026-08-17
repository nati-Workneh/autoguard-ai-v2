from pathlib import Path

from backend.business_policy import business_action, load_business_policy


def test_policy_boundaries():
    policy = load_business_policy()
    threshold = policy["business_threshold"]
    assert business_action(threshold - 0.01, policy) == "Automatic processing eligible"
    assert business_action(threshold, policy) == "Manual review recommended"
    assert business_action(threshold + 0.05, policy) == "Manual review recommended"


def test_invalid_policy_fails(tmp_path: Path):
    bad_policy = tmp_path / "policy.json"
    bad_policy.write_text('{"business_threshold": 2}')

    try:
        load_business_policy(bad_policy)
    except ValueError:
        return
    assert False, "expected ValueError for an out-of-range business_threshold"
