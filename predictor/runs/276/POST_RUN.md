**Run 276 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jun 20, 2026?
Bin cible : `KXLOWTCHI-26JUN20-B59.5` · Outcome : NO · Low observée (bin gagnant) : 61-62°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.158, Brier=0.0249, P&L réel=$+14.84 ⭐
- `learned_v2` (challenger) — p_yes=0.208, Brier=0.0434, P&L théorique=$+14.84
- `kalshi_mid_baseline` (baseline) — p_yes=0.280, Brier=0.0784, P&L théorique=$+14.84

Verdict run 276 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/276/report.json
