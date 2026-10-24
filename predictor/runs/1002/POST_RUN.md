**Run 1002 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Oct 22, 2026?
Bin cible : `KXLOWTCHI-26OCT22-B52.5` · Outcome : NO · Low observée (bin gagnant) : 50-51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.253, Brier=0.0639, P&L réel=$-95.76
- `learned_v2` (challenger) — p_yes=0.082, Brier=0.0067, P&L théorique=$-95.76 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.095, Brier=0.0090, P&L théorique=$-95.76

Verdict run 1002 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1002/report.json
