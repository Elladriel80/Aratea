**Run 284 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 20, 2026?
Bin cible : `KXLOWTDEN-26JUN20-B55.5` · Outcome : NO · Low observée (bin gagnant) : ≤55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.119, Brier=0.0141, P&L réel=$+9.17 ⭐
- `learned_v2` (challenger) — p_yes=0.123, Brier=0.0151, P&L théorique=$+9.17
- `kalshi_mid_baseline` (baseline) — p_yes=0.195, Brier=0.0380, P&L théorique=$+9.17

Verdict run 284 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/284/report.json
