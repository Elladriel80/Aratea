**Run 676 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Sep 9, 2026?
Bin cible : `KXLOWTMIA-26SEP09-B81.5` · Outcome : NO · Low observée (bin gagnant) : 79-80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.258, Brier=0.0666, P&L réel=$-70.98
- `learned_v2` (challenger) — p_yes=0.085, Brier=0.0071, P&L théorique=$-70.98
- `kalshi_mid_baseline` (baseline) — p_yes=0.065, Brier=0.0042, P&L théorique=$-70.98 ⭐

Verdict run 676 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/676/report.json
