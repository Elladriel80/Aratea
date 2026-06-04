**Run 144 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jun 3, 2026?
Bin cible : `KXLOWTLAX-26JUN03-B57.5` · Outcome : NO · Low observée (bin gagnant) : 59-60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.181, Brier=0.0327, P&L réel=$-2.38
- `learned_v2` (challenger) — p_yes=0.040, Brier=0.0016, P&L théorique=$-2.38 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.085, Brier=0.0072, P&L théorique=$-2.38

Verdict run 144 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/144/report.json
