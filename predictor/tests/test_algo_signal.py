"""Tests du marqueur ``algo_signal`` (Phase 1 apprentissage).

Couvre :
  - PaperBet : défaut "bet", round-trip Ledger conserve la colonne.
  - Migration auto d'un ancien ledger 16 colonnes (Ledger + live_run).
  - _select_control_bins : sélectionne des bins sous le seuil, exclut les
    bins-paris, respecte n.
  - _capture_one_bin(algo_signal="no_bet") : mise nulle, pas de register
    portefeuille, marqueur propagé.
  - _paper_bets_summary : P&L et compteur Phase 1 = "bet" seuls ; groupe
    de contrôle séparé.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

import daily_auto
import live_run
import build_dashboard_manifest as bdm
from src.simulation.ledger import Ledger, PaperBet
from src.simulation.sizing import PortfolioHeat


_OLD_HEADER = (
    "bet_id,placed_at_utc,market_ticker,event_ticker,target_date,side,"
    "stake_usd,entry_price,prob_model,prob_market_implied,edge,method,spec,"
    "resolved_at_utc,resolution,pnl_usd\n"
)
_OLD_ROW = (
    "a,2026-05-10T17:00:00Z,KXLOWTNYC-26MAY11-B50.5,KXLOWTNYC-26MAY11,"
    "2026-05-11,NO,100.0,0.36,0.146,0.36,-0.21,ensemble,test,"
    "2026-05-12T12:00:00Z,no,40.0\n"
)


# --- PaperBet / Ledger -----------------------------------------------------
def test_paperbet_defaults_to_bet() -> None:
    bet = PaperBet(
        bet_id="x", placed_at_utc="t", market_ticker="m", event_ticker="e",
        target_date="2026-05-11", side="NO", stake_usd=10.0, entry_price=0.5,
        prob_model=0.4, prob_market_implied=0.5, edge=-0.1, method="ensemble",
        spec="s",
    )
    assert bet.algo_signal == "bet"


def test_ledger_roundtrip_preserves_signal(tmp_path: Path) -> None:
    path = tmp_path / "paper_bets.csv"
    led = Ledger(path)
    led.append(PaperBet(
        bet_id="c", placed_at_utc="t", market_ticker="m", event_ticker="e",
        target_date="2026-05-11", side="YES", stake_usd=0.0, entry_price=0.5,
        prob_model=0.51, prob_market_implied=0.5, edge=0.01, method="ensemble",
        spec="s", algo_signal="no_bet",
    ))
    back = led.read_all()
    assert len(back) == 1
    assert back[0].algo_signal == "no_bet"
    assert "algo_signal" in path.read_text(encoding="utf-8").splitlines()[0]


def test_ledger_migrates_old_16col_file(tmp_path: Path) -> None:
    path = tmp_path / "paper_bets.csv"
    path.write_text(_OLD_HEADER + _OLD_ROW, encoding="utf-8")
    led = Ledger(path)  # __init__ doit migrer
    header = path.read_text(encoding="utf-8").splitlines()[0]
    assert "algo_signal" in header
    rows = led.read_all()
    assert rows[0].algo_signal == "bet"  # backfill


def test_live_run_ensure_column_migrates(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "paper_bets.csv"
    path.write_text(_OLD_HEADER + _OLD_ROW, encoding="utf-8")
    monkeypatch.setattr(live_run, "LEDGER_PATH", path)
    live_run._ensure_algo_signal_column()
    header = path.read_text(encoding="utf-8").splitlines()[0]
    assert header.endswith("algo_signal")
    # Et un append ultérieur reste aligné (17 colonnes partout).
    live_run._append_ledger_row({
        "bet_id": "z", "placed_at_utc": "t", "market_ticker": "m",
        "event_ticker": "e", "target_date": "2026-05-11", "side": "NO",
        "stake_usd": 0.0, "entry_price": 0.5, "prob_model": 0.4,
        "prob_market_implied": 0.5, "edge": -0.01, "method": "ensemble",
        "spec": "s", "algo_signal": "no_bet",
    })
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert all(len(line.split(",")) == 17 for line in lines)


# --- _select_control_bins --------------------------------------------------
def _fake_event() -> SimpleNamespace:
    def mk(t, bid, ask):
        return SimpleNamespace(ticker=t, yes_bid=bid, yes_ask=ask)
    markets = [mk("M1", 0.48, 0.52), mk("M2", 0.40, 0.44), mk("M3", 0.30, 0.34)]
    raw = {"markets": [{"ticker": "M1", "strike_type": "between"},
                       {"ticker": "M2", "strike_type": "between"},
                       {"ticker": "M3", "strike_type": "between"}]}
    return SimpleNamespace(markets=markets, raw=raw,
                           event_ticker="KXLOWTNYC-26MAY17", title="t")


def test_select_control_bins_picks_subthreshold_excludes_bet() -> None:
    ev = _fake_event()
    # M1: mid .50 p .70 edge +.20 (bet) ; M2: mid .42 p .43 edge +.01 ;
    # M3: mid .32 p .33 edge +.01 (témoins).
    probs = {"M1": 0.70, "M2": 0.43, "M3": 0.33}
    ctrls = daily_auto._select_control_bins(ev, probs, n=2, exclude_tickers={"M1"})
    tickers = {c["ticker"] for c in ctrls}
    assert tickers == {"M2", "M3"}
    assert all(c["abs_edge"] < daily_auto.EDGE_THRESHOLD for c in ctrls)
    assert "M1" not in tickers


def test_select_control_bins_respects_n_and_zero() -> None:
    ev = _fake_event()
    probs = {"M1": 0.70, "M2": 0.43, "M3": 0.33}
    assert daily_auto._select_control_bins(ev, probs, 1, {"M1"}).__len__() == 1
    assert daily_auto._select_control_bins(ev, probs, 0, {"M1"}) == []


# --- _capture_one_bin : branche no_bet -------------------------------------
def test_capture_one_bin_no_bet_zero_stake_no_register(monkeypatch) -> None:
    ev = _fake_event()
    fake_spec = SimpleNamespace(target_date=date(2026, 5, 17))
    fake_spec.describe = lambda: "spec"
    monkeypatch.setattr(daily_auto, "parse_market", lambda m: fake_spec)
    monkeypatch.setattr(
        daily_auto, "_predict_all_models",
        lambda registry, weather, spec, mid: [
            {"name": "ensemble", "role": "champion", "p_yes": 0.43, "method": "m"},
        ],
    )
    portfolio = PortfolioHeat()
    target = {"ticker": "M2", "yes_mid": 0.42, "p_champion": 0.43,
              "edge": 0.01, "abs_edge": 0.01,
              "yes_bid": 0.40, "yes_ask": 0.44, "spread": 0.04}
    result = daily_auto._capture_one_bin(
        ev=ev, target=target, weather=None,
        registry={"current_champion": "ensemble"},
        portfolio=portfolio, current_bankroll=1000.0, dry_run=True,
        algo_signal="no_bet",
    )
    assert result["captured"] is True
    assert result["algo_signal"] == "no_bet"
    assert result["size_usd"] == 0.0
    # Aucun engagement de heat : le témoin ne consomme rien.
    assert portfolio.total_open_fraction() == pytest.approx(0.0)


# --- _paper_bets_summary ---------------------------------------------------
def test_paper_bets_summary_splits_bet_and_control(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "paper_bets.csv"
    header = _OLD_HEADER.rstrip("\n") + ",algo_signal\n"

    def row(bet_id, side, resolution, pnl, signal):
        return (
            f"{bet_id},2026-05-10T17:00:00Z,KXLOWTNYC-26MAY11-B50.5,"
            f"KXLOWTNYC-26MAY11,2026-05-11,{side},10.0,0.5,0.4,0.5,-0.1,"
            f"ensemble,test,2026-05-12T12:00:00Z,{resolution},{pnl},{signal}\n"
        )

    path.write_text(
        header
        + row("b1", "NO", "no", 8.0, "bet")     # bet gagné
        + row("b2", "YES", "no", -10.0, "bet")  # bet perdu
        + row("c1", "NO", "no", 0.0, "no_bet")  # témoin gagné
        + row("c2", "YES", "no", 0.0, "no_bet"),  # témoin perdu
        encoding="utf-8",
    )
    monkeypatch.setattr(bdm, "PAPER_BETS_CSV", path)
    s = bdm._paper_bets_summary()
    # P&L et compteur = "bet" seuls.
    assert s["n_resolved"] == 2
    assert s["pnl_usd_cumulative"] == pytest.approx(-2.0)
    assert s["wins"] == 1 and s["losses"] == 1
    assert s["phase_1_counter"].startswith("2/")
    # Groupe témoin séparé.
    assert s["control_group"]["n_resolved"] == 2
    assert s["control_group"]["wins"] == 1
    assert s["control_group"]["losses"] == 1


# --- _already_captured_control ---------------------------------------------
def _ledger_with(tmp_path: Path, *bets: PaperBet) -> Path:
    path = tmp_path / "paper_bets.csv"
    led = Ledger(path)
    for b in bets:
        led.append(b)
    return path


def _mk_bet(bet_id: str, ticker: str = "M2", signal: str = "no_bet",
            resolution: str | None = None) -> PaperBet:
    return PaperBet(
        bet_id=bet_id, placed_at_utc="t", market_ticker=ticker,
        event_ticker="KXLOWTNYC-26MAY17", target_date="2026-05-17",
        side="YES", stake_usd=0.0, entry_price=0.42, prob_model=0.43,
        prob_market_implied=0.42, edge=0.01, method="ensemble", spec="s",
        resolution=resolution,
        resolved_at_utc="t2" if resolution else None,
        pnl_usd=0.0 if resolution else None,
        algo_signal=signal,
    )


def test_already_captured_control_dedupes_on_ledger(tmp_path: Path, monkeypatch) -> None:
    path = _ledger_with(tmp_path, _mk_bet("c1", ticker="M2", signal="no_bet"))
    monkeypatch.setattr(daily_auto, "LEDGER_PATH", path)
    assert daily_auto._already_captured_control("KXLOWTNYC-26MAY17", "M2") is True
    # Autre bin ou autre event : pas de dedupe.
    assert daily_auto._already_captured_control("KXLOWTNYC-26MAY17", "M3") is False
    assert daily_auto._already_captured_control("KXLOWTNYC-26MAY18", "M2") is False


def test_already_captured_control_ignores_bet_rows(tmp_path: Path, monkeypatch) -> None:
    # Une ligne "bet" sur le même bin ne bloque PAS un témoin.
    path = _ledger_with(tmp_path, _mk_bet("b1", ticker="M2", signal="bet"))
    monkeypatch.setattr(daily_auto, "LEDGER_PATH", path)
    assert daily_auto._already_captured_control("KXLOWTNYC-26MAY17", "M2") is False


# --- _settle_control_rows --------------------------------------------------
class _FakeKalshi:
    """KalshiClient factice : get_event sert un payload raw fixé d'avance."""

    payload_by_event: dict = {}

    def get_event(self, event_ticker: str):
        raw = self.payload_by_event[event_ticker]
        return SimpleNamespace(raw=raw)


