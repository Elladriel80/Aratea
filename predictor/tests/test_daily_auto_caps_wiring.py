"""Tests d'intégration légère du câblage PortfolioHeat dans daily_auto.

Stratégie : tester les deux helpers isolés (``_compute_current_bankroll``,
``_size_with_caps``) plutôt que de monter les mocks lourds nécessaires à
``_capture_one_bin`` (KalshiClient, OpenMeteoClient, EnsemblePredictor,
registry). Le comportement end-to-end sera observable au premier cron
post-merge via les logs.

Couvre :
  - Calcul correct du bankroll marqué-au-market depuis le ledger.
  - Fail-fast si bankroll sous seuil viable.
  - Sizing zéro quand les caps saturent (heat à 100 % du max).
  - Sizing normal sur portfolio vierge.
  - Skip + log explicite sur ``cap_atteint`` (via _capture_one_bin
    monkeypatché pour éviter les mocks Kalshi).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.simulation.clusters import BetContext
from src.simulation.sizing import (
    MAX_CLUSTER_EXPOSURE,
    MAX_FRACTION_PER_BET,
    MAX_PORTFOLIO_HEAT,
    PortfolioHeat,
)

# daily_auto est dans predictor/scripts/, conftest.py ajoute ce path.
import daily_auto


# --- Fixtures ledger -------------------------------------------------------
_HEADER = (
    "bet_id,placed_at_utc,market_ticker,event_ticker,target_date,side,"
    "stake_usd,entry_price,prob_model,prob_market_implied,edge,method,spec,"
    "resolved_at_utc,resolution,pnl_usd\n"
)


def _write_ledger(path: Path, rows: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_HEADER + "".join(rows), encoding="utf-8")


def _settled_row(bet_id: str, pnl: float) -> str:
    return (
        f"{bet_id},2026-05-10T17:00:00Z,KXLOWTNYC-26MAY11-B50.5,"
        f"KXLOWTNYC-26MAY11,2026-05-11,NO,100.0,0.36,0.146,0.36,-0.21,"
        f"ensemble,test,2026-05-12T12:00:00Z,no,{pnl}\n"
    )


# --- _compute_current_bankroll --------------------------------------------
def test_compute_current_bankroll_sums_pnl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "paper_bets.csv"
    _write_ledger(
        path,
        [
            _settled_row("a", pnl=50.0),
            _settled_row("b", pnl=-30.0),
            _settled_row("c", pnl=100.0),
        ],
    )
    monkeypatch.setattr(daily_auto, "LEDGER_PATH", path)
    # starting_bankroll = 1000 (config par défaut), P&L = 120 → 1120
    assert daily_auto._compute_current_bankroll() == pytest.approx(1120.0)


def test_compute_current_bankroll_ignores_unresolved(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "paper_bets.csv"
    unresolved = (
        "x,2026-05-15T17:00:00Z,KXLOWTNYC-26MAY16-B50.5,"
        "KXLOWTNYC-26MAY16,2026-05-16,NO,100.0,0.36,0.146,0.36,-0.21,"
        "ensemble,test,,,\n"
    )
    _write_ledger(path, [_settled_row("a", pnl=50.0), unresolved])
    monkeypatch.setattr(daily_auto, "LEDGER_PATH", path)
    # Le pari non-resolved a pnl_usd=None → exclu du sum. Bankroll = 1050.
    assert daily_auto._compute_current_bankroll() == pytest.approx(1050.0)


def test_compute_current_bankroll_fails_fast_below_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "paper_bets.csv"
    # Pertes massives : -900 → bankroll = 100 < 200 = MIN_VIABLE.
    _write_ledger(path, [_settled_row("a", pnl=-900.0)])
    monkeypatch.setattr(daily_auto, "LEDGER_PATH", path)
    with pytest.raises(RuntimeError, match="Bankroll dégradé sous seuil"):
        daily_auto._compute_current_bankroll()


# --- _size_with_caps ------------------------------------------------------
def test_size_with_caps_returns_zero_when_heat_saturated() -> None:
    portfolio = PortfolioHeat()
    # 2 paris à 5 % chacun → heat 10 % = MAX_PORTFOLIO_HEAT.
    portfolio.register(BetContext(
        "a", "KXLOWTNYC-26MAY15", "NE", date(2026, 5, 15), 0.05,
    ))
    portfolio.register(BetContext(
        "b", "KXLOWTLAX-26MAY15", "SW", date(2026, 5, 15), 0.05,
    ))
    size, ctx = daily_auto._size_with_caps(
        target={"edge": 0.20, "yes_mid": 0.50, "p_champion": 0.70},
        event_ticker="KXLOWTCHI-26MAY17",  # cluster MW, vierge
        current_bankroll=1000.0,
        portfolio=portfolio,
        settlement_date=date(2026, 5, 17),
        bet_id="new-bet-id",
    )
    assert size == 0.0
    assert ctx is None


def test_size_with_caps_returns_per_trade_cap_on_empty_portfolio() -> None:
    portfolio = PortfolioHeat()
    size, ctx = daily_auto._size_with_caps(
        target={"edge": 0.20, "yes_mid": 0.50, "p_champion": 0.70},
        event_ticker="KXLOWTNYC-26MAY17",
        current_bankroll=1000.0,
        portfolio=portfolio,
        settlement_date=date(2026, 5, 17),
        bet_id="x",
    )
    # Bankroll 1000, edge 0.20, Kelly 0.25 → fraction 0.10, capée à 5 % = $50.
    assert size == 50.0
    assert ctx is not None
    assert ctx.spatial_cluster == "NE"
    assert ctx.market_ticker == "KXLOWTNYC-26MAY17"  # sans strike


def test_size_with_caps_uses_event_ticker_not_market_ticker() -> None:
    """Si l'impl confondait event_ticker et market_ticker, le parser
    exploserait sur ``-B50.5`` non-parseable. Test garde-fou."""
    portfolio = PortfolioHeat()
    # On simule ce que daily_auto fait : target['ticker'] est le
    # market_ticker (avec strike), event_ticker est passé séparément.
    size, ctx = daily_auto._size_with_caps(
        target={
            "ticker": "KXLOWTNYC-26MAY17-B50.5",  # market_ticker avec strike
            "edge": 0.20, "yes_mid": 0.50, "p_champion": 0.70,
        },
        event_ticker="KXLOWTNYC-26MAY17",  # sans strike
        current_bankroll=1000.0,
        portfolio=portfolio,
        settlement_date=date(2026, 5, 17),
        bet_id="x",
    )
    assert size > 0.0
    assert ctx is not None


# --- _capture_one_bin : cap_atteint path (test plus large) ----------------
# --- Phase 1 portfolio caps -----------------------------------------------
def test_phase1_caps_are_strictly_more_permissive_than_strict_defaults() -> None:
    """Contrat Phase 1 : on prend MOINS de risque par pari (per-trade plus
    petit) pour pouvoir en ouvrir BEAUCOUP PLUS simultanément (heat et
    cluster plus larges). Si quelqu'un inverse ces inégalités, le throughput
    s'effondre — ce test garde-fou empêche un revert silencieux."""
    assert daily_auto.PHASE1_MAX_FRACTION_PER_BET < MAX_FRACTION_PER_BET, (
        "Phase 1 doit shrinker la taille par pari pour mécaniquement en "
        "permettre davantage en simultané sous une heat élargie."
    )
    assert daily_auto.PHASE1_MAX_PORTFOLIO_HEAT > MAX_PORTFOLIO_HEAT, (
        "Phase 1 doit élargir la heat globale pour ramasser du N."
    )
    assert daily_auto.PHASE1_MAX_CLUSTER_EXPOSURE > MAX_CLUSTER_EXPOSURE, (
        "Phase 1 doit élargir le cap par cluster pour ne pas étrangler "
        "une région trop tôt."
    )
    # Sanity : les nouveaux paramètres restent dans [0, 1] et la heat
    # globale couvre au moins ~10 paris simultanés au per-trade nouveau.
    assert 0 < daily_auto.PHASE1_MAX_FRACTION_PER_BET <= 1
    assert 0 < daily_auto.PHASE1_MAX_PORTFOLIO_HEAT <= 1
    assert 0 < daily_auto.PHASE1_MAX_CLUSTER_EXPOSURE <= 1
    assert (
        daily_auto.PHASE1_MAX_PORTFOLIO_HEAT
        / daily_auto.PHASE1_MAX_FRACTION_PER_BET
        >= 10
    ), "Phase 1 vise au moins 10 paris simultanés ; sinon réajuster."


