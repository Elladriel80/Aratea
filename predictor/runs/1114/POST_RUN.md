**Run 1114 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 7, 2026?
Bin cible : `KXLOWTSFO-26NOV07-B55.5` · Outcome : NO · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.342, Brier=0.1167, P&L réel=$-125.48
- `learned_v2` (challenger) — p_yes=0.534, Brier=0.2851, P&L théorique=$-125.48
- `kalshi_mid_baseline` (baseline) — p_yes=0.040, Brier=0.0016, P&L théorique=$-125.48 ⭐

Verdict run 1114 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1114/report.json