def test_settle_control_rows_patches_settled_leaves_open(tmp_path: Path, monkeypatch) -> None:
    path = _ledger_with(
        tmp_path,
        _mk_bet("c1", ticker="M2", signal="no_bet"),           # settled yes
        _mk_bet("c2", ticker="M3", signal="no_bet"),           # pas encore settled
        _mk_bet("c3", ticker="M4", signal="no_bet"),           # void
        _mk_bet("b1", ticker="M5", signal="bet"),              # bet : jamais touché
        _mk_bet("c9", ticker="M6", signal="no_bet", resolution="no"),  # déjà résolu
    )
    monkeypatch.setattr(daily_auto, "LEDGER_PATH", path)
    _FakeKalshi.payload_by_event = {
        "KXLOWTNYC-26MAY17": {"markets": [
            {"ticker": "M2", "status": "settled", "result": "yes"},
            {"ticker": "M3", "status": "active", "result": ""},
            {"ticker": "M4", "status": "settled", "result": "annulled"},
            {"ticker": "M5", "status": "settled", "result": "no"},
            {"ticker": "M6", "status": "settled", "result": "no"},
        ]},
    }
    monkeypatch.setattr(daily_auto, "KalshiClient", _FakeKalshi)

    summary = daily_auto._settle_control_rows()
    assert summary == {"open_controls": 3, "settled": 2}

    rows = {b.bet_id: b for b in Ledger(path).read_all()}
    assert rows["c1"].resolution == "yes"
    assert rows["c1"].pnl_usd == 0.0
    assert rows["c1"].resolved_at_utc
    assert rows["c2"].resolution is None          # reste ouvert, retry demain
    assert rows["c3"].resolution == "void"
    assert rows["b1"].resolution is None          # les "bet" passent par finalize_run
    assert rows["c9"].resolution == "no"          # déjà résolu : intouché


