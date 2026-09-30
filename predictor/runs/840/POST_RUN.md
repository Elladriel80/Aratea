**Run 840 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Sep 29, 2026?
Bin cible : `KXHIGHTDC-26SEP29-B76.5` · Outcome : NO · Low observée (bin gagnant) : 74-75°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.367, Brier=0.1345, P&L réel=$+19.62
- `learned_v2` (challenger) — p_yes=0.201, Brier=0.0403, P&L théorique=$+19.62 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.545, Brier=0.2970, P&L théorique=$+19.62

Verdict run 840 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/840/report.json
