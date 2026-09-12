**Run 689 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Sep 11, 2026?
Bin cible : `KXLOWTDC-26SEP11-B68.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.015, Brier=0.0002, P&L réel=$+14.85 ⭐
- `learned_v2` (challenger) — p_yes=0.013, Brier=0.0002, P&L théorique=$+14.85
- `kalshi_mid_baseline` (baseline) — p_yes=0.150, Brier=0.0225, P&L théorique=$+14.85

Verdict run 689 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/689/report.json
