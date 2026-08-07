**Run 621 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Aug 5, 2026?
Bin cible : `KXLOWTNYC-26AUG05-B67.5` · Outcome : NO · Low observée (bin gagnant) : 69-70°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.227, Brier=0.0514, P&L réel=$+47.00 ⭐
- `learned_v2` (challenger) — p_yes=0.249, Brier=0.0618, P&L théorique=$+47.00
- `kalshi_mid_baseline` (baseline) — p_yes=0.395, Brier=0.1560, P&L théorique=$+47.00

Verdict run 621 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/621/report.json