def test_phase1_caps_unblock_a_ledger_saturated_under_strict_defaults(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Régression du symptôme observé sur le ledger 2026-05-18 → 0 captures
    19 et 20 mai. Stratégie : on construit deux paris non-settled de 5 %
    chacun (= 10 % heat = MAX_PORTFOLIO_HEAT). En Phase 2 strict, le
    portefeuille reconstruit a remaining_capacity = 0. En Phase 1 large
    (heat 30 %), il reste de la place pour de nouvelles captures."""
    path = tmp_path / "paper_bets.csv"
    # 2 paris OUVERTS (resolved_at_utc vide) à 5 % du bankroll de 1000.
    unresolved_a = (
        "a,2026-05-18T19:44:41Z,KXLOWTNYC-26MAY19-B71.5,"
        "KXLOWTNYC-26MAY19,2026-05-19,NO,50.0,0.4,0.06,0.4,-0.34,"
        "ensemble,test,,,\n"
    )
    unresolved_b = (
        "b,2026-05-18T19:44:49Z,KXLOWTLAX-26MAY19-B57.5,"
        "KXLOWTLAX-26MAY19,2026-05-19,NO,50.0,0.45,0.25,0.45,-0.20,"
        "ensemble,test,,,\n"
    )
    _write_ledger(path, [unresolved_a, unresolved_b])

    bankroll = 1000.0

    # Reconstruction Phase 2 stricte (les defaults du module sizing) :
    # heat 10 % saturée → 0 capacité résiduelle sur les nouveaux paris.
    strict_portfolio = PortfolioHeat.from_ledger(path, bankroll)
    assert strict_portfolio.total_open_fraction() == pytest.approx(0.10)
    # Cluster MW vierge ; le cap heat doit binder à 0.
    assert strict_portfolio.remaining_capacity(
        "MW", date(2026, 5, 20)
    ) == pytest.approx(0.0)

    # Reconstruction Phase 1 (les valeurs de daily_auto) : heat 30 %,
    # cluster 15 %, per-trade 2 % → on devrait avoir au moins
    # per_trade=2 % de room sur un cluster vierge.
    phase1_portfolio = PortfolioHeat.from_ledger(
        path,
        bankroll,
        max_portfolio_heat=daily_auto.PHASE1_MAX_PORTFOLIO_HEAT,
        max_cluster_exposure=daily_auto.PHASE1_MAX_CLUSTER_EXPOSURE,
        max_fraction_per_bet=daily_auto.PHASE1_MAX_FRACTION_PER_BET,
    )
    assert phase1_portfolio.total_open_fraction() == pytest.approx(0.10)
    room = phase1_portfolio.remaining_capacity("MW", date(2026, 5, 20))
    assert room == pytest.approx(
        daily_auto.PHASE1_MAX_FRACTION_PER_BET
    ), (
        "Sur cluster vierge et heat à 10 %, c'est le per-trade Phase 1 "
        "qui doit binder ; sinon les nouvelles captures restent bloquées."
    )


def test_capture_one_bin_skips_and_logs_on_cap_atteint(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Quand le portefeuille sature, _capture_one_bin renvoie skip et logge
    explicitement la raison. Vérifie le contrat de PR #85 (refus pur)."""
    # Portfolio saturé sur cluster MW pour bloquer le nouveau bet CHI.
    portfolio = PortfolioHeat()
    portfolio.register(BetContext(
        "a", "KXLOWTNYC-26MAY15", "NE", date(2026, 5, 15), 0.05,
    ))
    portfolio.register(BetContext(
        "b", "KXLOWTLAX-26MAY15", "SW", date(2026, 5, 15), 0.05,
    ))

    # Mock minimal de l'event Kalshi pour atteindre _size_with_caps.
    fake_market = MagicMock(ticker="KXLOWTCHI-26MAY17-B40.5")
    fake_ev = MagicMock(
        event_ticker="KXLOWTCHI-26MAY17",
        markets=[fake_market],
        title="fake",
    )
    fake_spec = MagicMock(target_date=date(2026, 5, 17))
    fake_spec.describe = lambda: "fake spec"
    monkeypatch.setattr(daily_auto, "parse_market", lambda m: fake_spec)

    target = {
        "ticker": "KXLOWTCHI-26MAY17-B40.5",
        "yes_mid": 0.5, "p_champion": 0.7,
        "edge": 0.20, "abs_edge": 0.20,
        "yes_bid": 0.48, "yes_ask": 0.52, "spread": 0.04,
    }

    result = daily_auto._capture_one_bin(
        ev=fake_ev, target=target, weather=None, registry={"current_champion": "x"},
        portfolio=portfolio, current_bankroll=1000.0, dry_run=True,
    )

    assert result["captured"] is False
    assert result["reason"] == "cap_atteint"
    captured = capsys.readouterr().out
    assert "[skip]" in captured
    assert "cap atteint" in captured.lower()
    # Vérifie aussi qu'on log le heat % et le bankroll pour debug.
    assert "heat=" in captured
    assert "bankroll=" in captured
