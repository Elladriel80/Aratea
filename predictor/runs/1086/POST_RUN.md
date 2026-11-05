**Run 1086 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 2, 2026?
Bin cible : `KXLOWTSFO-26NOV02-B53.5` · Outcome : NO · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.271, Brier=0.0734, P&L réel=$-103.41
- `learned_v2` (challenger) — p_yes=0.305, Brier=0.0928, P&L théorique=$-103.41
- `kalshi_mid_baseline` (baseline) — p_yes=0.215, Brier=0.0462, P&L théorique=$-103.41 ⭐

Verdict run 1086 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1086/report.json
