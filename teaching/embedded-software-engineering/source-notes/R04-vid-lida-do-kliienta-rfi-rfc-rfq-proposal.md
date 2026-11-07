---
title: "Лекція 04 — Від ліда до формалізованого pre-sale"
date: 2026-09-15
session: 04
source_transcript: ../source-transcripts/2026-09-15.md
status: frozen
frozen_at: 2026-09-28
revision_policy: "Після реконструкції 2026-09-28 цей матеріал не переписується; наступні лекції лише додаються."
---

# Лекція 04. Від ліда до формалізованого pre-sale

> **Хронологія:** 15.09.2026 · четверте заняття.  
> **Первинне джерело:** [повний транскрипт](../source-transcripts/2026-09-15.md).  
> **Попередня точка:** маємо контакт після referral/event/content.  
> **Мета заняття:** довести lead до технічного follow-up і перших формальних pre-sale артефактів.

## 1. Event — не фінал, а початок funnel

На цьому занятті тема конференцій продовжується вже як **керована business-development система**, а не просто networking.

Логіка:

```text
visibility / event
      ↓
first contact
      ↓
lead
      ↓
initial meeting
      ↓
identified pain point
      ↓
technical follow-up
      ↓
formal information exchange
```

Успішна поїздка вимірюється не кількістю розданих business cards, а тим, чи з'явилися контакти з конкретним next action.

## 2. Speaker як частина кампанії, а не окрема людина на сцені

У лекції важливо підкреслено: speaking slot працює лише разом із підготовкою до і після події.

### До події

- вибрати тему за business relevance;
- підготувати speaker-а;
- публікувати анонси;
- визначити target companies/people;
- підготувати supporting team і case materials.

### Під час події

- speaker створює attention і authority;
- команда працює в залі, знайомиться, слухає pain points;
- контакти одразу фіксуються разом з контекстом.

### Після події

- швидкий follow-up;
- конкретна пропозиція наступної розмови;
- внутрішня класифікація contact/lead/opportunity.

## 3. Initial meeting: клієнт оцінює не тільки компанію, а конкретних людей

До першої серйозної розмови команда має зробити домашню роботу: зрозуміти company profile, продукти, публічні технічні напрями і ролі учасників зустрічі.

У лекції презентація provider-а умовно складається з трьох блоків:

1. **Хто ми:** масштаб, географія, індустрії, delivery capability.
2. **Чому нам можна довіряти:** кейси, процеси, стандарти/сертифікації там, де вони релевантні.
3. **Що ми вже робили схожого:** невеликий набір case studies, підібраний під конкретного співрозмовника.

Важливе правило: не вивалювати на клієнта весь портфель. Case studies мають відповідати його контексту.

## 4. Перехід від presentation до discovery

Презентація лише відкриває двері. Основна цінність з'являється, коли provider переходить до **конкретних запитань** і показує domain competence.

```text
company story
   ↓
relevant cases
   ↓
technical questions
   ↓
pain point
   ↓
"we should talk about this separately"
```

У лекції це метафорично названо «дати пластир на місце, де болить»: не вирішити все на першій зустрічі, а показати, що проблема розпізнана і у вас є релевантна компетенція.

## 5. Technical follow-up

На наступну зустріч варто приводити людей, які можуть говорити про конкретний technical domain. Важливо зберігати **continuity of faces**: ключові люди першого контакту не повинні повністю зникнути, інакше довіру доводиться будувати заново.

Мета follow-up у логіці курсу:

- уточнити pain;
- показати technical depth;
- зрозуміти boundaries;
- не «безкоштовно спроєктувати весь продукт»;
- перейти до структурованого обміну інформацією.

## 6. RFI — Request for Information

RFI — запит, за допомогою якого потенційний клієнт перевіряє provider capability. Формат може бути дуже простим: spreadsheet із питаннями й колонкою answer/evidence.

Типові групи питань:

- company profile;
- relevant domains;
- engineering roles і capacity;
- tools;
- languages/technology stack;
- quality/safety/security processes;
- standards/framework experience;
- laboratories / equipment / manufacturing capability;
- references або allowed case descriptions.

