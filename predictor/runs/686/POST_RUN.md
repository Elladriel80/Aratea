**Run 686 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Sep 11, 2026?
Bin cible : `KXLOWTCHI-26SEP11-B63.5` · Outcome : NO · Low observée (bin gagnant) : 61-62°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.170, Brier=0.0289, P&L réel=$+45.15 ⭐
- `learned_v2` (challenger) — p_yes=0.246, Brier=0.0604, P&L théorique=$+45.15
- `kalshi_mid_baseline` (baseline) — p_yes=0.350, Brier=0.1225, P&L théorique=$+45.15

Verdict run 686 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/686/report.json
