**Run 152 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 3, 2026?
Bin cible : `KXLOWTDEN-26JUN03-B51.5` · Outcome : YES · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.133, Brier=0.7511, P&L réel=$+16.74 ⭐
- `learned_v2` (challenger) — p_yes=0.072, Brier=0.8610, P&L théorique=$+16.74
- `kalshi_mid_baseline` (baseline) — p_yes=0.070, Brier=0.8649, P&L théorique=$+16.74

Verdict run 152 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/152/report.json
