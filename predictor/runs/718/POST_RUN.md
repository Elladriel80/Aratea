**Run 718 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Sep 15, 2026?
Bin cible : `KXLOWTDC-26SEP15-B56.5` · Outcome : NO · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.118, Brier=0.0139, P&L réel=$+12.40 ⭐
- `learned_v2` (challenger) — p_yes=0.118, Brier=0.0139, P&L théorique=$+12.40
- `kalshi_mid_baseline` (baseline) — p_yes=0.185, Brier=0.0342, P&L théorique=$+12.40

Verdict run 718 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/718/report.json
