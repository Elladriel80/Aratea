# Fenêtre d'hiver et Degré entier

**Date :** 12 septembre 2026
**Pour :** le propriétaire (pas un document technique)

Deux règles de paiement n'étaient pas encore chiffrées le 12 septembre.
Cette note dit seulement ce qui a été compté sur des lectures déjà là.
Le site public n'a pas été changé. Le modèle en ligne n'a pas été changé.
Aucun pari avec de l'argent réel. Aucun chiffre n'a été inventé.

On n'a pas relancé les autres essais du 12 septembre (NBM, membres GEFS,
thermomètre du jour, siècle, densités, NBM + correction ville).

## Les deux noms (stables)

**Fenêtre d'hiver.** La journée officielle va de minuit à minuit en heure
locale d'hiver, toute l'année, même en été. Ce n'est pas l'heure affichée
à la pendule quand l'heure d'été est en vigueur.

**Degré entier.** Le chiffre qui paie est un degré entier, pas un
demi-degré.

## Ce qu'on a trouvé dans le code avant de compter

Kalshi paie le rapport officiel de la station (CLI), par exemple Midway,
Hobby, DFW.

Le dossier sait déjà fabriquer le jour en heure d'hiver
(`lst_window.py`, minuit à minuit en heure standard locale).
La mesure A utilise `lst_date` de ce fichier. Les essais récents
(vérité station, membres d'ensemble, thermomètre du jour) passent
par là.

Hypothèse, pas une mesure : le mélange en ligne demande encore à
Open-Meteo le max et le min du jour calendaire dans le fuseau de la
ville. Ce fuseau avance d'une heure en été. Ce n'est peut-être pas la
même fenêtre de 24 heures que le rapport officiel.

L'arrondi entier half-up du NWS est déjà dans `resolution.py`
(75,5 devient 76 ; 76,5 devient 77, pas 76). `synthetic_bins.py` et
le mélange en ligne élargissent déjà chaque case de plus ou moins
0,5 degré (lo-0,5 ≤ x < hi+0,5). La mesure B compte combien de fois
cet élargissement change l'appartenance à la case, sur les mêmes
extrêmes horaires.

## Comment on a compté

**Fenêtre d'hiver.** Mêmes lectures horaires de la station (archive IEM
ASOS / METAR, fichier déjà dans le dépôt, 1er mai au 12 septembre 2026,
18 villes). Pour chaque jour :

- A : max et min sur le jour de la pendule (heure d'été si elle est
  en vigueur)
- B : max et min sur le jour officiel (heure d'hiver, décalage fixe)

Un jour n'est gardé que s'il a au moins 18 lectures dans les deux
fenêtres. Une heure absente reste absente.

Contrôle : Phoenix n'a pas d'heure d'été. Les deux fenêtres doivent
être les mêmes.

Complément, pas un changement de valeur : les heures imprimées du
rapport officiel (2020 à 2026). On compte seulement si le max ou le min
officiel est tombé entre minuit et 1 h du matin un jour d'heure d'été.
Ce n'est pas la preuve que le chiffre du jour change (il peut y avoir
égalité avec une autre heure).

**Degré entier.** On compare une valeur continue (ou un demi-degré) à
l'entier NWS, puis on regarde si la case de 2 degrés change.

Deux sources, clairement séparées :

1. Les mêmes METAR horaires. Presque tous sont déjà des entiers.
2. GHCN-Daily (NCEI, 18 fichiers officiels). Le max et le min y sont
   en dixièmes de °C. On convertit en °F sans arrondir d'abord.
   Hypothèse : pour ces stations américaines, le dixième de °C vient
   souvent d'un °F déjà entier. La partie après la virgule peut être
   un effet d'unité, pas un vrai demi-degré du capteur.

On n'a pas l'archive minute par minute dans le dépôt. Pour voir un
vrai arrondi capteur, il faudrait l'ASOS 1 minute IEM / NCEI.

## Fenêtre d'hiver : résultat

