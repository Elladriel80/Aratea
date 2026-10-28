**Run 1042 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 27, 2026?
Bin cible : `KXHIGHTSFO-26OCT27-B64.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.207, Brier=0.0427, P&L réel=$+266.40 ⭐
- `learned_v2` (challenger) — p_yes=0.242, Brier=0.0588, P&L théorique=$+266.40
- `kalshi_mid_baseline` (baseline) — p_yes=0.720, Brier=0.5184, P&L théorique=$+266.40

Verdict run 1042 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1042/report.json
