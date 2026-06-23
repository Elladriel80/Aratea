**Run 294 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 22, 2026?
Bin cible : `KXLOWTDC-26JUN22-B70.5` · Outcome : NO · Low observée (bin gagnant) : ≥71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.278, Brier=0.0770, P&L réel=$+20.08
- `learned_v2` (challenger) — p_yes=0.130, Brier=0.0170, P&L théorique=$+20.08 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.365, Brier=0.1332, P&L théorique=$+20.08

Verdict run 294 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/294/report.json
