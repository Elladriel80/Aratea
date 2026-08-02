**Run 599 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Aug 1, 2026?
Bin cible : `KXLOWTCHI-26AUG01-B68.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.449, Brier=0.2013, P&L réel=$-79.16
- `learned_v2` (challenger) — p_yes=0.754, Brier=0.5679, P&L théorique=$-79.16
- `kalshi_mid_baseline` (baseline) — p_yes=0.355, Brier=0.1260, P&L théorique=$-79.16 ⭐

Verdict run 599 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/599/report.json
