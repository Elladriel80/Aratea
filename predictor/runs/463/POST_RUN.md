**Run 463 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 15, 2026?
Bin cible : `KXLOWTNYC-26JUL15-B75.5` · Outcome : YES · Low observée (bin gagnant) : 75-76°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.059, Brier=0.8848, P&L réel=$-68.14
- `learned_v2` (challenger) — p_yes=0.013, Brier=0.9736, P&L théorique=$-68.14
- `kalshi_mid_baseline` (baseline) — p_yes=0.115, Brier=0.7832, P&L théorique=$-68.14 ⭐

Verdict run 463 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/463/report.json
