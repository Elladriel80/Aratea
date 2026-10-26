**Run 1018 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Oct 25, 2026?
Bin cible : `KXLOWTSFO-26OCT25-B51.5` · Outcome : YES · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.309, Brier=0.4771, P&L réel=$-96.66
- `learned_v2` (challenger) — p_yes=0.106, Brier=0.8000, P&L théorique=$-96.66
- `kalshi_mid_baseline` (baseline) — p_yes=0.460, Brier=0.2916, P&L théorique=$-96.66 ⭐

Verdict run 1018 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1018/report.json
