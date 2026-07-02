**Run 364 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Jul 1, 2026?
Bin cible : `KXHIGHTSFO-26JUL01-B68.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.161, Brier=0.0260, P&L réel=$+7.68 ⭐
- `learned_v2` (challenger) — p_yes=0.169, Brier=0.0284, P&L théorique=$+7.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.265, Brier=0.0702, P&L théorique=$+7.68

Verdict run 364 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/364/report.json
