**Run 303 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 24, 2026?
Bin cible : `KXLOWTNYC-26JUN24-B63.5` · Outcome : YES · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.482, Brier=0.2685, P&L réel=$+70.20 ⭐
- `learned_v2` (challenger) — p_yes=0.369, Brier=0.3983, P&L théorique=$+70.20
- `kalshi_mid_baseline` (baseline) — p_yes=0.350, Brier=0.4225, P&L théorique=$+70.20

Verdict run 303 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/303/report.json
