**Run 783 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Sep 23, 2026?
Bin cible : `KXLOWTBOS-26SEP23-B57.5` · Outcome : NO · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.309, Brier=0.0955, P&L réel=$-56.80
- `learned_v2` (challenger) — p_yes=0.408, Brier=0.1666, P&L théorique=$-56.80
- `kalshi_mid_baseline` (baseline) — p_yes=0.100, Brier=0.0100, P&L théorique=$-56.80 ⭐

Verdict run 783 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/783/report.json
