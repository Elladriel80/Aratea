**Run 129 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jun 1, 2026?
Bin cible : `KXLOWTDC-26JUN01-B59.5` · Outcome : YES · Low observée (bin gagnant) : 59-60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.184, Brier=0.6655, P&L réel=$-20.60
- `learned_v2` (challenger) — p_yes=0.092, Brier=0.8237, P&L théorique=$-20.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.485, Brier=0.2652, P&L théorique=$-20.60 ⭐

Verdict run 129 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/129/report.json
