**Run 186 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 6, 2026?
Bin cible : `KXLOWTNYC-26JUN06-B69.5` · Outcome : NO · Low observée (bin gagnant) : ≤67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.246, Brier=0.0606, P&L réel=$+5.04
- `learned_v2` (challenger) — p_yes=0.172, Brier=0.0296, P&L théorique=$+5.04 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.315, Brier=0.0992, P&L théorique=$+5.04

Verdict run 186 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/186/report.json
