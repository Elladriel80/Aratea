**Run 745 — résolu NO · Multi-model A/B**

Event : Highest temperature in Seattle on Sep 17, 2026?
Bin cible : `KXHIGHTSEA-26SEP17-B78.5` · Outcome : NO · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.120, Brier=0.0144, P&L réel=$+12.39 ⭐
- `learned_v2` (challenger) — p_yes=0.207, Brier=0.0427, P&L théorique=$+12.39
- `kalshi_mid_baseline` (baseline) — p_yes=0.295, Brier=0.0870, P&L théorique=$+12.39

Verdict run 745 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/745/report.json
