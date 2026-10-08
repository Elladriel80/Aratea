**Run 896 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Oct 7, 2026?
Bin cible : `KXLOWTPHX-26OCT07-B77.5` · Outcome : NO · Low observée (bin gagnant) : 79-80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.128, Brier=0.0163, P&L réel=$+15.33 ⭐
- `learned_v2` (challenger) — p_yes=0.227, Brier=0.0517, P&L théorique=$+15.33
- `kalshi_mid_baseline` (baseline) — p_yes=0.210, Brier=0.0441, P&L théorique=$+15.33

Verdict run 896 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/896/report.json
