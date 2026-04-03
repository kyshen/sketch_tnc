from src.experiments.benchmark import build_benchmark_plan


def test_build_benchmark_plan_contains_exact_and_implicit_variants():
    plan = build_benchmark_plan("smoke")
    names = {(case.name, variant.name) for case, variant in plan}
    assert ("ring5_p2_b3_r2", "exact") in names
    assert ("ring5_p2_b3_r2", "boss_selective_implicit") in names
    assert ("ring5_p2_b3_r2", "boss_force_implicit") in names


def test_rank_sweep_plan_contains_multiple_ranks():
    plan = build_benchmark_plan("rank_sweep")
    names = {(case.name, variant.name) for case, variant in plan}
    assert ("ring7_p3_b6_r2", "exact") in names
    assert ("ring7_p3_b6_r2", "boss_selective_explicit_r2") in names
    assert ("ring7_p3_b6_r2", "boss_selective_implicit_r8") in names


def test_adaptive_schedule_plan_contains_schedule_variants():
    plan = build_benchmark_plan("adaptive_schedule")
    names = {(case.name, variant.name) for case, variant in plan}
    assert ("ring7_p3_b6_r2", "boss_adaptive_flat") in names
    assert ("random7_p3_b5_r2", "boss_adaptive_depth_open") in names
