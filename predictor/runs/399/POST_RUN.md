**Run 399 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 7, 2026?
Bin cible : `KXLOWTSFO-26JUL07-B54.5` · Outcome : YES · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.320, Brier=0.4622, P&L réel=$+345.61 ⭐
- `learned_v2` (challenger) — p_yes=0.121, Brier=0.7724, P&L théorique=$+345.61
- `kalshi_mid_baseline` (baseline) — p_yes=0.155, Brier=0.7140, P&L théorique=$+345.61

Verdict run 399 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/399/report.json
