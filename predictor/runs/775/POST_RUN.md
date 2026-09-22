**Run 775 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Sep 21, 2026?
Bin cible : `KXLOWTDEN-26SEP21-B52.5` · Outcome : NO · Low observée (bin gagnant) : 50-51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.122, Brier=0.0149, P&L réel=$-38.43
- `learned_v2` (challenger) — p_yes=0.030, Brier=0.0009, P&L théorique=$-38.43 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.070, Brier=0.0049, P&L théorique=$-38.43

Verdict run 775 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/775/report.json
