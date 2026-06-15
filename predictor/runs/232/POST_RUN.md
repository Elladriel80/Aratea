**Run 232 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 14, 2026?
Bin cible : `KXLOWTMIA-26JUN14-B76.5` · Outcome : YES · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.209, Brier=0.6249, P&L réel=$+534.65 ⭐
- `learned_v2` (challenger) — p_yes=0.073, Brier=0.8586, P&L théorique=$+534.65
- `kalshi_mid_baseline` (baseline) — p_yes=0.075, Brier=0.8556, P&L théorique=$+534.65

Verdict run 232 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/232/report.json
