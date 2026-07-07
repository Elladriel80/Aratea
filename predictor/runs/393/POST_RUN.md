**Run 393 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 6, 2026?
Bin cible : `KXLOWTSFO-26JUL06-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.615, Brier=0.1484, P&L réel=$-67.13
- `learned_v2` (challenger) — p_yes=0.637, Brier=0.1317, P&L théorique=$-67.13
- `kalshi_mid_baseline` (baseline) — p_yes=0.755, Brier=0.0600, P&L théorique=$-67.13 ⭐

Verdict run 393 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/393/report.json
