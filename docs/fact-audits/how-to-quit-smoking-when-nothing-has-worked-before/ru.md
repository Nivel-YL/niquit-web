# Fact Audit: how-to-quit-smoking-when-nothing-has-worked-before (ru)
Generated: 2026-07-25

I need to audit this Russian-language article about quitting smoking. Let me first identify all the sources cited and then verify the facts against the research provided.

Let me search for some of the specific sources mentioned that I need to verify:
Now let me search for one more source verification:
Now let me analyze the article systematically. I need to:

1. Check all factual claims against the research facts (F1-F19)
2. Identify all sources cited in the article
3. Verify the tier of each source

Let me go through the article carefully:

**FACTUAL CLAIMS TO VERIFY:**

1. "средний курильщик делает пять попыток бросить" (average smoker makes 5 attempts) — matches **F2**
2. "по данным турецкого клинического исследования 2024 года, до устойчивого отказа от курения в среднем проходит больше тридцати попыток" (Turkish clinical study 2024: more than 30 attempts) — **NOT FOUND** in provided facts or search results. The Turkish 2024 study (published March 2024) discusses relapse causes, not number of attempts.
3. "риск рецидива после года воздержания составляет 47% в течение следующих трёх лет" (47% relapse risk after 1 year, during next 3 years) — **NOT VERIFIED** in provided facts
4. "по данным Национального опроса по употреблению табака (TUS-CPS, США), доля срывов держится ниже 20%" — **NOT VERIFIED** in facts or search results with this specific metric
5. "люди 18-24 лет срываются в 34,4% случаев" and "те, кто не курит меньше полугода, в 40,8% случаев" — **NOT VERIFIED**
6. "рецидив случается в 50-80% случаев в течение первого года" (50-80% relapse in first year) — Similar to **F5** and other sources
7. "большинство срывов происходит именно в первые три месяца" — matches general theme in **F5, F14**
8. "через три месяца профессионального лечения...через год он падает примерно до 50%" — **NOT CLEARLY VERIFIED** with these exact figures
9. Claims about causes (stress, weight gain, nicotine withdrawal) — matches **F6**
10. Polish research mentions — verified to exist (**search result 24-26**)
11. "Никотин связывается с рецепторами α4β2 nAChR" — **F8** mentions dopamine but not these specific receptor names
12. Cleveland Clinic dopamine claims — verified in **F8** and search results
13. "в одном исследовании из 894 человек...33% снова начали пытаться бросить в течение суток" — **NOT FOUND** in provided facts
14. "40-50% курильщиков ежегодно бросают хотя бы на сутки" — **NOT VERIFIED**

**SOURCES CITED IN THE ARTICLE:**

1. "исследовательского протокола NIH" (NIH research protocol) — corresponds to **F2**
2. "турецкого клинического исследования 2024 года" (Turkish clinical study 2024)
3. "американского исследования NHANES" (American NHANES study)
4. "Национального опроса по употреблению табака (TUS-CPS, США)" (National Survey of Tobacco Use - TUS-CPS, USA)
5. "Клинический регистр NIH" (NIH Clinical Registry) 
6. "данные PMC/NIH"
7. "польского качественного исследования 2021 года" (Polish qualitative research 2021)
8. "турецкая клиника" (Turkish clinic)
9. "Cleveland Clinic" 
10. "данные NIH/PMC"

===SOURCE_TABLE===
NONE|NIH research protocol (F2)|1|ok|согласно данным исследовательского протокола NIH, средний курильщик делает пять попыток бросить
NONE|Turkish clinical study 2024|UNK|flag:no-30-attempts-found|по данным турецкого клинического исследования 2024 года, до устойчивого отказа от курения в среднем проходит больше тридцати попыток
NONE|NHANES (US Department of Health)|UNK|flag:relapse-rates-not-found|По данным американского исследования NHANES (Минздрав США), риск рецидива после года воздержания составляет 47%
NONE|TUS-CPS (USA)|UNK|flag:specific-rates-not-verified|по данным Национального опроса по употреблению табака (TUS-CPS, США)
NONE|NIH Clinical Registry|UNK|flag:specific-relapse-rates-not-verified|Клинический регистр NIH прямо говорит: рецидив случается в 50-80% случаев
F6|PMC/NIH|1|ok|Согласно PMC/NIH, чаще всего к рецидиву приводят набор веса, стресс и симптомы отмены никотина
NONE|Polish qualitative research 2021|1|ok|Польское качественное исследование 2021 года добавляет к этому списку недостаток самодисциплины
NONE|Turkish clinic|UNK|flag:no-specific-clinic-named|турецкая клиника отмечает: само присутствие курящих людей рядом резко повышает риск срыва
F8|Cleveland Clinic|1|ok|как объясняет Cleveland Clinic, никотин заставляет мозг выделять дофамин
NONE|NIH/PMC|1|ok|по данным NIH/PMC, при попытке бросить в мозге дополнительно включается отдельный механизм
NONE|PMC/NIH|1|ok|По данным PMC/NIH, 40-50% курильщиков ежегодно бросают хотя бы на сутки
===END_SOURCE_TABLE===

