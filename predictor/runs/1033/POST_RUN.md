**Run 1033 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Oct 27, 2026?
Bin cible : `KXLOWTSFO-26OCT27-B55.5` · Outcome : YES · Low observée (bin gagnant) : 55-56°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.410, Brier=0.3477, P&L réel=$+200.64 ⭐
- `learned_v2` (challenger) — p_yes=0.237, Brier=0.5817, P&L théorique=$+200.64
- `kalshi_mid_baseline` (baseline) — p_yes=0.340, Brier=0.4356, P&L théorique=$+200.64

Verdict run 1033 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1033/report.json
