**Run 062 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on May 26, 2026?
Bin cible : `KXLOWTBOS-26MAY26-B53.5` · Outcome : YES · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.101, Brier=0.8083, P&L réel=$+12.35 ⭐
- `learned_v2` (challenger) — p_yes=0.038, Brier=0.9259, P&L théorique=$+12.35
- `kalshi_mid_baseline` (baseline) — p_yes=0.050, Brier=0.9025, P&L théorique=$+12.35

Verdict run 062 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/062/report.json
