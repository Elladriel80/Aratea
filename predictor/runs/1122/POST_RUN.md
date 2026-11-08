**Run 1122 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Nov 7, 2026?
Bin cible : `KXLOWTDEN-26NOV07-B35.5` · Outcome : YES · Low observée (bin gagnant) : 35-36°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.187, Brier=0.6603, P&L réel=$-124.89
- `learned_v2` (challenger) — p_yes=0.316, Brier=0.4680, P&L théorique=$-124.89 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.310, Brier=0.4761, P&L théorique=$-124.89

Verdict run 1122 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1122/report.json
