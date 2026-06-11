**Run 198 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 9, 2026?
Bin cible : `KXLOWTDEN-26JUN09-B57.5` · Outcome : NO · Low observée (bin gagnant) : 55-56°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.140, Brier=0.0197, P&L réel=$+15.60 ⭐
- `learned_v2` (challenger) — p_yes=0.194, Brier=0.0376, P&L théorique=$+15.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.390, Brier=0.1521, P&L théorique=$+15.60

Verdict run 198 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/198/report.json
