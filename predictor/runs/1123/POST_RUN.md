**Run 1123 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Nov 7, 2026?
Bin cible : `KXLOWTDEN-26NOV07-B31.5` · Outcome : NO · Low observée (bin gagnant) : 35-36°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.221, Brier=0.0490, P&L réel=$-125.42
- `learned_v2` (challenger) — p_yes=0.392, Brier=0.1537, P&L théorique=$-125.42
- `kalshi_mid_baseline` (baseline) — p_yes=0.135, Brier=0.0182, P&L théorique=$-125.42 ⭐

Verdict run 1123 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1123/report.json
