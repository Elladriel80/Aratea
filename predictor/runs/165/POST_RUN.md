**Run 165 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 4, 2026?
Bin cible : `KXLOWTNYC-26JUN04-B61.5` · Outcome : NO · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.190, Brier=0.0360, P&L réel=$+9.66 ⭐
- `learned_v2` (challenger) — p_yes=0.257, Brier=0.0661, P&L théorique=$+9.66
- `kalshi_mid_baseline` (baseline) — p_yes=0.345, Brier=0.1190, P&L théorique=$+9.66

Verdict run 165 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/165/report.json
