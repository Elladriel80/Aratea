**Run 458 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 14, 2026?
Bin cible : `KXLOWTCHI-26JUL14-B73.5` · Outcome : YES · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.564, Brier=0.1902, P&L réel=$+223.48 ⭐
- `learned_v2` (challenger) — p_yes=0.542, Brier=0.2098, P&L théorique=$+223.48
- `kalshi_mid_baseline` (baseline) — p_yes=0.245, Brier=0.5700, P&L théorique=$+223.48

Verdict run 458 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/458/report.json
