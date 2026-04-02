from src.experiments.benchmark import build_benchmark_plan


def test_build_benchmark_plan_contains_exact_and_implicit_variants():
    plan = build_benchmark_plan("smoke")
    names = {(case.name, variant.name) for case, variant in plan}
    assert ("ring5_p2_b3_r2", "exact") in names
    assert ("ring5_p2_b3_r2", "boss_selective_implicit") in names
    assert ("ring5_p2_b3_r2", "boss_force_implicit") in names