У великих закупівлях однаковий RFI часто отримують кілька vendors, тому відповідь має бути **порівнюваною, доказовою і без маркетингового туману**.

## 7. RFQ — Request for Quotation

RFQ просить вже не тільки описати capability, а оцінити **вартість/обсяг/термін**. В embedded це складніше, ніж «кількість engineer-hours», бо можуть входити:

- engineering effort;
- components;
- PCB/mechanical fabrication;
- assembly;
- test equipment;
- prototypes/re-spins;
- external labs;
- shipment/customs;
- certification-related samples/activities.

Якщо RFQ приходить до достатньої technical definition, estimation може бути грубим або сильно залежати від assumptions. Це треба явно показувати.

## 8. RFC у цьому курсі

На лекції RFC використовується як **Request for Clarification** — структурований запит на уточнення solution/problem statement.

### Редакторське уточнення 01 — acronym policy

`RFC` не має одного універсального B2B procurement meaning. У software world воно часто означає *Request for Comments*; в окремих компаніях може використовуватись інакше. Тому в документах курсу слід писати повну форму при першій появі: **RFC (Request for Clarification — course terminology)**.

## 9. Proposal як інтеграція попередніх знань

Proposal не повинен виникати з повітря. Він збирає те, що вже відомо з meetings, RFI/RFQ/RFC та власного analysis.

```text
meetings ─┐
RFI ──────┤
RFQ ──────┼──→ Proposal
RFC ──────┤
research ─┘
```

Перший каркас Proposal, який формується на цій стадії:

- executive/solution summary;
- problem understanding;
- assumptions і open questions;
- high-level architecture/approach;
- engineering workstreams;
- verification/validation intent;
- team/resources;
- schedule/estimate;
- risks/dependencies;
- commercial model.

Повний розбір standards, commercial model та risk allocation переходить у наступне заняття.

## 10. Version control для pre-sale documents

Лекція рекомендує ставитися до Proposal як до керованого engineering artifact. Практична схема:

```text
0.1 → 0.2 → 0.3  internal drafts
          ↓
        1.0      external release
          ↓ client feedback
        1.1 → 1.2 internal work
          ↓
        2.0      next external release
```

Номер версії сам по собі не головне. Головне — щоб було видно:

- дату;
- author/owner;
- change history;
- що змінилося після client feedback;
- яка саме версія є basis for estimate/decision.

## 11. Не віддати весь engineering без контракту

Pre-sale engineering має межу. Чим більше provider розкриває готових design details, тим більше безоплатної роботи він віддає до комерційного рішення.

Тому потрібен internal review:

- чи достатньо evidence, щоб показати capability;
- чи не перетворився Proposal у фактично безкоштовний detailed design;
- чи assumptions видимі;
- чи estimation traceable;
- чи promises реально deliverable.

## 12. Контрольні запитання

1. Чим lead відрізняється від випадкового контакту?
2. Яка мета initial meeting?
3. Чому case studies треба підбирати під конкретного клієнта?
4. Чим RFI відрізняється від RFQ?
5. Чому estimation embedded-проєкту включає більше, ніж engineer-hours?
6. Чому треба розшифровувати RFC у кожному конкретному процесі?
7. Що Proposal інтегрує з попередніх етапів?
8. Навіщо pre-sale document version control?
9. Де проходить межа між доказом capability і безкоштовним engineering?

## 13. Таблиця артефактів

| Артефакт | Основне питання | Вихід provider-а |
|---|---|---|
| Initial meeting | «Чи є сенс говорити далі?» | trust + next meeting |
| Technical follow-up | «Чи розуміють вони нашу проблему?» | clarified pain + technical credibility |
| RFI | «Хто ви і що реально вмієте?» | structured capability evidence |
| RFQ | «Скільки це може коштувати/тривати?» | estimate + assumptions |
| RFC (course) | «Що саме мається на увазі?» | clarified scope/solution inputs |
| Proposal | «Як ви пропонуєте це зробити?» | integrated technical/commercial view |

## 14. Місток до 16.09.2026

Наступний крок — зробити Proposal дорослим engineering/commercial документом: **які standards і reference documents потрібні, як впливають certification/conformity constraints, як обрати T&M або Fixed Price і хто реально несе які ризики.**
