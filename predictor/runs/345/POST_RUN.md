**Run 345 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Seattle on Jun 29, 2026?
Bin cible : `KXLOWTSEA-26JUN29-B52.5` · Outcome : YES · Low observée (bin gagnant) : 52-53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.400, Brier=0.3602, P&L réel=$+137.00
- `learned_v2` (challenger) — p_yes=0.522, Brier=0.2285, P&L théorique=$+137.00 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.315, Brier=0.4692, P&L théorique=$+137.00

Verdict run 345 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/345/report.json
