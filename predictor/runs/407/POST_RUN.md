**Run 407 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 8, 2026?
Bin cible : `KXLOWTSFO-26JUL08-B53.5` · Outcome : YES · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.227, Brier=0.5981, P&L réel=$+263.02 ⭐
- `learned_v2` (challenger) — p_yes=0.098, Brier=0.8131, P&L théorique=$+263.02
- `kalshi_mid_baseline` (baseline) — p_yes=0.165, Brier=0.6972, P&L théorique=$+263.02

Verdict run 407 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/407/report.json
