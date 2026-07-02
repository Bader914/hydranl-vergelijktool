# Diepgaande analyse van de drie voorbeeldberekeningen

Deze analyse hoort bij de berekeningen in `sample_data/` en legt uit welke
waarden opvallen, wat ze betekenen en waarom de verschillen ontstaan. Alle
getallen komen rechtstreeks uit de HydraNL-uitvoer (`uitvoer.html`) en -invoer
(`invoer.hyd`); de tool reproduceert ze automatisch op het tabblad **Analyse**.

> **Locatie:** `15-03_00148_1_HY_km0013.70` (Rijksdriehoek x=102.499, y=438.900),
> een oeverlocatie langs de **Hollandsche IJssel**, benedenstrooms beïnvloed door
> de **Hollandsche IJsselkering** en de **Europoortkering (Maeslantkering)**.
> Zichtjaar **2050**. Faalmechanisme: **golfoverslag en overloop**.
> Kruinhoogte dijk 6,00 m+NAP.

---

## 1. De drie berekeningen vormen een "wat-als"-reeks

De drie berekeningen verschillen niet willekeurig; ze zijn precies zo gekozen dat
je de effecten kunt ontrafelen:

| Berekening | Klimaat | Zeespiegel­stijging | Aftopdebiet | Kritiek overslagdebiet |
|---|---|---|---|---|
| **1_Shape_1** (referentie) | G (gematigd) | 0,05 m | 18.000 m³/s | 1 l/s/m |
| **Def v01_Shape_1** | **W (warm)** | **0,25 m** | 18.000 m³/s | 1 l/s/m |
| **1_Shape_10** | W (warm) | 0,25 m | **25.000 m³/s** | **10 l/s/m** |

- **`Def v01_Shape_1` − `1_Shape_1`** isoleert dus het **klimaateffect** (G→W,
  +0,20 m zeespiegel, W-afvoerstatistiek), want alle andere knoppen zijn gelijk.
- **`1_Shape_10` − `Def v01_Shape_1`** isoleert het effect van de **ontwerp-/
  statistiekkeuzes** (hoger aftopdebiet + 10× hoger toelaatbaar overslagdebiet)
  bovenop het W-klimaat.

Deze opzet maakt een schone decompositie mogelijk (§4).

---

## 2. Wat betekenen de gewijzigde waarden?

- **Klimaatscenario (3 = G, 4 = W).** Bepaalt de zwaarte van de statistiek. W
  (warm) betekent meer opwarming, een hogere zeespiegel en zwaardere
  rivierafvoeren. Dit is de "hoofdknop"; de andere wijzigingen zijn er deels een
  gevolg van.
- **Zeewaterstandstijging (0,05 → 0,25 m).** Een vaste opslag op de
  zeewaterstand. Omdat deze locatie via de Maasmond direct op zee "voelt", werkt
  elke centimeter zeespiegel bijna één-op-één door in de belasting. **Verhoogt
  het HBN.**
- **Afvoerstatistiek Q (G_2050 → W_2050).** Het bestand met
  overschrijdingskansen van de piekafvoer bij Lobith. De W-variant bevat
  zwaardere afvoeren. **Verhoogt het HBN — maar alleen als afvoer de belasting
  bepaalt** (zie §5: dat is hier nauwelijks het geval).
- **Aftopdebiet (18.000 → 25.000 m³/s).** De afvoer waarboven hogere afvoeren
  niet zwaarder meetellen (omdat de Rijn bovenstrooms overstroomt). 18.000 is de
  klassieke aftopping; 25.000 laat veel zwaardere afvoeren toe. **Verhoogt het
  HBN bij afvoergedreven locaties.**
- **Kritiek overslagdebiet (0,001 → 0,01 m³/s/m = 1 → 10 l/s/m).** Hoeveel
  golfoverslag je toelaatbaar acht. Meer toegestane overslag betekent een **lager**
  benodigd belastingniveau. Deze factor 10 is de grootste enkele knop in de reeks
  en **verlaagt het HBN fors.**

---

## 3. De HBN-resultaten (m+NAP)

Het Hydraulisch Belastingniveau per overschrijdingsfrequentie:

| Frequentie | 1_Shape_1 | Def v01_Shape_1 | 1_Shape_10 |
|---|---|---|---|
| 1/3.000 | 3,295 | 3,347 | 3,142 |
| 1/10.000 | 3,439 | 3,478 | 3,260 |
| 1/25.000 | 3,537 | 3,569 | 3,341 |
| 1/30.000 | 3,556 | 3,587 | 3,357 |
| 1/83.333 | 3,658 | 3,687 | 3,446 |
| 1/100.000 | 3,676 | 3,706 | 3,463 |
| 1/250.000 | 3,768 | 3,809 | 3,556 |
| 1/833.333 | 3,918 | 4,023 | 3,762 |

Alle niveaus (3,1–4,0 m+NAP) liggen ruim onder de kruinhoogte van 6,0 m+NAP: er
is veel waking, wat past bij een overslag- (niet overloop-)gedreven toets.

---

## 4. Decompositie: waarom is het netto-effect verrassend?

Verschillen ten opzichte van de referentie `1_Shape_1`, in **centimeters**:

| Frequentie | Klimaat G→W<br>(Def − calc1) | Aftop + overslag<br>(calc10 − Def) | **Totaal**<br>(calc10 − calc1) |
|---|---:|---:|---:|
| 1/3.000 | +5,2 | −20,5 | **−15,3** |
| 1/10.000 | +3,9 | −21,8 | **−17,9** |
| 1/25.000 | +3,2 | −22,8 | **−19,6** |
| 1/30.000 | +3,1 | −23,0 | **−19,9** |
| 1/83.333 | +2,9 | −24,1 | **−21,2** |
| 1/100.000 | +3,0 | −24,3 | **−21,3** |
| 1/250.000 | +4,1 | −25,3 | **−21,2** |
| 1/833.333 | +10,5 | −26,1 | **−15,6** |

