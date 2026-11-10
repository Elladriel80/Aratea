**Run 1128 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 9, 2026?
Bin cible : `KXLOWTSFO-26NOV09-B53.5` · Outcome : YES · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.250, Brier=0.5623, P&L réel=$-108.80
- `learned_v2` (challenger) — p_yes=0.284, Brier=0.5120, P&L théorique=$-108.80
- `kalshi_mid_baseline` (baseline) — p_yes=0.360, Brier=0.4096, P&L théorique=$-108.80 ⭐

Verdict run 1128 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1128/report.json
