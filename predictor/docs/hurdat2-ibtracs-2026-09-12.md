# HURDAT2 / IBTrACS : l'histoire officielle des ouragans, comptée

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Première mesure Phase 2 pour les ouragans. Vérité catalogue :
**HURDAT2 / IBTrACS**.
Cibles catalogue : **Ouragan formation**, **Ouragan intensité**,
**Ouragan landfall**.

Cette note dit seulement ce qui a été mesuré. Le site public n'a pas
été changé. Le modèle Kalshi en ligne n'a pas été changé. Aucun pari
avec de l'argent réel. Aucun chiffre n'a été inventé. On n'a pas
commencé les prévisions NHC (a-decks / b-decks). On n'a pas commencé
Méditerranée ni Inde. On n'a pas inventé de score pour la sécheresse US.

## D'où viennent les chiffres

Deux fichiers publics, Atlantique seulement (océan, golfe du Mexique,
mer des Caraïbes).

1. **HURDAT2**, National Hurricane Center (NOAA). Fichier
   `hurdat2-1851-2025-02272026.txt`. Page :
   https://www.nhc.noaa.gov/data/
   Dossier : https://www.nhc.noaa.gov/data/hurdat/
   Format : https://www.nhc.noaa.gov/data/hurdat/hurdat2-format-atl-1851-2021.pdf
   Mis à jour le 27 février 2026 pour ajouter la saison 2025.
   La saison 2026 n'y est pas encore.

2. **IBTrACS** v04r01, NCEI (NOAA). Fichier Atlantique nord
   `ibtracs.NA.list.v04r01.csv` (daté 10 septembre 2026 sur le serveur).
   https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/
   Notice des colonnes :
   https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/doc/IBTrACS_v04r01_column_documentation.pdf

Les statuts (TD, TS, HU, etc.) et le drapeau L sont ceux du fichier.
Les catégories 1 à 5 viennent de la table officielle NHC, en nœuds :
https://www.nhc.noaa.gov/aboutsshws.php
(34-63 = tempête ; 64-82 = 1 ; 83-95 = 2 ; 96-112 = 3 ; 113-136 = 4 ;
137 et plus = 5). On n'a pas inventé d'autre échelle.

Le fichier Pacifique HURDAT2 existe. On ne l'a pas compté. Ici c'est
l'Atlantique, comme les trois cibles Tier 1.

## Combien d'années et de tempêtes (HURDAT2)

**2004 systèmes**, de **1851 à 2025**. **175 années** d'affilée.
**Zéro année vide**. **Zéro erreur de lecture**.

Parmi ces 2004 :

| Quoi (tel que publié) | Nombre |
|---|---:|
| Au moins tempête nommée (TS, SS ou HU) | 1773 |
| Ouragan (statut HU) | 978 |
| Majeur (vent à 96 nœuds ou plus) | 342 |
| Au moins un drapeau L (centre sur une côte) | 732 |
| Points L | 1175 |
| Landfall L encore ouragan (HU) | 376 |
| Landfall L encore majeur | 131 |

Pic de vent, même table officielle :

| Pic | Systèmes |
|---|---:|
| Dépression (TD) | 228 |
| Tempête (TS) | 777 |
| Catégorie 1 | 398 |
| Catégorie 2 | 259 |
| Catégorie 3 | 164 |
| Catégorie 4 | 133 |
| Catégorie 5 | 45 |

Vent le plus fort du fichier : 165 nœuds. Aucun vent de pic manquant.

Les trois cibles, en compte seulement (pas un produit, pas un prix) :

- **Ouragan formation** : 978 systèmes ont eu le statut HU.
- **Ouragan intensité** : le tableau des pics ci-dessus.
- **Ouragan landfall** : 376 ouragans ont un drapeau L encore en HU.

Sur 175 saisons, comptes déjà écrits dans le scaffolding Phase B
(seuil seulement, pas un contrat) :

