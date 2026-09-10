**Run 679 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Sep 9, 2026?
Bin cible : `KXLOWTDEN-26SEP09-B54.5` · Outcome : YES · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.089, Brier=0.8291, P&L réel=$-70.53
- `learned_v2` (challenger) — p_yes=0.021, Brier=0.9581, P&L théorique=$-70.53
- `kalshi_mid_baseline` (baseline) — p_yes=0.225, Brier=0.6006, P&L théorique=$-70.53 ⭐

Verdict run 679 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/679/report.json
