**Run 283 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 20, 2026?
Bin cible : `KXLOWTDEN-26JUN20-B57.5` · Outcome : NO · Low observée (bin gagnant) : ≤55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.146, Brier=0.0214, P&L réel=$-38.22
- `learned_v2` (challenger) — p_yes=0.155, Brier=0.0241, P&L théorique=$-38.22
- `kalshi_mid_baseline` (baseline) — p_yes=0.065, Brier=0.0042, P&L théorique=$-38.22 ⭐

Verdict run 283 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/283/report.json
