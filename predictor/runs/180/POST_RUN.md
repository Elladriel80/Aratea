**Run 180 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 5, 2026?
Bin cible : `KXLOWTMIA-26JUN05-B76.5` · Outcome : YES · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.407, Brier=0.3516, P&L réel=$+63.14 ⭐
- `learned_v2` (challenger) — p_yes=0.316, Brier=0.4673, P&L théorique=$+63.14
- `kalshi_mid_baseline` (baseline) — p_yes=0.180, Brier=0.6724, P&L théorique=$+63.14

Verdict run 180 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/180/report.json
