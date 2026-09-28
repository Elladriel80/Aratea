**Run 815 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Sep 27, 2026?
Bin cible : `KXLOWTPHX-26SEP27-B77.5` · Outcome : NO · Low observée (bin gagnant) : 79-80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.143, Brier=0.0206, P&L réel=$+17.52 ⭐
- `learned_v2` (challenger) — p_yes=0.211, Brier=0.0446, P&L théorique=$+17.52
- `kalshi_mid_baseline` (baseline) — p_yes=0.240, Brier=0.0576, P&L théorique=$+17.52

Verdict run 815 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/815/report.json
