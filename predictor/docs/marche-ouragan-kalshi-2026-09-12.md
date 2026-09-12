# Marché ouragan Kalshi, puis NHC a-decks / b-decks

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Deuxième mesure Phase 2 pour les ouragans. Variable catalogue :
**Marché ouragan Kalshi**.
Si le livre est trop mince pour noter : **NHC a-decks / b-decks**.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle Kalshi en ligne n'a pas été changé. Aucun pari
avec de l'argent réel. Aucun chiffre n'a été inventé. On n'a pas
commencé Méditerranée ni Inde. On n'a pas inventé de score pour la
sécheresse.

## 1. Est-ce qu'un marché ouragan Kalshi se joue ?

Oui, il existe des contrats. Non, on ne peut pas les noter contre
la vérité officielle HURDAT2.

L'API publique (lecture seule, 12 septembre 2026) donne :

| Quoi | Nombre |
|---|---:|
| Séries climat / ouragan | 59 |
| Événements | 181 |
| Contrats | 381 |
| Contrats avec un peu de volume | 266 |
| Contrats avec bid et ask tous les deux > 0 | 202 |
| Contrats déjà réglés oui ou non | 96 |
| Saisons réglées, avec un prix, et HURDAT2 officiel | **0** |

La barre du projet pour une cible saisonnière est 10 saisons. Ici : 0.
Donc : **trop mince pour noter**.

Les comptes de saison (combien d'ouragans, combien de majeurs) ont
des titres pour 2022, 2023, 2024, 2025 et 2026. Les saisons 2022 à
2025 sont des coquilles vides : l'événement existe, les contrats et
les prix ont disparu de l'API. La saison 2026 a des prix, mais le
fichier HURDAT2 officiel s'arrête à 2025.

Les marchés « ouragan touche telle ville » (Miami, New York, etc.)
sont dans le même cas : un titre, zéro contrat.

## 2. Comment Kalshi paie (les règles écrites)

Pas un résumé inventé. Les phrases viennent des contrats.

**Nombre d'ouragans (KXHURCTOT), saison 2026.**
« If the NOAA's National Hurricane Center records more than K
hurricanes of hurricane category 1 or above between January 1, 2026
and December 01, 2026, then the market resolves to Yes. »
Source de règlement : NHC / NOAA. Certification : LTHUR.pdf.

**Nombre de majeurs (KXHURCTOTMAJ).**
Même fenêtre, « category 3 or above », même source NHC.

**Catégorie d'une tempête nommée (KXHURCAT).**
« If [nom] reaches maximum sustained winds of greater than or equal
to [157 / 130 / ...] mph, then the market resolves to Yes. »
C'est un contrat par nom de la liste 2026, pas une saison entière.

**Premier ouragan, noms, dates, landfall Hawaï / Caroline du Nord.**
D'autres livres 2026 existent. Ils paient sur un nom, une date ou
un atterrissage local. Ce n'est pas le compte Atlantique de la
mutuelle.

Aucun de ces livres n'a été tradé avec de l'argent réel ici.

## 3. Prix 2026 contre la climato HURDAT2 (PR 241)

Même fichier que PR 241 : `hurdat2-1851-2025-02272026.txt`.
Relu ici : **2004** systèmes, **978** HU, **342** majeurs, **376**
landfalls encore ouragan. Identique à PR 241. Aucun chiffre nouveau
inventé.

Attention : on est le 12 septembre. Une partie de la saison 2026
est déjà passée. La climato ci-dessous est la chance sur **toute**
une saison, de 1851 à 2025. Ce n'est **pas** un score. 2026 n'a
pas encore de HURDAT2 officiel.

Prix = milieu entre l'achat et la vente, le 12 septembre 2026.

**Combien d'ouragans Atlantique (plus que K) :**

| Plus que | Prix marché | Climato HURDAT2 (1er janv. au 1er déc.) |
|---|---:|---:|
| 4 | 0,075 | 0,583 |
| 5 | 0,050 | 0,463 |
| 6 | 0,045 | 0,320 |
| 7 | 0,015 | 0,183 |
| 8 | 0,005 | 0,137 |
| 9 | 0,005 | 0,097 |
| 10 | 0,005 | 0,046 |
| 12 | 0,005 | 0,011 |
| 15 | 0,005 | 0,000 |

**Combien de majeurs (plus que K) :**

| Plus que | Prix marché | Climato HURDAT2 (1er janv. au 1er déc.) |
|---|---:|---:|
| 0 | 0,410 | 0,811 |
| 1 | 0,155 | 0,543 |
| 2 | 0,095 | 0,286 |
| 3 | 0,045 | 0,160 |
| 4 | 0,025 | 0,097 |
| 5 | 0,010 | 0,046 |
| 6 | 0,010 | 0,011 |
| 7 | 0,010 | 0,000 |

Le marché du 12 septembre est plus bas que la climato de saison
entière. C'est normal en milieu de saison, et on n'en fait pas un
edge. On n'a pas le résultat 2026.

L'année civile complète (jusqu'au 31 décembre) donne presque les
mêmes chances. L'écart est écrit dans
`data/truth/kalshi_hurricane/kalshi_hurricane_report.md`.

## 4. Donc on passe au repli : NHC a-decks / b-decks

Le marché ne se note pas (0 saison). On mesure alors les prévisions
officielles NHC (a-decks) et le best-track opérationnel (b-decks)
contre le même HURDAT2.

Archives publiques : https://ftp.nhc.noaa.gov/atcf/archive/
On garde seulement OFCL (prévision officielle) et OCD5 (la
climatologie-persistance déjà dans le fichier). On n'invente pas
d'autre modèle.

**Ouragan formation :** bloquée. Un a-deck commence quand le
système est déjà numéroté. Ce n'est pas une prévision de naissance.

**Ouragan landfall oui/non :** bloquée. Il faudrait dessiner une
côte. Le PDF HURDAT2 dit déjà que le drapeau L est incomplet sur
certaines années. On ne redessine pas la carte. On peut seulement
mesurer l'écart de trajectoire au point L, si une prévision tombe
pile à cette heure.

**Ouragan intensité :** mesurée (OFCL contre OCD5 contre HURDAT2,
même instant, sans interpoler). Les comptes sont dans
`data/truth/nhc_decks/nhc_decks_report.md`.

## Verdicts (noms du catalogue, non renommés)

| Nom | Verdict |
|---|---|
| Marché ouragan Kalshi | bloquée |
| NHC a-decks / b-decks | (voir le rapport decks après le run) |
| Ouragan formation | bloquée |
| Ouragan intensité | (voir le rapport decks) |
| Ouragan landfall | bloquée |
| HURDAT2 / IBTrACS | testée, ça aide |
| Sécheresse Méditerranée | cible Tier 1 (pas encore testée) |
| Sécheresse Inde | cible Tier 1 (pas encore testée) |

## Décision

On ne change pas le modèle Kalshi en ligne.

Pourquoi : ce n'est pas un test de température. Le livre ouragan
n'a aucune saison notable contre HURDAT2. La gate (10 saisons,
BSS > 0,05) n'est pas jouable ici. On n'invente pas de BSS.

## Comment relancer

Dans le dossier `predictor`, avec internet la première fois :

```
python scripts/eval_marche_ouragan_kalshi.py
```

Sans internet, si les fichiers sont déjà là :

```
python scripts/eval_marche_ouragan_kalshi.py --skip-fetch
```

Les fichiers bruts restent locaux (caches). Les comptes sont dans
`data/truth/kalshi_hurricane/` et `data/truth/nhc_decks/`.

Pas de changement du texte du site. Pas de trading réel.