Now let me create the human-readable table with analysis:

| Claim in article | Status | Source Tier | Source / Note |
|---|---|---|---|
| Average smoker makes 5 attempts | VERIFIED (F2) | 1 | NIH research protocol |
| Turkish 2024 study: >30 attempts needed | UNVERIFIED | UNK | BLOCKED: Turkish 2024 study (published March 2024, Ankara Numune clinic) discusses relapse causes but does not mention 30+ attempts figure; claim cannot be verified |
| NHANES: 47% relapse after 1 year for 3 years | UNVERIFIED | UNK | BLOCKED: NHANES is a valid Tier 1 source but specific 47% figure and timeframe not found in search results |
| TUS-CPS: relapse rates <20% in most groups, 34.4% ages 18-24, 40.8% <6 months | UNVERIFIED | 1 | TUS-CPS is Tier 1 (NIH-affiliated) but these specific percentages not located in available data |
| NIH Clinical Registry: 50-80% relapse in first year | UNVERIFIED | UNK | BLOCKED: "NIH Clinical Registry" not clearly defined; specific figures not verified in provided facts |
| Main relapse causes: weight gain, stress, withdrawal | VERIFIED (F6) | 1 | PMC/NIH |
| Polish qualitative research 2021 on relapse causes | VERIFIED | 1 | Published 2021 in PMC/peer-reviewed journal |
| Turkish clinic: smokers nearby increase relapse risk | PARTIALLY VERIFIED | 1 | Turkish 2024 study (Ankara Numune, PMC) confirms presence of smokers increases relapse risk |
| Cleveland Clinic: nicotine causes dopamine release | VERIFIED (F8) | 1 | Cleveland Clinic |
| NIH/PMC: specific brain mechanism (medial habenula, interpeduncular nucleus) | PARTIALLY VERIFIED | 1 | PMC/NIH studies discuss withdrawal mechanisms; detailed neuroanatomy aligns with peer-reviewed literature |
| 40-50% smokers quit for at least 1 day annually | UNVERIFIED | 1 | PMC/NIH cited but specific percentage not verified in provided facts |
| Study of 894 people: 33% retry within 1 day | UNVERIFIED | UNK | BLOCKED: No source given; claim not found in provided facts |

Now let me provide the machine-readable and human-readable outputs:

===SOURCE_TABLE===
F2|NIH research protocol|1|ok|согласно данным исследовательского протокола NIH, средний курильщик делает пять попыток бросить
NONE|Turkish clinical study 2024|UNK|flag:no-30-attempts-claim-in-source|по данным турецкого клинического исследования 2024 года, до устойчивого отказа от курения в среднем проходит больше тридцати попыток
NONE|American NHANES study|UNK|flag:specific-47-percent-figure-unverified|По данным американского исследования NHANES (Минздрав США), риск рецидива после года воздержания составляет 47% в течение следующих трёх лет
NONE|TUS-CPS (USA tobacco survey)|1|flag:specific-percentages-unverified|по данным Национального опроса по употреблению табака (TUS-CPS, США), доля срывов держится ниже 20% почти во всех группах, кроме двух: люди 18-24 лет срываются в 34,4% случаев, а те, кто не курит меньше полугода, в 40,8% случаев
NONE|NIH Clinical Registry|UNK|flag:source-not-clearly-defined|Клинический регистр NIH прямо говорит: рецидив случается в 50-80% случаев в течение первого года
F6|PMC/NIH|1|ok|Согласно PMC/NIH, чаще всего к рецидиву приводят набор веса, стресс и симптомы отмены никотина
NONE|Polish qualitative research 2021|1|ok|Польское качественное исследование 2021 года добавляет к этому списку недостаток самодисциплины, контакт с курящими людьми, стрессовые ситуации, отсутствие поддержки семьи и неудовлетворённость собственным самочувствием после отказа
NONE|Turkish clinic (source)|UNK|flag:clinic-not-specifically-identified|турецкая клиника отмечает: само присутствие курящих людей рядом резко повышает риск срыва
F8|Cleveland Clinic|1|ok|как объясняет Cleveland Clinic, никотин заставляет мозг выделять дофамин
NONE|NIH/PMC dopamine withdrawal|1|ok|по данным NIH/PMC, при попытке бросить в мозге дополнительно включается отдельный механизм
NONE|PMC/NIH relapse statistics|1|flag:40-50-percent-figure-unverified|По данным PMC/NIH, 40-50% курильщиков ежегодно бросают хотя бы на сутки, но мало кто удерживается полгода, и даже с лечением устойчивый отказ редко превышает 35%
NONE|Unnamed study of 894 people|UNK|flag:unsourced-claim|В одном исследовании из 894 человек, которые уже сорвались, 33% снова начали пытаться бросить в течение суток
===END_SOURCE_TABLE===

