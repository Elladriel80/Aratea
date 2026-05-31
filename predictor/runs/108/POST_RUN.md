**Run 108 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on May 30, 2026?
Bin cible : `KXLOWTBOS-26MAY30-B41.5` · Outcome : NO · Low observée (bin gagnant) : 45-46°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.110, Brier=0.0120, P&L réel=$+5.38
- `learned_v2` (challenger) — p_yes=0.043, Brier=0.0019, P&L théorique=$+5.38 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.215, Brier=0.0462, P&L théorique=$+5.38

Verdict run 108 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/108/report.json
