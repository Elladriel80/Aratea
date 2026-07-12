**Run 437 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Jul 11, 2026?
Bin cible : `KXLOWTBOS-26JUL11-B66.5` · Outcome : NO · Low observée (bin gagnant) : ≥67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.289, Brier=0.0836, P&L réel=$-8.56
- `learned_v2` (challenger) — p_yes=0.312, Brier=0.0976, P&L théorique=$-8.56
- `kalshi_mid_baseline` (baseline) — p_yes=0.145, Brier=0.0210, P&L théorique=$-8.56 ⭐

Verdict run 437 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/437/report.json
