**Run 578 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 30, 2026?
Bin cible : `KXLOWTSFO-26JUL30-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.353, Brier=0.4190, P&L réel=$-81.88
- `learned_v2` (challenger) — p_yes=0.150, Brier=0.7218, P&L théorique=$-81.88
- `kalshi_mid_baseline` (baseline) — p_yes=0.555, Brier=0.1980, P&L théorique=$-81.88 ⭐

Verdict run 578 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/578/report.json
