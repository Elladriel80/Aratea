**Run 1093 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Seattle on Nov 2, 2026?
Bin cible : `KXLOWTSEA-26NOV02-B34.5` · Outcome : YES · Low observée (bin gagnant) : 34-35°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.069, Brier=0.8662, P&L réel=$-115.92
- `learned_v2` (challenger) — p_yes=0.121, Brier=0.7727, P&L théorique=$-115.92
- `kalshi_mid_baseline` (baseline) — p_yes=0.160, Brier=0.7056, P&L théorique=$-115.92 ⭐

Verdict run 1093 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1093/report.json