**Interpretatie:**

1. **Het klimaateffect is positief maar bescheiden: +3 tot +10 cm.** Het groeit
   naar de zeldzamere frequenties toe (van +5 cm bij 1/3.000 naar +10,5 cm bij
   1/833.333). Logisch: de zeespiegelstijging en zwaardere W-statistiek tellen
   zwaarder mee in de extremen.
2. **De ontwerp-/statistiekkeuzes verlagen het HBN met 20–26 cm.** Dit wordt
   gedreven door het **10× hogere toelaatbare overslagdebiet** (1 → 10 l/s/m).
   Het hogere aftopdebiet (18.000 → 25.000) werkt de andere kant op (verhogend),
   maar is hier klein omdat afvoer de belasting nauwelijks bepaalt (§5); netto
   overheerst de verlaging door de overslagnorm ruimschoots.
3. **Netto is `1_Shape_10` dus 15–21 cm LAGER dan de referentie**, ondanks het
   zwaardere klimaat. **De belangrijkste les:** een ogenschijnlijk "technische"
   keuze als het toelaatbare overslagdebiet weegt hier zwaarder dan de sprong van
   klimaatscenario G naar W. Wie twee berekeningen vergelijkt moet dus goed
   opletten *welke* knoppen tegelijk veranderden — anders trek je de verkeerde
   conclusie over "het klimaat".

---

## 5. Belastingmechanisme: dit is een storm-/zeegedreven locatie

Uit de illustratiepunten bij 1/3.000 (referentie `1_Shape_1`):

- **76% van de faalkans** komt uit de toestand **"Europoortkering open én
  Hollandsche IJsselkering open"**. De keringen staan dus meestal open op het
  maatgevende moment; de op één na grootste bijdrage (15%) is "beide gesloten
  met waterbezwaar".
- Binnen die dominante toestand komt de belasting vooral uit de
  **noordwestelijke windrichtingen**: WNW 31%, NW 21%, W 11%, NNW 11%.
- Het maatgevende ontwerppunt heeft een **hoge zeewaterstand (~2,9 m+NAP)**,
  **stevige wind (~18–25 m/s)** en een **bescheiden Rijnafvoer (~2.200–2.400
  m³/s)**. De afvoertak (q Rijn = 10.000 m³/s uit noordoostelijke richtingen)
  levert vrijwel **0%** bijdrage.

**Conclusie:** de belasting wordt bepaald door **noordwesterstormen die zeewater
opstuwen**, niet door hoogwater op de rivier. Dat verklaart §4 volledig:

- De **zeespiegelstijging** werkt daarom sterk door (klimaateffect positief).
- De **afvoerstatistiek (G→W)** en het **aftopdebiet** doen weinig, want afvoer
  is hier niet maatgevend — precies wat de kleine bijdrage van die knoppen laat
  zien.

Onder klimaat W verschuift het beeld nog verder naar de zee: het aandeel
"beide keringen open" stijgt van **76% → 80% → 94%** (calc1 → Def → calc10) en de
zeewaterstand in het ontwerppunt loopt op van **2,92 → 2,97 → 2,99 m+NAP**.

---

## 6. Overige opvallende (ongewijzigde) invoer

Deze staan in alle drie gelijk, maar zijn belangrijk voor de interpretatie:

- **Modelonzekerheid golfoverslag:** `MU = −0,09`, `SIGMA = 0,18` — de lognormale
  onzekerheid op de overslag. `STAT_ONZ = JA` en de `metOnzHeid`-statistiek­
  bestanden betekenen dat de statistische onzekerheid al in de basis zit; dit
  verzwaart vooral de kleine frequenties.
- **Keringbetrouwbaarheid:** `ALFA = 0,01`, `ALFA_HOIJK = 0,005` (niet-sluitkansen),
  `KANS_WATERBEZWAAR = 0,33`. Deze bepalen hoe vaak de "gesloten"-toestanden
  meetellen — hier samen ~19% van de faalkans.
- **`FACTOR_TP_TM = 1,1`:** omrekening van piek- naar spectrale golfperiode; direct
  van invloed op de berekende overslag.
- **Rekenroosters** (`QMIN/QMAX/QSTAP`, `MMIN/MMAX/MSTAP`, `UMAX`): rekentechnisch,
  geen fysische invloed zolang ze ruim genoeg zijn.
- **Reparaties:** de log meldt 1.071 + 116 correcties in de belastingmatrix waar de
  waterstand niet-fysisch afnam bij toenemende afvoer/zeewaterstand
  (`REPAREER_Q/M = JA`). Dit is normaal en duidt niet op een fout.

---

## 7. Samengevat

- Deze locatie is **storm- en zeewaterstand-gedreven** (NW-wind, open keringen),
  niet afvoergedreven.
- **Klimaat G→W verhoogt** het HBN met **+3 tot +10 cm**, sterker in de extremen.
- Het **10× hogere toelaatbare overslagdebiet verlaagt** het HBN met **~20–26 cm**
  en domineert het netto-resultaat.
- **Netto is `1_Shape_10` 15–21 cm lager** dan de referentie — een goed voorbeeld
  waarom je bij het vergelijken van berekeningen altijd moet nagaan *welke*
  parameters samen veranderden voordat je een effect aan "het klimaat" toeschrijft.
