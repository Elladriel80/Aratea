**Run 1027 — résolu NO · Multi-model A/B**

Event : Highest temperature in Boston on Oct 25, 2026?
Bin cible : `KXHIGHTBOS-26OCT25-B64.5` · Outcome : NO · Low observée (bin gagnant) : 62-63°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.298, Brier=0.0891, P&L réel=$+125.99 ⭐
- `learned_v2` (challenger) — p_yes=0.510, Brier=0.2605, P&L théorique=$+125.99
- `kalshi_mid_baseline` (baseline) — p_yes=0.565, Brier=0.3192, P&L théorique=$+125.99

Verdict run 1027 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1027/report.json
