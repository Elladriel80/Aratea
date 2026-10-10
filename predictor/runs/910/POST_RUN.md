**Run 910 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Oct 9, 2026?
Bin cible : `KXLOWTDC-26OCT09-B52.5` · Outcome : YES · Low observée (bin gagnant) : 52-53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.271, Brier=0.5310, P&L réel=$-44.52
- `learned_v2` (challenger) — p_yes=0.085, Brier=0.8375, P&L théorique=$-44.52
- `kalshi_mid_baseline` (baseline) — p_yes=0.470, Brier=0.2809, P&L théorique=$-44.52 ⭐

Verdict run 910 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/910/report.json
