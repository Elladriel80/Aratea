**Run 1171 — résolu NO · Multi-model A/B**

Event : Highest temperature in Boston on Nov 13, 2026?
Bin cible : `KXHIGHTBOS-26NOV13-B48.5` · Outcome : NO · Low observée (bin gagnant) : 46-47°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.105, Brier=0.0111, P&L réel=$+102.48
- `learned_v2` (challenger) — p_yes=0.102, Brier=0.0104, P&L théorique=$+102.48 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.515, Brier=0.2652, P&L théorique=$+102.48

Verdict run 1171 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1171/report.json
