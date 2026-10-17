**Run 964 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 16, 2026?
Bin cible : `KXHIGHTSFO-26OCT16-B82.5` · Outcome : NO · Low observée (bin gagnant) : 84-85°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.164, Brier=0.0269, P&L réel=$-62.27
- `learned_v2` (challenger) — p_yes=0.300, Brier=0.0903, P&L théorique=$-62.27
- `kalshi_mid_baseline` (baseline) — p_yes=0.035, Brier=0.0012, P&L théorique=$-62.27 ⭐

Verdict run 964 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/964/report.json
