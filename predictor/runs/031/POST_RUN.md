**Run 031 — résolu NO · Multi-model A/B**

Event : Highest temperature in Boston on May 22, 2026?
Bin cible : `KXHIGHTBOS-26MAY22-B62.5` · Outcome : NO · Low observée (bin gagnant) : ≤62°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.119, Brier=0.0143, P&L réel=$+5.85 ⭐
- `learned_v2` (challenger) — p_yes=0.200, Brier=0.0400, P&L théorique=$+5.85
- `kalshi_mid_baseline` (baseline) — p_yes=0.225, Brier=0.0506, P&L théorique=$+5.85

Verdict run 031 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/031/report.json
