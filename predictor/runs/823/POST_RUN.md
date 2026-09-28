**Run 823 — résolu NO · Multi-model A/B**

Event : Highest temperature in Phoenix on Sep 27, 2026?
Bin cible : `KXHIGHTPHX-26SEP27-B95.5` · Outcome : NO · Low observée (bin gagnant) : 97-98°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.052, Brier=0.0027, P&L réel=$+9.80 ⭐
- `learned_v2` (challenger) — p_yes=0.114, Brier=0.0129, P&L théorique=$+9.80
- `kalshi_mid_baseline` (baseline) — p_yes=0.265, Brier=0.0702, P&L théorique=$+9.80

Verdict run 823 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/823/report.json
