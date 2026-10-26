**Run 1023 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 25, 2026?
Bin cible : `KXHIGHTSFO-26OCT25-B69.5` · Outcome : NO · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.179, Brier=0.0320, P&L réel=$+74.39 ⭐
- `learned_v2` (challenger) — p_yes=0.246, Brier=0.0604, P&L théorique=$+74.39
- `kalshi_mid_baseline` (baseline) — p_yes=0.435, Brier=0.1892, P&L théorique=$+74.39

Verdict run 1023 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1023/report.json
