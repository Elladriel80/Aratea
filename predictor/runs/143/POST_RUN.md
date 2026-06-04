**Run 143 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 3, 2026?
Bin cible : `KXLOWTNYC-26JUN03-B59.5` · Outcome : NO · Low observée (bin gagnant) : ≥60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.193, Brier=0.0372, P&L réel=$+22.88 ⭐
- `learned_v2` (challenger) — p_yes=0.267, Brier=0.0712, P&L théorique=$+22.88
- `kalshi_mid_baseline` (baseline) — p_yes=0.520, Brier=0.2704, P&L théorique=$+22.88

Verdict run 143 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/143/report.json
