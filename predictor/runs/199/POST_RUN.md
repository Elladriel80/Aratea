**Run 199 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 9, 2026?
Bin cible : `KXLOWTDEN-26JUN09-B55.5` · Outcome : YES · Low observée (bin gagnant) : 55-56°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.110, Brier=0.7921, P&L réel=$-24.16
- `learned_v2` (challenger) — p_yes=0.188, Brier=0.6586, P&L théorique=$-24.16
- `kalshi_mid_baseline` (baseline) — p_yes=0.245, Brier=0.5700, P&L théorique=$-24.16 ⭐

Verdict run 199 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/199/report.json
