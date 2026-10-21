**Run 987 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Oct 20, 2026?
Bin cible : `KXLOWTCHI-26OCT20-B46.5` · Outcome : YES · Low observée (bin gagnant) : 46-47°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.400, Brier=0.3597, P&L réel=$+265.68 ⭐
- `learned_v2` (challenger) — p_yes=0.237, Brier=0.5824, P&L théorique=$+265.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.280, Brier=0.5184, P&L théorique=$+265.68

Verdict run 987 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/987/report.json