18 villes. 2314 jours comparables. 1er mai au 11 septembre 2026.

| Ensemble | Jours | Max différent | Min différent | Case de 2° différente |
|---|---|---|---|---|
| Tous | 2314 | 18 (0,78 %) | 185 (8,0 %) | 129 (5,6 %) |
| Avec heure d'été | 2188 | 18 | 185 | 129 |
| Sans heure d'été | 126 | 0 | 0 | 0 |

Les 126 jours sans heure d'été sont Phoenix (pas d'heure d'été).
Zéro différence. Le contrôle est bon.

Quand le chiffre change, l'entier officiel change aussi (18 et 185).
La case de 2 degrés change moins souvent : 9 jours pour le max
(0,39 %), 122 jours pour le min (5,3 %).

Parmi ces écarts, l'extrême du jour LST tombe à 00:xx heure d'été
(l'heure qui reste à la veille officielle) pour **1 max sur 18**
et **167 min sur 185**. Le reste vient de l'autre bord : la pendule
prend l'heure 00:xx du jour, qui appartient encore à la veille en
heure d'hiver. Compte revérifié avec `lst_date` du fichier
`lst_window.py`.

Villes les plus touchées (jours où le max ou le min change) :

| Ville | Jours | Max | Min | Case de 2° |
|---|---|---|---|---|
| Chicago | 130 | 4 | 19 | 13 |
| Philadelphie | 130 | 1 | 16 | 10 |
| Washington | 130 | 2 | 16 | 12 |
| New York | 130 | 4 | 12 | 10 |
| Seattle | 126 | 0 | 15 | 10 |
| Boston | 129 | 1 | 14 | 10 |
| Phoenix | 126 | 0 | 0 | 0 |

Chicago est la plus touchée : 22 jours sur 130 (surtout le min).
Phoenix : 0 jour sur 126.

En clair : se tromper d'heure change surtout le **minimum** du jour
(environ 8 jours sur 100). Le maximum bouge rarement (moins de 1 jour
sur 100). Sur les contrats de 2 degrés, environ 6 jours sur 100
tombent dans la mauvaise case, presque toujours à cause du min.

### Heures imprimées du rapport officiel (complément)

44 005 jours, 1er janvier 2020 au 12 septembre 2026. 525 heures de max
illisibles, 507 heures de min illisibles. On ne les a pas inventées.

| | Heures lisibles | Dont 00:xx en heure d'été |
|---|---|---|
| Max | 43480 | 366 (0,84 %) |
| Min | 43498 | 431 (0,99 %) |

Phoenix : 0 et 0. Midway a le plus de max à 00:xx en heure d'été
(53 jours). Boston et Denver ont le plus de min à 00:xx (52 chacun).
Ce tableau ne compte pas les valeurs qui changent. Le tableau ASOS
ci-dessus le fait.

## Degré entier : résultat

### Lectures horaires déjà dans le dépôt

56 302 lectures, 18 villes, 1er mai au 12 septembre 2026.

| | Compte |
|---|---|
| Lectures déjà un entier | 56258 / 56302 |
| Lectures avec un dixième | 44 / 56302 (0,08 %) |
| Jours assez couverts | 2314 |
| Jours dont le max ou le min n'est pas entier | 3 |
| Extrêmes du jour (max et min) | 4628 |
| Déjà un entier | 4625 |
| Exactement un demi-degré (x,5) | 0 |
| Entier NWS différent de la partie entière | 1 |
| Case de 2° différente (entier vs partie entière) | 0 |
| La case payée ne contient pas x sans ±0,5 °F | 0 / 4628 |
| ±0,5 °F (comme synthetic_bins) change l'appartenance | 0 / 4628 |

Les 3 jours dont l'extrême a un dixième : Denver 13 juillet 2026
(min 64,4), Chicago 25 août 2026 (min 62,6), Phoenix 11 août 2026
(min 82,4). Un seul de ces trois change l'entier (62,6 devient 63).
Aucun ne change la case de 2 degrés. L'élargissement ±0,5 °F de
`synthetic_bins.py` ne déplace aucun de ces 4628 extrêmes.

Les 44 dixièmes ressemblent surtout à une conversion depuis des °C
entiers (64,4 ; 62,6 ; 82,4). Une seule lecture à 68,5, et ce n'était
pas le max ni le min du jour.

### Fichier quotidien GHCN (dixième de °C vers °F)

18 stations. 1 059 816 max ou min, 1869 à 2026. Source :
ncei.noaa.gov, fichiers `.dly` déjà utilisés pour le siècle.

Hypothèse rappelée : ce n'est pas un capteur au demi-degré. C'est
souvent un °F entier stocké en dixième de °C.

| | Compte |
|---|---|
| Valeurs | 1059816 |
| Déjà un entier °F | 116797 (11,0 %) |
| Exactement x,5 | 0 |
| Entier NWS ≠ partie entière (tronquer) | 465194 (43,9 %) |
| Case de 2° différente si on tronque | 246576 (23,3 %) |
| Entier NWS ≠ arrondi Python | 0 |
| Case de 2° différente si on passe par le demi-degré | 0 |
| ±0,5 °F (synthetic_bins) change l'appartenance | 495748 (46,8 %) |

En clair : dans GHCN, on ne voit **aucun** vrai x,5. Si on oublie
l'arrondi NWS et qu'on tronque après la conversion °C → °F, on se
trompe de case 23 jours sur 100. L'élargissement ±0,5 °F replace
46,8 % de ces conversions dans la case de l'entier officiel. Ce
sont des restes d'unité, pas des demi-degrés capteur. Le code
siècle fait déjà le bon arrondi.

## Verdict

**Fenêtre d'hiver : oui, ça compte, surtout pour le min.**

Se tromper d'heure (pendule d'été au lieu de l'heure d'hiver) a
changé le min 185 jours sur 2314, et la case de 2 degrés 129 jours
sur 2314. Le max presque jamais. Chicago est la plus exposée.
Phoenix (pas d'heure d'été) reste à zéro. Le code qui fabrique la
vérité station est déjà du bon côté. On ne change pas le mélange
en ligne dans cette étape. Si un chemin de prévision prend encore
le jour d'Open-Meteo en heure murale, c'est là que l'écart peut
entrer. Ce n'est pas mesuré sur les prévisions ici, seulement sur
les lectures.

