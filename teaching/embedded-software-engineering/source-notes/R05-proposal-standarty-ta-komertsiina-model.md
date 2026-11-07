---
title: "Лекція 05 — Proposal, стандарти та комерційна модель"
date: 2026-09-16
session: 05
source_transcript: ../source-transcripts/2026-09-16.md
status: frozen
frozen_at: 2026-09-28
revision_policy: "Після реконструкції 2026-09-28 цей матеріал не переписується; наступні лекції лише додаються."
---

# Лекція 05. Proposal, стандарти та комерційна модель

> **Хронологія:** 16.09.2026 · п'яте заняття.  
> **Первинне джерело:** [повний транскрипт](../source-transcripts/2026-09-16.md).  
> **Фокус:** перетворити pre-sale vision у контрольований набір engineering assumptions, нормативних reference documents, ресурсів і commercial risk.

## 1. Де ми знаходимося в lifecycle

На початку заняття відновлюється послідовність, яку курс використовує як навчальну модель:

```text
Lead
 ↓
RFI
 ↓
RFC (Request for Clarification — course terminology)
 ↓
Proposal
 ↘
  RFQ / commercial estimate
```

У реальному procurement порядок може відрізнятися, частина артефактів може йти паралельно або мати інші назви. Тут важлива не бюрократична послідовність, а логіка: **спочатку зрозуміти задачу, потім сформулювати спосіб рішення, потім чесно порахувати ресурси й ризики.**

## 2. Чому embedded Proposal швидко впирається у standards

Для систем, що взаємодіють з фізичним світом, client expectation часто включає не тільки функції, а й:

- safety;
- security;
- EMC/electrical/mechanical constraints;
- quality process;
- traceability;
- production/market requirements;
- verification evidence.

Тому Proposal має містити **reference basis**: які нормативні, process та engineering documents впливають на рішення.

## 3. Три рівні орієнтирів: framework → standard → guideline/practice

Лекція пропонує корисну навчальну ієрархію:

```text
PROCESS / ASSESSMENT FRAMEWORK
            ↓
        STANDARDS
            ↓
 GUIDELINES / RULE SETS / PRACTICES
            ↓
     PROJECT IMPLEMENTATION
```

Її не треба сприймати як юридичну універсальну піраміду: конкретні документи можуть мати інший статус. Але як спосіб мислення вона корисна.

### Framework / process model

Відповідає переважно на питання **«які процеси мають існувати і як оцінювати їхню спроможність?»**

Приклад: Automotive SPICE.

### Standard

Фіксує вимоги, принципи, work products або criteria для конкретної області.

### Guideline / coding/design rule set

Допомагає перевести high-level requirement у конкретні engineering rules. Приклади можуть включати MISRA C/C++, MAAB style guidelines або внутрішні project rules — але їх застосовність завжди треба обґрунтувати.

## 4. Редакторське уточнення — Automotive SPICE capability levels

У транскрипті прозвучала модель із сімома рівнями. Для **Automotive SPICE PAM 4.0 capability scale — Level 0...Level 5**:

| Level | Назва |
|---|---|
| 0 | Incomplete |
| 1 | Performed |
| 2 | Managed |
| 3 | Established |
| 4 | Predictable |
| 5 | Innovating |

Офіційний VDA QMC PAM 4.0: <https://vda-qmc.de/wp-content/uploads/2023/12/Automotive-SPICE-PAM-v40.pdf>

Також важливо: Automotive SPICE — **process assessment model**, а не сертифікат, що автоматично «дозволяє робити системи певного класу складності».

## 5. Редакторське уточнення — standards і CE

Усна лекція занадто сильно ототожнила стандарти із законом та CE із «сертифікацією по ISO».

Для ЄС коректніше мислити так:

```text
applicable EU legislation = mandatory legal requirements
             ↓
harmonised standards = usually voluntary route to presumption of conformity
             ↓
conformity assessment + technical documentation + declaration
             ↓
CE marking, якщо його вимагає застосовне законодавство
```

Тобто:

- standards у Європі загалом є добровільними technical specifications, якщо закон не робить конкретне посилання обов'язковим;
- harmonised standards часто дають **presumption of conformity**, але альтернативне технічне рішення може бути допустимим;
- CE marking — не універсальний «сертифікат якості» і не завжди видається third party;
- спочатку треба визначити **яке саме legislation applies to the product**.

Офіційні джерела ЄС:

- <https://europa.eu/youreurope/business/product-rules-compliance/general-product-compliance/standards-in-europe/index_en.htm>
- <https://europa.eu/youreurope/business/product-rules-compliance/general-product-compliance/conformity-assessment/index_en.htm>
- <https://europa.eu/youreurope/business/product-rules-compliance/general-product-compliance/ce-marking/index_en.htm>

## 6. Functional safety classification: не змішувати стандарти й домени

У лекції знову з'являється HARA/ASIL як приклад того, як risk classification впливає на engineering rigor.

### Редакторське уточнення

Для ISO 26262 автомобільний ASIL визначається через **Severity, Exposure, Controllability**. QM та ASIL A–D не слід переносити як універсальну шкалу на всі індустрії.

ISO 26262-3: <https://www.iso.org/standard/68385.html>

Також конкретні правила на кшталт «заборонити dynamic memory» або «залишити 70% вільної пам'яті» можуть бути project/domain guideline, але їх не варто подавати як універсальну пряму вимогу ISO 26262 без конкретного reference.

