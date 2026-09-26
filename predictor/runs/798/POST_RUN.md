**Run 798 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Sep 25, 2026?
Bin cible : `KXLOWTBOS-26SEP25-B56.5` · Outcome : NO · Low observée (bin gagnant) : 50-51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.392, Brier=0.1534, P&L réel=$-51.30
- `learned_v2` (challenger) — p_yes=0.646, Brier=0.4178, P&L théorique=$-51.30
- `kalshi_mid_baseline` (baseline) — p_yes=0.100, Brier=0.0100, P&L théorique=$-51.30 ⭐

Verdict run 798 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/798/report.json