**Degré entier : sur les lectures du dépôt, presque jamais.**

Le rapport officiel imprime déjà un entier. Les METAR horaires aussi,
sauf 44 lectures sur 56 302. Sur 4628 extrêmes du jour, la case de
2 degrés n'a jamais changé. On n'a pas vu de vrai demi-degré officiel
quotidien. Pour mesurer l'arrondi du capteur avant publication, il
manque l'ASOS 1 minute.

Ce qui compte pour le modèle : ne pas tronquer une conversion °C → °F
(GHCN, 23 % de mauvaises cases), et garder l'arrondi entier NWS sur
les prévisions continues. Ça, le code le fait déjà. Ce n'est pas une
raison de changer le champion.

## Comment relancer le script

Dans le dossier `predictor` :

```
python scripts/eval_settlement_window_rounding.py --skip-fetch
```

Sans `--skip-fetch`, le script peut retélécharger GHCN (NCEI) si le
cache local manque. Il ne retélécharge pas l'ASOS si
`data/asos/extracted.json` est déjà là.

Le script écrit :

- `data/truth/settlement/settlement_ab.json` : les comptes
- `data/truth/settlement/settlement_ab.md` : le même tableau, côté machine

## Ce que cette étape ne fait pas

Le modèle en ligne n'est pas changé.
Pas de changement du texte du site.
Pas de trading réel.
Pas de nouvel essai NBM, GEFS, thermomètre du jour, siècle, densités,
ni NBM + correction ville.
Pas d'archive minute par minute : l'arrondi capteur avant le rapport
officiel n'est donc pas mesuré.
