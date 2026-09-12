"""P(bin) = part des membres, sans cloche."""
from src.truth.synthetic_bins import Bin, prob_in_bin_members, prob_in_bin_members_models


def test_fraction_counts_members_in_the_2f_bin():
    vals = [74.2, 75.4, 76.1, 77.4, 80.0]
    b = Bin(76, 77)
    assert prob_in_bin_members(vals, b) == 2 / 5
    assert prob_in_bin_members([], b) == 0.0
    assert prob_in_bin_members([76.0], Bin(None, 75)) == 0.0
    assert prob_in_bin_members([76.0], Bin(76, None)) == 1.0


def test_equal_weight_per_model_not_per_member():
    # 3 membres dans le bin côté petit modèle, 0 côté gros modèle → 0.5
    per = {
        "tiny": [76.0, 76.2, 76.4],
        "huge": [90.0] * 30,
    }
    assert abs(prob_in_bin_members_models(per, Bin(76, 77)) - 0.5) < 1e-12
    assert prob_in_bin_members_models({}, Bin(76, 77)) == 0.0
