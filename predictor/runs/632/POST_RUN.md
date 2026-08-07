**Run 632 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Aug 5, 2026?
Bin cible : `KXLOWTMIA-26AUG05-B78.5` · Outcome : YES · Low observée (bin gagnant) : 78-79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.318, Brier=0.4652, P&L réel=$-71.98
- `learned_v2` (challenger) — p_yes=0.166, Brier=0.6957, P&L théorique=$-71.98
- `kalshi_mid_baseline` (baseline) — p_yes=0.390, Brier=0.3721, P&L théorique=$-71.98 ⭐

Verdict run 632 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/632/report.json
