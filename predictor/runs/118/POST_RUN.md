**Run 118 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 1, 2026?
Bin cible : `KXLOWTNYC-26JUN01-B56.5` · Outcome : NO · Low observée (bin gagnant) : ≤54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.227, Brier=0.0515, P&L réel=$+10.38 ⭐
- `learned_v2` (challenger) — p_yes=0.323, Brier=0.1046, P&L théorique=$+10.38
- `kalshi_mid_baseline` (baseline) — p_yes=0.335, Brier=0.1122, P&L théorique=$+10.38

Verdict run 118 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/118/report.json
