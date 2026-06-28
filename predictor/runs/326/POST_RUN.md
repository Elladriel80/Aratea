**Run 326 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 26, 2026?
Bin cible : `KXLOWTMIA-26JUN26-B82.5` · Outcome : NO · Low observée (bin gagnant) : 80-81°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.308, Brier=0.0949, P&L réel=$-59.37
- `learned_v2` (challenger) — p_yes=0.113, Brier=0.0128, P&L théorique=$-59.37
- `kalshi_mid_baseline` (baseline) — p_yes=0.030, Brier=0.0009, P&L théorique=$-59.37 ⭐

Verdict run 326 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/326/report.json