def test_settle_control_rows_noop_without_controls(tmp_path: Path, monkeypatch) -> None:
    path = _ledger_with(tmp_path, _mk_bet("b1", ticker="M5", signal="bet"))
    monkeypatch.setattr(daily_auto, "LEDGER_PATH", path)

    class _Boom:
        def get_event(self, *_a):  # pragma: no cover - ne doit jamais être appelé
            raise AssertionError("no_bet absent : Kalshi ne doit pas être appelé")

    monkeypatch.setattr(daily_auto, "KalshiClient", _Boom)
    assert daily_auto._settle_control_rows() == {"open_controls": 0, "settled": 0}


# --- câblage step_capture : témoins capturés après les paris ----------------
def test_step_capture_wires_control_bins(monkeypatch, tmp_path: Path) -> None:
    """Vérifie le câblage bout-en-bout (bug 2026-07-31 : _select_control_bins
    définie mais jamais appelée → 0 ligne no_bet en 6 semaines)."""
    path = tmp_path / "paper_bets.csv"
    Ledger(path)  # crée l'en-tête
    monkeypatch.setattr(daily_auto, "LEDGER_PATH", path)

    ev = _fake_event()

    class _FakeClient:
        def get_event(self, event_ticker):
            return ev

    fake_spec = SimpleNamespace(target_date=date(2026, 5, 17))
    fake_spec.describe = lambda: "spec"

    monkeypatch.setattr(daily_auto, "KalshiClient", _FakeClient)
    monkeypatch.setattr(daily_auto, "OpenMeteoClient", lambda: None)
    monkeypatch.setattr(daily_auto, "EnsemblePredictor", lambda w: SimpleNamespace(
        predict=lambda spec: SimpleNamespace(prob_yes=0.5)))
    monkeypatch.setattr(daily_auto, "_load_champion_registry",
                        lambda: {"current_champion": "ensemble"})
    monkeypatch.setattr(daily_auto, "_compute_current_bankroll", lambda: 1000.0)
    monkeypatch.setattr(daily_auto, "parse_market", lambda m: fake_spec)
    monkeypatch.setattr(daily_auto, "_already_captured_bin", lambda e, m: None)
    monkeypatch.setattr(daily_auto, "EVENT_SERIES_LIST", ["KXLOWTNYC"])
    # Probabilités contrôlées : M1 seul au-dessus du seuil (pari), M2/M3 témoins.
    probs = {"M1": 0.70, "M2": 0.43, "M3": 0.33}
    monkeypatch.setattr(daily_auto, "normalize_event_probs", lambda ps: ps)

    # Court-circuite le scoring par marché : injecte directement les probs.
    real_select_targets = daily_auto._select_target_bins
    real_select_controls = daily_auto._select_control_bins
    calls = {"targets": 0, "controls": 0}

    def spy_targets(ev_, p):
        calls["targets"] += 1
        return [{"ticker": "M1", "yes_bid": 0.48, "yes_ask": 0.52,
                 "yes_mid": 0.50, "spread": 0.04, "p_champion": 0.70,
                 "edge": 0.20, "abs_edge": 0.20}]

    def spy_controls(ev_, p, n, exclude_tickers):
        calls["controls"] += 1
        assert n == 1                      # autant de témoins que de paris capturés
        assert "M1" in exclude_tickers     # le bin parié est exclu
        return real_select_controls(ev_, probs, n, exclude_tickers)

    monkeypatch.setattr(daily_auto, "_select_target_bins", spy_targets)
    monkeypatch.setattr(daily_auto, "_select_control_bins", spy_controls)

    captured_signals = []

    def fake_capture(ev, target, weather, registry, portfolio,
                     current_bankroll, dry_run, algo_signal="bet"):
        captured_signals.append((target["ticker"], algo_signal))
        return {"captured": True, "algo_signal": algo_signal,
                "event_ticker": ev.event_ticker, "market_ticker": target["ticker"]}

    monkeypatch.setattr(daily_auto, "_capture_one_bin", fake_capture)

    summary = daily_auto.step_capture(dry_run=True)

    assert calls["targets"] == 1
    assert calls["controls"] == 1          # LE câblage : la sélection témoin est appelée
    assert ("M1", "bet") in captured_signals
    no_bets = [t for t, s in captured_signals if s == "no_bet"]
    assert len(no_bets) == 1               # n = event_captured = 1
    assert no_bets[0] in {"M2", "M3"}
    assert summary["captured_count"] == 1  # les témoins ne gonflent pas le compteur
    assert summary["control_count"] == 1
