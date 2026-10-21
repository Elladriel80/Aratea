**Run 991 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Oct 20, 2026?
Bin cible : `KXLOWTDEN-26OCT20-B40.5` · Outcome : NO · Low observée (bin gagnant) : ≥47°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.273, Brier=0.0743, P&L réel=$-103.35
- `learned_v2` (challenger) — p_yes=0.114, Brier=0.0130, P&L théorique=$-103.35 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.150, Brier=0.0225, P&L théorique=$-103.35

Verdict run 991 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/991/report.json
