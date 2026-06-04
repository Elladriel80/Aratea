**Run 159 — résolu NO · Multi-model A/B**

Event : Highest temperature in Boston on Jun 3, 2026?
Bin cible : `KXHIGHTBOS-26JUN03-B76.5` · Outcome : NO · Low observée (bin gagnant) : 80-81°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.115, Brier=0.0132, P&L réel=$+6.21 ⭐
- `learned_v2` (challenger) — p_yes=0.189, Brier=0.0357, P&L théorique=$+6.21
- `kalshi_mid_baseline` (baseline) — p_yes=0.230, Brier=0.0529, P&L théorique=$+6.21

Verdict run 159 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/159/report.json
