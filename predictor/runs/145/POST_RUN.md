**Run 145 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jun 3, 2026?
Bin cible : `KXLOWTLAX-26JUN03-B59.5` · Outcome : YES · Low observée (bin gagnant) : 59-60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.336, Brier=0.4405, P&L réel=$-21.09
- `learned_v2` (challenger) — p_yes=0.170, Brier=0.6891, P&L théorique=$-21.09
- `kalshi_mid_baseline` (baseline) — p_yes=0.430, Brier=0.3249, P&L théorique=$-21.09 ⭐

Verdict run 145 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/145/report.json
