**Run 786 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Sep 23, 2026?
Bin cible : `KXHIGHTSFO-26SEP23-B79.5` · Outcome : NO · Low observée (bin gagnant) : 77-78°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.147, Brier=0.0216, P&L réel=$+21.45 ⭐
- `learned_v2` (challenger) — p_yes=0.221, Brier=0.0489, P&L théorique=$+21.45
- `kalshi_mid_baseline` (baseline) — p_yes=0.275, Brier=0.0756, P&L théorique=$+21.45

Verdict run 786 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/786/report.json
