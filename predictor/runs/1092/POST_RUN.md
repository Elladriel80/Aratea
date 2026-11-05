**Run 1092 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Nov 2, 2026?
Bin cible : `KXLOWTDEN-26NOV02-B44.5` · Outcome : NO · Low observée (bin gagnant) : 42-43°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.146, Brier=0.0213, P&L réel=$+35.72 ⭐
- `learned_v2` (challenger) — p_yes=0.310, Brier=0.0963, P&L théorique=$+35.72
- `kalshi_mid_baseline` (baseline) — p_yes=0.235, Brier=0.0552, P&L théorique=$+35.72

Verdict run 1092 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1092/report.json
