**Run 355 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on Jul 1, 2026?
Bin cible : `KXLOWTBOS-26JUL01-B70.5` · Outcome : YES · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.334, Brier=0.4434, P&L réel=$+279.84
- `learned_v2` (challenger) — p_yes=0.551, Brier=0.2017, P&L théorique=$+279.84 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.205, Brier=0.6320, P&L théorique=$+279.84

Verdict run 355 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/355/report.json