## 7. Proposal має показати architecture, implementation і V&V

Клієнт повинен бачити не тільки **що** ми зробимо, а й **як ми доведемо**, що результат відповідає потребі.

### Architecture

- high-level decomposition;
- major interfaces;
- external dependencies;
- key constraints;
- alternatives/trade-offs.

### Implementation

- technologies/tools;
- planned workstreams;
- build/manufacturing path;
- integration strategy;
- feasibility checks / PoC, якщо треба.

### Verification & Validation

- review/static analysis;
- unit tests;
- integration tests;
- bench/HIL/real-hardware tests;
- regression/performance tests;
- acceptance/validation evidence.

Не треба механічно вставляти всі види тестів у кожен Proposal. Набір V&V повинен випливати з product risk, requirements і applicable process/reference basis.

## 8. Resources — не лише люди

Embedded estimate складається щонайменше з чотирьох ресурсних шарів:

| Шар | Приклади |
|---|---|
| People | architect, firmware, hardware, mechanics, QA, safety/security, manager |
| Material | components, PCBs, mechanics, harnesses, fixtures |
| External services | fabrication, assembly, lab, certification/conformity work |
| Time/dependencies | lead time, shipping, customs, re-spins, waiting for samples |

Тому Gantt/critical path для embedded часто залежить від речей, які не прискорюються додаванням ще одного software engineer.

## 9. T&M та Fixed Price — що реально змінюється

Лекція порівнює дві базові commercial models.

### Time & Material

Клієнт оплачує фактичну залученість за погодженими rates і, за договором, матеріальні/зовнішні витрати. Модель добре працює при невизначеному scope, discovery, research, R&D, частих змінах.

### Fixed Price

Provider бере на себе зобов'язання виконати визначений scope за погоджену ціну/умови. Модель потребує значно чіткішого scope, acceptance criteria, assumptions і change-control.

### Редакторське уточнення — risk allocation

Не можна коректно казати, що «в T&M усі ризики лежать на клієнті», а «у Fixed Price всі — на vendor». **Розподіл юридичних, safety, IP, liability, warranty, schedule та commercial risks визначає contract.**

Простіше:

| Ризик | T&M | Fixed Price |
|---|---|---|
| Scope uncertainty | легше absorb через reprioritization | небезпечна без change request |
| Provider overrun effort | частіше оплачуваний, якщо робота погоджена | частіше б'є по margin provider-а |
| Budget predictability client-а | нижча | вища для зафіксованого scope |
| Need for clear acceptance criteria | важливо | критично |
| Legal/liability risk | залежить від договору | залежить від договору |

## 10. Коли Fixed Price має сенс

За логікою лекції, FP стає реалістичним, коли:

- problem/scope добре відомий;
- requirements достатньо стабільні;
- provider уже робив аналогічну роботу;
- acceptance criteria зрозумілі;
- dependencies і client obligations зафіксовані;
- change process існує;
- uncertainty включена у contingency/margin.

Якщо ці умови не виконані, T&M або phased model часто чесніша.

## 11. Estimate має бути traceable

Правильний estimate не починається з «мені здається, це три місяці». Він будується через decomposition.

```text
scope / assumptions
      ↓
workstreams / WBS
      ↓
roles + effort
      ↓
materials + external services
      ↓
dependencies / lead times
      ↓
risk / contingency
      ↓
commercial estimate
```

Кожна велика цифра повинна мати пояснення: звідки вона взялася і що її змінить.

## 12. Контрольні запитання

1. Навіщо Proposal reference basis?
2. Чим process assessment model відрізняється від product safety standard?
3. Які capability levels має Automotive SPICE 4.0?
4. Чому CE marking не треба називати просто «ISO certification»?
5. Що дає harmonised standard у ЄС?
6. Які три параметри лежать в основі automotive HARA/ASIL?
7. Чим T&M і Fixed Price відрізняються насамперед з commercial perspective?
8. Чому legal/liability risk не можна визначити лише з pricing model?
9. Які non-human resources треба врахувати в embedded estimate?
10. Що робить estimate traceable?

## 13. Схема заняття

```text
client need
   ↓
reference basis
   ├─ process/framework
   ├─ standards / legislation
   └─ guidelines / project rules
   ↓
architecture + implementation + V&V
   ↓
resources + timeline + risks
   ↓
T&M / FP / hybrid commercial model
   ↓
Proposal that can be negotiated
```

## 14. Місток до 22.09.2026

Після погодженого Proposal виникає наступний різкий перехід: **контакт має стати контрактом, а контракт — delivery team і requirements.** Наступне заняття починає шлях від signed agreement до staffing, product discovery, business analysis, user stories, system requirements і першої architecture visualization.

## Перевірені посилання

- Automotive SPICE PAM 4.0: <https://vda-qmc.de/wp-content/uploads/2023/12/Automotive-SPICE-PAM-v40.pdf>
- ISO 26262-3:2018: <https://www.iso.org/standard/68385.html>
- EU standards overview: <https://europa.eu/youreurope/business/product-rules-compliance/general-product-compliance/standards-in-europe/index_en.htm>
- EU conformity assessment: <https://europa.eu/youreurope/business/product-rules-compliance/general-product-compliance/conformity-assessment/index_en.htm>
- CE marking: <https://europa.eu/youreurope/business/product-rules-compliance/general-product-compliance/ce-marking/index_en.htm>
