**Run 828 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Sep 29, 2026?
Bin cible : `KXLOWTLAX-26SEP29-B62.5` · Outcome : YES · Low observée (bin gagnant) : 62-63°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.269, Brier=0.5342, P&L réel=$+505.34 ⭐
- `learned_v2` (challenger) — p_yes=0.093, Brier=0.8227, P&L théorique=$+505.34
- `kalshi_mid_baseline` (baseline) — p_yes=0.115, Brier=0.7832, P&L théorique=$+505.34

Verdict run 828 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/828/report.json
