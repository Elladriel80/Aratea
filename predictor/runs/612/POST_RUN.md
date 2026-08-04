**Run 612 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Aug 3, 2026?
Bin cible : `KXLOWTCHI-26AUG03-B62.5` · Outcome : YES · Low observée (bin gagnant) : 62-63°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.465, Brier=0.2867, P&L réel=$+172.12 ⭐
- `learned_v2` (challenger) — p_yes=0.328, Brier=0.4517, P&L théorique=$+172.12
- `kalshi_mid_baseline` (baseline) — p_yes=0.325, Brier=0.4556, P&L théorique=$+172.12

Verdict run 612 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/612/report.json
