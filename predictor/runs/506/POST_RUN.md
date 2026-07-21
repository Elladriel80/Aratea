**Run 506 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 20, 2026?
Bin cible : `KXLOWTSFO-26JUL20-B58.5` · Outcome : YES · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.602, Brier=0.1581, P&L réel=$-60.86
- `learned_v2` (challenger) — p_yes=0.615, Brier=0.1486, P&L théorique=$-60.86
- `kalshi_mid_baseline` (baseline) — p_yes=0.660, Brier=0.1156, P&L théorique=$-60.86 ⭐

Verdict run 506 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/506/report.json
