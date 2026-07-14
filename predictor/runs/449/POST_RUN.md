**Run 449 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 13, 2026?
Bin cible : `KXLOWTSFO-26JUL13-B60.5` · Outcome : YES · Low observée (bin gagnant) : 60-61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.259, Brier=0.5489, P&L réel=$-83.89
- `learned_v2` (challenger) — p_yes=0.078, Brier=0.8498, P&L théorique=$-83.89
- `kalshi_mid_baseline` (baseline) — p_yes=0.405, Brier=0.3540, P&L théorique=$-83.89 ⭐

Verdict run 449 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/449/report.json
