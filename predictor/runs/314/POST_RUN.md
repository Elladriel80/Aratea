**Run 314 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 24, 2026?
Bin cible : `KXLOWTDEN-26JUN24-B59.5` · Outcome : YES · Low observée (bin gagnant) : 59-60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.508, Brier=0.2420, P&L réel=$+215.05 ⭐
- `learned_v2` (challenger) — p_yes=0.424, Brier=0.3321, P&L théorique=$+215.05
- `kalshi_mid_baseline` (baseline) — p_yes=0.150, Brier=0.7225, P&L théorique=$+215.05

Verdict run 314 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/314/report.json
