from src.experiments.benchmark import build_benchmark_plan


def test_smoke_plan_contains_fixed_baseline_and_adaptive_mainline():
    plan = build_benchmark_plan("smoke")
    names = {(case.name, variant.name) for case, variant in plan}
    assert ("ring5_p2_b3", "exact") in names
    assert ("ring5_p2_b3", "boss_fixed_baseline") in names
    assert ("ring5_p2_b3", "boss_adaptive_mainline") in names


def test_representative_plan_contains_representative_cases():
    plan = build_benchmark_plan("representative")
    names = {(case.name, variant.name) for case, variant in plan}
    assert ("ring9_p3_b6", "exact") in names
    assert ("ring9_p3_b6", "boss_fixed_baseline") in names
    assert ("random9_p3_b5", "boss_adaptive_mainline") in names
    assert ("random9_p3_b5", "boss_adaptive_conservative") in names
