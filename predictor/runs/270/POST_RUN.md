**Run 270 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 20, 2026?
Bin cible : `KXLOWTNYC-26JUN20-B64.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.186, Brier=0.0345, P&L réel=$+25.92 ⭐
- `learned_v2` (challenger) — p_yes=0.216, Brier=0.0468, P&L théorique=$+25.92
- `kalshi_mid_baseline` (baseline) — p_yes=0.405, Brier=0.1640, P&L théorique=$+25.92

Verdict run 270 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/270/report.json
