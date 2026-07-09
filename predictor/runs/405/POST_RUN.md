**Run 405 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 8, 2026?
Bin cible : `KXLOWTNYC-26JUL08-B63.5` · Outcome : YES · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.397, Brier=0.3635, P&L réel=$+361.57
- `learned_v2` (challenger) — p_yes=0.633, Brier=0.1345, P&L théorique=$+361.57 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.135, Brier=0.7482, P&L théorique=$+361.57

Verdict run 405 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/405/report.json
