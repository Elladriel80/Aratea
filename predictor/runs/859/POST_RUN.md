**Run 859 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Oct 3, 2026?
Bin cible : `KXLOWTMIA-26OCT03-B75.5` · Outcome : NO · Low observée (bin gagnant) : 79-80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.154, Brier=0.0236, P&L réel=$-59.92
- `learned_v2` (challenger) — p_yes=0.052, Brier=0.0027, P&L théorique=$-59.92 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.070, Brier=0.0049, P&L théorique=$-59.92

Verdict run 859 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/859/report.json
