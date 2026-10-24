**Run 1012 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 22, 2026?
Bin cible : `KXHIGHTSFO-26OCT22-B63.5` · Outcome : YES · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.226, Brier=0.5988, P&L réel=$+702.24
- `learned_v2` (challenger) — p_yes=0.319, Brier=0.4644, P&L théorique=$+702.24 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.120, Brier=0.7744, P&L théorique=$+702.24

Verdict run 1012 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1012/report.json
