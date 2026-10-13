**Run 926 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Oct 11, 2026?
Bin cible : `KXLOWTMIA-26OCT11-B78.5` · Outcome : NO · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.362, Brier=0.1308, P&L réel=$-45.38
- `learned_v2` (challenger) — p_yes=0.150, Brier=0.0226, P&L théorique=$-45.38 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.165, Brier=0.0272, P&L théorique=$-45.38

Verdict run 926 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/926/report.json
