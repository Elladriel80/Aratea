**Run 398 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 7, 2026?
Bin cible : `KXLOWTSFO-26JUL07-B56.5` · Outcome : NO · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.443, Brier=0.1958, P&L réel=$+278.73 ⭐
- `learned_v2` (challenger) — p_yes=0.460, Brier=0.2115, P&L théorique=$+278.73
- `kalshi_mid_baseline` (baseline) — p_yes=0.815, Brier=0.6642, P&L théorique=$+278.73

Verdict run 398 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/398/report.json
