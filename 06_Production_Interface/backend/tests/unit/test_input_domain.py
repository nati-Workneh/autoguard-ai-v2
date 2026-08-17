"""Unit tests for backend/input_domain.py -- the single source of truth for
the model's supported numeric ranges (verified against the 50,000-row dataset:
PAST_ACCIDENTS 0-15, SPEEDING_VIOLATIONS 0-22, DUIS 0-6)."""

from __future__ import annotations

from backend.input_domain import MODEL_INPUT_DOMAIN, check_out_of_distribution


class TestDomainBounds:
    def test_bounds_match_the_verified_dataset_ranges(self):
        assert MODEL_INPUT_DOMAIN["past_accidents"] == {"min": 0, "max": 15}
        assert MODEL_INPUT_DOMAIN["speeding_violations"] == {"min": 0, "max": 22}
        assert MODEL_INPUT_DOMAIN["duis"] == {"min": 0, "max": 6}


class TestCheckOutOfDistribution:
    def test_all_in_domain_returns_no_violations(self):
        violations = check_out_of_distribution(past_accidents=0, speeding_violations=0, duis=0)
        assert violations == []

    def test_boundary_maximums_are_accepted(self):
        violations = check_out_of_distribution(past_accidents=15, speeding_violations=22, duis=6)
        assert violations == []

    def test_one_over_boundary_is_flagged(self):
        violations = check_out_of_distribution(past_accidents=16, speeding_violations=22, duis=6)
        assert [v.field for v in violations] == ["past_accidents"]
        assert violations[0].supported_min == 0
        assert violations[0].supported_max == 15

    def test_speeding_violations_over_boundary_is_flagged(self):
        violations = check_out_of_distribution(past_accidents=0, speeding_violations=23, duis=0)
        assert [v.field for v in violations] == ["speeding_violations"]

    def test_duis_over_boundary_is_flagged(self):
        violations = check_out_of_distribution(past_accidents=0, speeding_violations=0, duis=7)
        assert [v.field for v in violations] == ["duis"]

    def test_extreme_multi_field_input_flags_every_field(self):
        violations = check_out_of_distribution(past_accidents=32, speeding_violations=32, duis=13)
        assert {v.field for v in violations} == {"past_accidents", "speeding_violations", "duis"}
        by_field = {v.field: v for v in violations}
        assert by_field["past_accidents"].value == 32
        assert by_field["speeding_violations"].value == 32
        assert by_field["duis"].value == 13

    def test_negative_values_are_also_flagged(self):
        violations = check_out_of_distribution(past_accidents=-1, speeding_violations=0, duis=0)
        assert [v.field for v in violations] == ["past_accidents"]

    def test_unknown_field_names_are_ignored(self):
        violations = check_out_of_distribution(not_a_real_field=999)
        assert violations == []
