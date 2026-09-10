**Run 673 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Sep 9, 2026?
Bin cible : `KXLOWTDC-26SEP09-B68.5` · Outcome : NO · Low observée (bin gagnant) : ≥69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.426, Brier=0.1812, P&L réel=$+65.28
- `learned_v2` (challenger) — p_yes=0.285, Brier=0.0812, P&L théorique=$+65.28 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.480, Brier=0.2304, P&L théorique=$+65.28

Verdict run 673 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/673/report.json
