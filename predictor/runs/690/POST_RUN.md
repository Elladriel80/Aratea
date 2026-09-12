**Run 690 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Sep 11, 2026?
Bin cible : `KXLOWTMIA-26SEP11-B79.5` · Outcome : NO · Low observée (bin gagnant) : 77-78°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.332, Brier=0.1101, P&L réel=$-84.25
- `learned_v2` (challenger) — p_yes=0.423, Brier=0.1791, P&L théorique=$-84.25
- `kalshi_mid_baseline` (baseline) — p_yes=0.250, Brier=0.0625, P&L théorique=$-84.25 ⭐

Verdict run 690 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/690/report.json
