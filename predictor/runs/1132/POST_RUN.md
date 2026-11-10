**Run 1132 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Nov 9, 2026?
Bin cible : `KXLOWTBOS-26NOV09-B46.5` · Outcome : NO · Low observée (bin gagnant) : ≥47°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.420, Brier=0.1762, P&L réel=$+120.23 ⭐
- `learned_v2` (challenger) — p_yes=0.777, Brier=0.6038, P&L théorique=$+120.23
- `kalshi_mid_baseline` (baseline) — p_yes=0.525, Brier=0.2756, P&L théorique=$+120.23

Verdict run 1132 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1132/report.json
