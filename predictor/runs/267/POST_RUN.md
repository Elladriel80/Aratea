**Run 267 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 18, 2026?
Bin cible : `KXLOWTMIA-26JUN18-B79.5` · Outcome : NO · Low observée (bin gagnant) : 81-82°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.251, Brier=0.0627, P&L réel=$+33.62
- `learned_v2` (challenger) — p_yes=0.063, Brier=0.0039, P&L théorique=$+33.62 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.415, Brier=0.1722, P&L théorique=$+33.62

Verdict run 267 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/267/report.json