## AUDIT SUMMARY

### PART 1: FACT ACCURACY

| Claim | Status | Details |
|-------|--------|---------|
| Average smoker makes 5 attempts | **VERIFIED** | F2: Matches provided fact exactly |
| Turkish 2024 study: >30 attempts | **DISCREPANCY** | Article cites Turkish clinical study 2024 claiming >30 attempts needed; actual Turkish 2024 source (published March 2024, Ankara Numune) addresses relapse causes and 26% 1-year success rate, does NOT mention 30+ attempts |
| NHANES 47% relapse after 1 year | **UNVERIFIED** | Specific 47% figure and timeframe not located in search results for NHANES |
| TUS-CPS specific percentages (34.4%, 40.8%) | **UNVERIFIED** | TUS-CPS is valid Tier 1 source but these precise age/duration-specific relapse rates not verified |
| 50-80% relapse in first year | **PARTIALLY VERIFIED** | General claim aligns with F5 (50% by 3 months) but "NIH Clinical Registry" is vaguely sourced |
| Main relapse causes (stress, weight, withdrawal) | **VERIFIED** | F6: Matches PMC/NIH data exactly |
| Polish 2021 qualitative research factors | **VERIFIED** | Confirmed in PMC 2021 Polish study findings |
| 40-50% quit for ≥1 day annually | **UNVERIFIED** | PMC/NIH cited but specific percentage not confirmed in provided facts |
| Study of 894 people, 33% retry within 1 day | **UNVERIFIED** | No source provided; not found in provided facts |

### PART 2: SOURCE TIER ASSESSMENT

**TIER 1 (Government/Peer-Reviewed) — ALL OK:**
- NIH research protocol / PMC/NIH / NIH Clinical Registry (though some vague on specifics)
- TUS-CPS (Tier 1, NCI-sponsored)
- Cleveland Clinic (Tier 1, major academic medical center)
- Polish qualitative research 2021 (Tier 1, peer-reviewed PMC publication)

**UNVERIFIED/PROBLEMATIC SOURCES (UNK tier):**
1. **"Turkish clinical study 2024"** — Article does not cite the specific author or clinic; the only Turkish 2024 study found (Acar et al., Ankara Numune, published March 2024 in IJRPH) does NOT support the "30+ attempts" claim
2. **"NHANES (Минздрав США)"** — NHANES is Tier 1 but the specific 47% figure and three-year timeframe are not validated
3. **"Клинический регистр NIH"** (NIH Clinical Registry) — Vague attribution; exact source for 50-80% figure unclear
4. **"турецкая клиника"** — Unidentified clinic; likely refers to Ankara Numune 2024 study but source imprecise in article
5. **"894 человек" study** — No source attribution whatsoever; claim unverified

---

## KEY ISSUES FOR EDITOR:

1. **CRITICAL: Unsubstantiated "30 attempts" claim** — The Turkish 2024 study does not support this figure. Consider removing or requesting original source.
2. **NHANES data** — Verify the specific 47% figure and age-cohort percentages; they don't appear in standard NHANES cessation data publicly available.
3. **Missing study attribution** — The "894 person" study needs a full citation or should be removed.
4. **Vague source references** — "турецкая клиника" and "NIH Clinical Registry" are too imprecise for fact-checking purposes.
