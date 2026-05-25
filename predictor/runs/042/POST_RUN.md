**Run 042 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on May 24, 2026?
Bin cible : `KXLOWTBOS-26MAY24-B47.5` · Outcome : NO · Low observée (bin gagnant) : ≥50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.125, Brier=0.0155, P&L réel=$+5.85
- `learned_v2` (challenger) — p_yes=0.046, Brier=0.0021, P&L théorique=$+5.85 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.225, Brier=0.0506, P&L théorique=$+5.85

Verdict run 042 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/042/report.json
