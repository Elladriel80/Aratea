**Run 1117 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Nov 7, 2026?
Bin cible : `KXLOWTDC-26NOV07-B48.5` · Outcome : NO · Low observée (bin gagnant) : 46-47°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.400, Brier=0.1600, P&L réel=$+162.72 ⭐
- `learned_v2` (challenger) — p_yes=0.788, Brier=0.6207, P&L théorique=$+162.72
- `kalshi_mid_baseline` (baseline) — p_yes=0.565, Brier=0.3192, P&L théorique=$+162.72

Verdict run 1117 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1117/report.json
