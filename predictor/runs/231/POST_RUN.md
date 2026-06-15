**Run 231 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 14, 2026?
Bin cible : `KXLOWTMIA-26JUN14-B78.5` · Outcome : NO · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.271, Brier=0.0732, P&L réel=$+255.64 ⭐
- `learned_v2` (challenger) — p_yes=0.318, Brier=0.1013, P&L théorique=$+255.64
- `kalshi_mid_baseline` (baseline) — p_yes=0.855, Brier=0.7310, P&L théorique=$+255.64

Verdict run 231 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/231/report.json