- 13 saisons avec 18 tempêtes nommées ou plus
- 21 saisons avec une énergie ACE à 159 ou plus
- 139 saisons avec au moins un landfall HU (drapeau L)
- 89 saisons avec au moins un landfall majeur (drapeau L)

## Le trou du drapeau L (on le dit tel quel)

L veut dire : le centre a croisé une côte. Ce n'est pas « États-Unis
seulement ».

Le PDF de format NHC dit aussi que les landfalls des États-Unis
continentaux sont marqués de 1851 à 1970 et depuis 1991. Les landfalls
hors États-Unis seulement de 1951 à 1970 et depuis 1991. Entre 1971 et
1990, le drapeau L est donc incomplet. On ne redessine pas la carte.
On ne sépare pas « US » et « ailleurs ».

## IBTrACS, pour croiser

Même bassin. **2299** lignes-systèmes dans le fichier. On a retiré
**26** tracks « spur » (consigne NCEI : ne pas les compter comme une
tempête). Restent **2273**.

Années : **1851 à 2026**, aucune saison vide dans l'intervalle.
**5** systèmes de 2026 sont encore provisoires (Arthur, Bertha,
Cristobal, Dolly, Edouard). HURDAT2 officiel s'arrête à 2025. C'est
le trou de 2026.

| Quoi (colonnes publiées) | Nombre |
|---|---:|
| Nommés (USA_STATUS TS / SS / HU / HR) | 1774 |
| Ouragan (USA_STATUS HU / HR) | 977 |
| Catégorie 1 ou plus (USA_SSHS) | 977 |
| Majeur (USA_SSHS 3 ou plus, ou vent 96 nœuds) | 343 |
| LANDFALL = 0 (masque terres NCEI) | 1242 |
| USA_RECORD L (même drapeau que HURDAT2) | 731 |

LANDFALL = 0 compte plus que le drapeau L : le masque NCEI prend
toutes les terres et les îles de plus de 1400 km². Ce n'est pas la
même chose. On garde les deux chiffres. On n'en choisit pas un.

Identifiants ATCF (le nom technique de la tempête, par exemple
AL092021) :

- 1998 IDs identiques des deux côtés
- 6 IDs HURDAT2 absents d'IBTrACS
- 13 IDs IBTrACS absents de HURDAT2
- 262 systèmes IBTrACS sans ID (souvent très anciens)

On n'a pas inventé les IDs manquants.

## Verdicts (noms du catalogue, non renommés)

| Nom | Verdict |
|---|---|
| HURDAT2 / IBTrACS | testée, ça aide |
| Ouragan formation | cible Tier 1 (pas encore testée) |
| Ouragan intensité | cible Tier 1 (pas encore testée) |
| Ouragan landfall | cible Tier 1 (pas encore testée) |
| NHC a-decks / b-decks | pas encore testée |
| Marché ouragan Kalshi | pas encore testée |
| Sécheresse Méditerranée | cible Tier 1 (pas encore testée) |
| Sécheresse Inde | cible Tier 1 (pas encore testée) |

HURDAT2 / IBTrACS aide : on a enfin le vrai compte, année par année,
depuis 1851, sans trou et sans chiffre inventé. Les trois cibles
ouragan restent « pas encore testées » : on a la vérité, pas encore
une prévision notée.

## Décision

On ne change pas le modèle Kalshi en ligne.

Pourquoi : ce n'est pas un test Kalshi. C'est la vérité ouragan
Phase 2. La gate (BSS > 0,05) demande une prévision. On ne l'a pas
notée ici.

Ensuite, si on veut la gate : archives NHC a-decks / b-decks
(prévision contre ce best-track). Pas avant. Pas Méditerranée.
Pas Inde.

## Comment relancer

Dans le dossier `predictor`, avec internet la première fois :

```
python scripts/eval_hurdat2_ibtracs.py
```

Les fichiers bruts restent locaux. Les comptes sont dans
`data/truth/hurdat2/`.

Pas de changement du texte du site. Pas de trading réel.
