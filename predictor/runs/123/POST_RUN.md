**Run 123 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jun 1, 2026?
Bin cible : `KXLOWTSFO-26JUN01-B50.5` · Outcome : NO · Low observée (bin gagnant) : 52-53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.303, Brier=0.0916, P&L réel=$+16.46
- `learned_v2` (challenger) — p_yes=0.207, Brier=0.0429, P&L théorique=$+16.46 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.445, Brier=0.1980, P&L théorique=$+16.46

Verdict run 123 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/123/report.json
