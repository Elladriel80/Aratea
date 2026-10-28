**Run 1031 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 27, 2026?
Bin cible : `KXLOWTNYC-26OCT27-B45.5` · Outcome : YES · Low observée (bin gagnant) : 45-46°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.294, Brier=0.4987, P&L réel=$+1781.33 ⭐
- `learned_v2` (challenger) — p_yes=0.093, Brier=0.8228, P&L théorique=$+1781.33
- `kalshi_mid_baseline` (baseline) — p_yes=0.055, Brier=0.8930, P&L théorique=$+1781.33

Verdict run 1031 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1031/report.json
