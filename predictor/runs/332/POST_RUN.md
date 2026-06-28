**Run 332 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 26, 2026?
Bin cible : `KXLOWTDEN-26JUN26-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.267, Brier=0.5371, P&L réel=$+504.78 ⭐
- `learned_v2` (challenger) — p_yes=0.082, Brier=0.8431, P&L théorique=$+504.78
- `kalshi_mid_baseline` (baseline) — p_yes=0.105, Brier=0.8010, P&L théorique=$+504.78

Verdict run 332 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/332/report.json
