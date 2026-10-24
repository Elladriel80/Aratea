**Run 1010 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 22, 2026?
Bin cible : `KXHIGHTSFO-26OCT22-B65.5` · Outcome : NO · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.247, Brier=0.0609, P&L réel=$+75.24
- `learned_v2` (challenger) — p_yes=0.237, Brier=0.0562, P&L théorique=$+75.24 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.440, Brier=0.1936, P&L théorique=$+75.24

Verdict run 1010 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1010/report.json
