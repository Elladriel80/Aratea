**Run 792 — résolu NO · Multi-model A/B**

Event : Highest temperature in Boston on Sep 23, 2026?
Bin cible : `KXHIGHTBOS-26SEP23-B62.5` · Outcome : NO · Low observée (bin gagnant) : 64-65°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.269, Brier=0.0722, P&L réel=$+76.47 ⭐
- `learned_v2` (challenger) — p_yes=0.425, Brier=0.1806, P&L théorique=$+76.47
- `kalshi_mid_baseline` (baseline) — p_yes=0.575, Brier=0.3306, P&L théorique=$+76.47

Verdict run 792 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/792/report.json
