**Run 800 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on Sep 25, 2026?
Bin cible : `KXLOWTBOS-26SEP25-B50.5` · Outcome : YES · Low observée (bin gagnant) : 50-51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.015, Brier=0.9695, P&L réel=$-51.33
- `learned_v2` (challenger) — p_yes=0.054, Brier=0.8953, P&L théorique=$-51.33
- `kalshi_mid_baseline` (baseline) — p_yes=0.115, Brier=0.7832, P&L théorique=$-51.33 ⭐

Verdict run 800 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/800/report.json
