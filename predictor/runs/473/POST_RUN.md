**Run 473 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 16, 2026?
Bin cible : `KXLOWTNYC-26JUL16-B76.5` · Outcome : NO · Low observée (bin gagnant) : 74-75°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.363, Brier=0.1319, P&L réel=$-66.96
- `learned_v2` (challenger) — p_yes=0.182, Brier=0.0330, P&L théorique=$-66.96 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.310, Brier=0.0961, P&L théorique=$-66.96

Verdict run 473 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/473/report.json
