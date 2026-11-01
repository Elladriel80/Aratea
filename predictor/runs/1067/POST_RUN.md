**Run 1067 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Oct 31, 2026?
Bin cible : `KXLOWTDEN-26OCT31-B43.5` · Outcome : YES · Low observée (bin gagnant) : 43-44°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.303, Brier=0.4852, P&L réel=$+397.13 ⭐
- `learned_v2` (challenger) — p_yes=0.123, Brier=0.7692, P&L théorique=$+397.13
- `kalshi_mid_baseline` (baseline) — p_yes=0.245, Brier=0.5700, P&L théorique=$+397.13

Verdict run 1067 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1067/report.json
