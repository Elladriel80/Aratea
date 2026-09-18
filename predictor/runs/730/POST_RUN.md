**Run 730 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Sep 17, 2026?
Bin cible : `KXLOWTNYC-26SEP17-B64.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.159, Brier=0.0251, P&L réel=$-56.25
- `learned_v2` (challenger) — p_yes=0.126, Brier=0.0160, P&L théorique=$-56.25
- `kalshi_mid_baseline` (baseline) — p_yes=0.090, Brier=0.0081, P&L théorique=$-56.25 ⭐

Verdict run 730 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/730/report.json
