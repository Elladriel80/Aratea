**Run 177 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 5, 2026?
Bin cible : `KXLOWTDC-26JUN05-B62.5` · Outcome : NO · Low observée (bin gagnant) : 64-65°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.125, Brier=0.0156, P&L réel=$+8.99 ⭐
- `learned_v2` (challenger) — p_yes=0.500, Brier=0.2500, P&L théorique=$+8.99
- `kalshi_mid_baseline` (baseline) — p_yes=0.290, Brier=0.0841, P&L théorique=$+8.99

Verdict run 177 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/177/report.json
