**Run 480 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 17, 2026?
Bin cible : `KXLOWTSFO-26JUL17-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.429, Brier=0.3263, P&L réel=$+242.57 ⭐
- `learned_v2` (challenger) — p_yes=0.271, Brier=0.5317, P&L théorique=$+242.57
- `kalshi_mid_baseline` (baseline) — p_yes=0.225, Brier=0.6006, P&L théorique=$+242.57

Verdict run 480 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/480/report.json
