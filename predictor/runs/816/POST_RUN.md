**Run 816 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Sep 27, 2026?
Bin cible : `KXHIGHTSFO-26SEP27-B68.5` · Outcome : NO · Low observée (bin gagnant) : 64-65°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.145, Brier=0.0211, P&L réel=$+63.67 ⭐
- `learned_v2` (challenger) — p_yes=0.185, Brier=0.0342, P&L théorique=$+63.67
- `kalshi_mid_baseline` (baseline) — p_yes=0.535, Brier=0.2862, P&L théorique=$+63.67

Verdict run 816 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/816/report.json
