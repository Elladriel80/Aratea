**Run 1090 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Nov 2, 2026?
Bin cible : `KXLOWTMIA-26NOV02-B70.5` · Outcome : YES · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.183, Brier=0.6671, P&L réel=$+1108.62
- `learned_v2` (challenger) — p_yes=0.188, Brier=0.6598, P&L théorique=$+1108.62 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.095, Brier=0.8190, P&L théorique=$+1108.62

Verdict run 1090 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1090/report.json
