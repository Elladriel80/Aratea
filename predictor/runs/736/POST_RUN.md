**Run 736 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Sep 17, 2026?
Bin cible : `KXHIGHTSFO-26SEP17-B73.5` · Outcome : NO · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.145, Brier=0.0211, P&L réel=$+22.55 ⭐
- `learned_v2` (challenger) — p_yes=0.195, Brier=0.0380, P&L théorique=$+22.55
- `kalshi_mid_baseline` (baseline) — p_yes=0.275, Brier=0.0756, P&L théorique=$+22.55

Verdict run 736 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/736/report.json
