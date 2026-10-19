**Run 971 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Oct 18, 2026?
Bin cible : `KXLOWTSFO-26OCT18-B58.5` · Outcome : YES · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.146, Brier=0.7287, P&L réel=$+1083.17 ⭐
- `learned_v2` (challenger) — p_yes=0.034, Brier=0.9334, P&L théorique=$+1083.17
- `kalshi_mid_baseline` (baseline) — p_yes=0.075, Brier=0.8556, P&L théorique=$+1083.17

Verdict run 971 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/971/report.json
