**Run 1194 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 22, 2026?
Bin cible : `KXLOWTSFO-26NOV22-B47.5` · Outcome : NO · Low observée (bin gagnant) : 49-50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.257, Brier=0.0659, P&L réel=$+130.34
- `learned_v2` (challenger) — p_yes=0.226, Brier=0.0511, P&L théorique=$+130.34 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.490, Brier=0.2401, P&L théorique=$+130.34

Verdict run 1194 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1194/report.json
