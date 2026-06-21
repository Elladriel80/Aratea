**Run 273 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jun 20, 2026?
Bin cible : `KXLOWTSFO-26JUN20-B57.5` · Outcome : NO · Low observée (bin gagnant) : ≥58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.361, Brier=0.1307, P&L réel=$+59.78 ⭐
- `learned_v2` (challenger) — p_yes=0.434, Brier=0.1888, P&L théorique=$+59.78
- `kalshi_mid_baseline` (baseline) — p_yes=0.610, Brier=0.3721, P&L théorique=$+59.78

Verdict run 273 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/273/report.json
