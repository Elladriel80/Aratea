**Run 361 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Jul 1, 2026?
Bin cible : `KXLOWTDEN-26JUL01-B58.5` · Outcome : NO · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.315, Brier=0.0993, P&L réel=$-72.06
- `learned_v2` (challenger) — p_yes=0.465, Brier=0.2164, P&L théorique=$-72.06
- `kalshi_mid_baseline` (baseline) — p_yes=0.145, Brier=0.0210, P&L théorique=$-72.06 ⭐

Verdict run 361 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/361/report.json
