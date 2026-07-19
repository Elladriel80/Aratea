**Run 488 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 18, 2026?
Bin cible : `KXLOWTSFO-26JUL18-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.318, Brier=0.4647, P&L réel=$+186.00 ⭐
- `learned_v2` (challenger) — p_yes=0.117, Brier=0.7793, P&L théorique=$+186.00
- `kalshi_mid_baseline` (baseline) — p_yes=0.250, Brier=0.5625, P&L théorique=$+186.00

Verdict run 488 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/488/report.json
