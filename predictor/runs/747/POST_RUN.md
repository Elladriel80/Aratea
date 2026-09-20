**Run 747 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Sep 19, 2026?
Bin cible : `KXLOWTLAX-26SEP19-B66.5` · Outcome : YES · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.112, Brier=0.7894, P&L réel=$-51.04
- `learned_v2` (challenger) — p_yes=0.035, Brier=0.9309, P&L théorique=$-51.04
- `kalshi_mid_baseline` (baseline) — p_yes=0.420, Brier=0.3364, P&L théorique=$-51.04 ⭐

Verdict run 747 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/747/report.json
