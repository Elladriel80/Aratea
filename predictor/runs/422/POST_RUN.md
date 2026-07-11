**Run 422 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 10, 2026?
Bin cible : `KXLOWTNYC-26JUL10-B69.5` · Outcome : NO · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.023, Brier=0.0005, P&L réel=$+26.68 ⭐
- `learned_v2` (challenger) — p_yes=0.051, Brier=0.0026, P&L théorique=$+26.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.230, Brier=0.0529, P&L théorique=$+26.68

Verdict run 422 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/422/report.json
