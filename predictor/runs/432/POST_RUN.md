**Run 432 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 11, 2026?
Bin cible : `KXLOWTSFO-26JUL11-B53.5` · Outcome : YES · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.391, Brier=0.3710, P&L réel=$+447.72 ⭐
- `learned_v2` (challenger) — p_yes=0.196, Brier=0.6468, P&L théorique=$+447.72
- `kalshi_mid_baseline` (baseline) — p_yes=0.160, Brier=0.7056, P&L théorique=$+447.72

Verdict run 432 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/432/report.json
