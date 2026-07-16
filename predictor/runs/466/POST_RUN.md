**Run 466 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 15, 2026?
Bin cible : `KXLOWTSFO-26JUL15-B59.5` · Outcome : NO · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.350, Brier=0.1224, P&L réel=$+172.32
- `learned_v2` (challenger) — p_yes=0.145, Brier=0.0211, P&L théorique=$+172.32 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.715, Brier=0.5112, P&L théorique=$+172.32

Verdict run 466 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/466/report.json
