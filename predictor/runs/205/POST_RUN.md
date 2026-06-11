**Run 205 — résolu YES · Multi-model A/B**

Event : Highest temperature in Washington DC on Jun 9, 2026?
Bin cible : `KXHIGHTDC-26JUN09-B83.5` · Outcome : YES · Low observée (bin gagnant) : 83-84°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.157, Brier=0.7115, P&L réel=$-12.15
- `learned_v2` (challenger) — p_yes=0.203, Brier=0.6347, P&L théorique=$-12.15
- `kalshi_mid_baseline` (baseline) — p_yes=0.285, Brier=0.5112, P&L théorique=$-12.15 ⭐

Verdict run 205 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/205/report.json
