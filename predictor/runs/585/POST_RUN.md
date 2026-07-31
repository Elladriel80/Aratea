**Run 585 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Jul 30, 2026?
Bin cible : `KXLOWTMIA-26JUL30-B78.5` · Outcome : NO · Low observée (bin gagnant) : 80-81°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.247, Brier=0.0610, P&L réel=$+45.08
- `learned_v2` (challenger) — p_yes=0.062, Brier=0.0039, P&L théorique=$+45.08 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.355, Brier=0.1260, P&L théorique=$+45.08

Verdict run 585 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/585/report.json
