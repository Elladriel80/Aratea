**Run 811 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Sep 27, 2026?
Bin cible : `KXLOWTSFO-26SEP27-B54.5` · Outcome : NO · Low observée (bin gagnant) : ≥57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.339, Brier=0.1152, P&L réel=$-55.56
- `learned_v2` (challenger) — p_yes=0.362, Brier=0.1314, P&L théorique=$-55.56
- `kalshi_mid_baseline` (baseline) — p_yes=0.120, Brier=0.0144, P&L théorique=$-55.56 ⭐

Verdict run 811 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/811/report.json
