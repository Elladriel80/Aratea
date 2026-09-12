**Run 697 — résolu NO · Multi-model A/B**

Event : Highest temperature in Phoenix on Sep 11, 2026?
Bin cible : `KXHIGHTPHX-26SEP11-B107.5` · Outcome : NO · Low observée (bin gagnant) : 105-106°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.171, Brier=0.0293, P&L réel=$+10.37 ⭐
- `learned_v2` (challenger) — p_yes=0.276, Brier=0.0759, P&L théorique=$+10.37
- `kalshi_mid_baseline` (baseline) — p_yes=0.305, Brier=0.0930, P&L théorique=$+10.37

Verdict run 697 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/697/report.json
