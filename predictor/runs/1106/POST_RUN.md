**Run 1106 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Nov 5, 2026?
Bin cible : `KXLOWTSEA-26NOV05-B47.5` · Outcome : NO · Low observée (bin gagnant) : 49-50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.075, Brier=0.0057, P&L réel=$+171.00
- `learned_v2` (challenger) — p_yes=0.040, Brier=0.0016, P&L théorique=$+171.00 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.570, Brier=0.3249, P&L théorique=$+171.00

Verdict run 1106 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1106/report.json
