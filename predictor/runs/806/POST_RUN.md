**Run 806 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Sep 25, 2026?
Bin cible : `KXLOWTSEA-26SEP25-B51.5` · Outcome : NO · Low observée (bin gagnant) : 49-50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.434, Brier=0.1883, P&L réel=$+63.82 ⭐
- `learned_v2` (challenger) — p_yes=0.604, Brier=0.3651, P&L théorique=$+63.82
- `kalshi_mid_baseline` (baseline) — p_yes=0.555, Brier=0.3080, P&L théorique=$+63.82

Verdict run 806 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/806/report.json
