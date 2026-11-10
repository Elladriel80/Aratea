**Run 1139 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Nov 9, 2026?
Bin cible : `KXHIGHTSFO-26NOV09-B70.5` · Outcome : NO · Low observée (bin gagnant) : 72-73°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.154, Brier=0.0239, P&L réel=$+111.10 ⭐
- `learned_v2` (challenger) — p_yes=0.242, Brier=0.0586, P&L théorique=$+111.10
- `kalshi_mid_baseline` (baseline) — p_yes=0.505, Brier=0.2550, P&L théorique=$+111.10

Verdict run 1139 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1139/report.json
