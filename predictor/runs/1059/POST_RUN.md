**Run 1059 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 29, 2026?
Bin cible : `KXHIGHTSFO-26OCT29-B65.5` · Outcome : YES · Low observée (bin gagnant) : 65-66°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.229, Brier=0.5943, P&L réel=$+669.81
- `learned_v2` (challenger) — p_yes=0.321, Brier=0.4608, P&L théorique=$+669.81 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.170, Brier=0.6889, P&L théorique=$+669.81

Verdict run 1059 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1059/report.json
