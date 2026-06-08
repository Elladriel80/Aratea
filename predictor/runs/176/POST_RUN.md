**Run 176 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 5, 2026?
Bin cible : `KXLOWTDC-26JUN05-B64.5` · Outcome : YES · Low observée (bin gagnant) : 64-65°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.189, Brier=0.6585, P&L réel=$-22.05
- `learned_v2` (challenger) — p_yes=0.500, Brier=0.2500, P&L théorique=$-22.05 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.475, Brier=0.2756, P&L théorique=$-22.05

Verdict run 176 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/176/report.json
