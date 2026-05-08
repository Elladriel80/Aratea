> [Read in English](README.md)

# augure-rounds

Mécanique d'émission des tokens **AUG-POC** sur la base de la valeur travail apportée au projet Augure.

> Augure est un projet open-source de prediction markets météo et d'assurance paramétrique décentralisée. Sa phase POC actuelle valide un edge prédictif sur les marchés Kalshi.

## Principe

Tout apport au projet — cash, code, donnée, design, recherche — relève de la même substance : la **valeur travail**. Ce repo opère le moteur qui :

1. **Collecte** mensuellement les contributions de chaque participant enregistré, **strictement à partir d'artefacts Git observables** (PRs mergés, diffs, commits, reviews). Pas d'auto-déclaration, pas d'heures déclarées, pas de narratif.
2. **Estime** leur valeur en équivalent **BTC** (« combien le marché aurait-il payé pour ce livrable ? »), via un agent IA suivant un rubric public.
3. **Ouvre une fenêtre de challenge publique de 7 jours** sur le rapport de valuation publié.
4. **Libère** les tokens AUG-POC à la fin de la fenêtre, mintés à hauteur de `valeur_BTC / NAV_par_token`.

Le cash suit le même chemin : un dépôt BTC (ou USDC au spot) est traité comme de la valeur travail déjà cristallisée.

## Règles dures

- **Faits seuls.** Source de vérité : Git. Ce qui n'est pas commité n'existe pas pour la valuation.
- **Push KO = 0.** PR rejetés, fermés sans merge ou abandonnés n'ont aucune valeur.
- **Unité BTC.** Taux horaires, NAV, valuations, mints — tout en BTC ou sats.
- **Pas de privilège catégoriel.** Un cash investor est traité comme un contributeur code : un apport de valeur, valorisé puis minté.

## Documents de référence

- **[`RUBRIC.fr.md`](RUBRIC.fr.md)** — procédure de valuation suivie par l'agent IA.
- **[`HOURLY_RATES.fr.md`](HOURLY_RATES.fr.md)** — grille de taux par profil (en sats/h).
- **[`agent/PROMPT.fr.md`](agent/PROMPT.fr.md)** — prompt système de l'agent.
- **[`WALLETS.md`](WALLETS.md)** — registry public des wallets.
- **[`CONTRIBUTING.fr.md`](CONTRIBUTING.fr.md)** — comment participer.

## Cycle mensuel

| Jour | Action |
|---|---|
| 1 | Snapshot automatique des contributions mergées du mois M-1 |
| 1-2 | L'agent IA produit `valuation_report.md` (PR ouverte) |
| 1-7 | Fenêtre de challenge publique (challenge formel par commentaire signé) |
| 7 | Auto-merge si non contesté → mint multisig. Sinon → vote du panel Top X holders |

## Valuations contestées — le panel des holders

Si un challenge formel est déposé pendant la fenêtre, la décision passe au **panel des Top X holders en tokens, chacun ayant 1 voix** (non pondéré par stake). Majorité simple.

| Phase | Contributeurs | X |
|---|---|---|
| 1 | ≤ 20 | 5 |
| 2 | 20-50 | 7 |
| 3 | > 50 | 11 |

Le panel valide la valuation de l'IA telle quelle, ou la renvoie avec instructions écrites pour révision.

## Garde-fous

- Cap mensuel : ≤ 10 % du supply circulant minté par fenêtre.
- Cap par apporteur : ≤ 30 % du mint mensuel.
- Valuations > 0,01 BTC dans un round : vote panel automatique même sans contestation.
- Cooldown nouveau entrant : première PR mergée > 30 jours avant éligibilité au mint.
- Slashing : claw-back sur 6 mois en cas de fraude établie par vote 67 %.

## Statut

Phase 1 (MVP 4 semaines) :
- [ ] RUBRIC, HOURLY_RATES, PROMPT (premiers drafts livrés)
- [ ] Script de collecte GitHub
- [ ] Multisig Safe sur Base
- [ ] Round genesis (valuation rétroactive du travail pré-open-source)
- [ ] Premier round live

## Licence

Code et documents sous [Apache 2.0](LICENSE).
