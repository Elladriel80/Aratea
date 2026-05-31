**Run 104 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on May 30, 2026?
Bin cible : `KXLOWTDC-26MAY30-B57.5` · Outcome : NO · Low observée (bin gagnant) : 61-62°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.135, Brier=0.0183, P&L réel=$+9.28
- `learned_v2` (challenger) — p_yes=0.078, Brier=0.0061, P&L théorique=$+9.28 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.320, Brier=0.1024, P&L théorique=$+9.28

Verdict run 104 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/104/report.json
