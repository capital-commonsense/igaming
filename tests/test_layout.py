import pytest

from dc_igaming.layout import ribbon_path, spread_labels, stack


def test_spread_leaves_well_spaced_labels_alone():
    assert spread_labels([0, 50, 100], 30, -100, 200) == pytest.approx([0, 50, 100])


def test_spread_pushes_clustered_labels_apart_symmetrically():
    out = spread_labels([100, 100, 100], 30, 0, 300)
    assert out == pytest.approx([70, 100, 130])


def test_spread_respects_min_gap_order_and_bounds():
    desired = [10, 12, 13, 14, 200, 201]
    out = spread_labels(desired, 25, 0, 260)
    assert all(b - a >= 25 - 1e-9 for a, b in zip(out, out[1:], strict=False))
    assert out[0] >= 0 and out[-1] <= 260


def test_spread_clamps_at_bottom():
    out = spread_labels([95, 96, 97], 20, 0, 100)
    assert out[-1] == pytest.approx(100)
    assert out == pytest.approx([60, 80, 100])


def test_spread_rejects_impossible_and_unsorted():
    with pytest.raises(ValueError):
        spread_labels([0, 1, 2], 100, 0, 50)
    with pytest.raises(ValueError):
        spread_labels([5, 1], 1, 0, 50)
    assert spread_labels([], 10, 0, 1) == []


def test_ribbon_path_is_closed_and_hits_endpoints():
    d = ribbon_path(0, 10, 20, 100, 50, 60)
    assert d.startswith("M0,10 ") and d.endswith(" 0,20 Z")
    assert "100,50" in d and "L100,60" in d


def test_stack_with_gaps():
    s = stack(["a", "b", "c"], [10, 5, 1], top=100, gaps=[0, 4, 2])
    assert [(x.top, x.bottom) for x in s] == [(100, 110), (114, 119), (121, 122)]
    assert s[0].mid == 105 and s[1].height == 5
    with pytest.raises(ValueError):
        stack(["a"], [1, 2], 0)
