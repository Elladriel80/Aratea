**Run 989 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Oct 20, 2026?
Bin cible : `KXLOWTBOS-26OCT20-B46.5` · Outcome : NO · Low observée (bin gagnant) : 44-45°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.387, Brier=0.1494, P&L réel=$-103.41
- `learned_v2` (challenger) — p_yes=0.651, Brier=0.4242, P&L théorique=$-103.41
- `kalshi_mid_baseline` (baseline) — p_yes=0.135, Brier=0.0182, P&L théorique=$-103.41 ⭐

Verdict run 989 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/989/report.json
