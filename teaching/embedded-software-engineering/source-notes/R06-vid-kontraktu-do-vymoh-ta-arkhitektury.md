---
title: "Лекція 06 — Від контракту до вимог та першої архітектури"
date: 2026-09-22
session: 06
source_transcript: ../source-transcripts/2026-09-22.md
status: frozen
frozen_at: 2026-09-28
revision_policy: "Після реконструкції 2026-09-28 цей матеріал не переписується; наступні лекції лише додаються. Прогноз майбутніх занять є прогнозом станом на 22.09.2026."
---

# Лекція 06. Від контракту до вимог та першої архітектури

> **Хронологія:** 22.09.2026 · шосте заняття.  
> **Первинне джерело:** [повний транскрипт](../source-transcripts/2026-09-22.md).  
> **Поворот:** pre-sale закінчується; ролі студентських команд починають рухатися від sales/engagement до system engineering.

## 1. Коли lead стає client у моделі курсу

Лекція проводить чітку навчальну межу: доки є meetings, RFI/RFQ/RFC/Proposal — це lead/opportunity. Після погодження юридичних документів і commercial start point починається client/project relationship.

### Редакторське уточнення 01

У реальних CRM, accounting і contracting processes слова *lead, opportunity, prospect, customer, client* можуть мати інші boundaries. Так само договір не обов'язково підписує саме C-level: signing authority визначає конкретна компанія. У курсі «signed agreement → client» — **корисна навчальна модель**, а не універсальна юридична дефініція.

## 2. Start lead time треба продати ще в Proposal

Підписаний contract не створює людей миттєво. Hardware/firmware/system roles можуть мати довгий hiring/onboarding time. Тому до старту проєкту треба заздалегідь зафіксувати:

- earliest start date;
- staffing assumptions;
- які люди вже available;
- які ролі ще треба recruit/allocate;
- що залежить від client access, hardware, accounts, documents;
- що відбувається, якщо ці prerequisites запізнюються.

Практичний принцип: **не обіцяти Monday start у Thursday, якщо команда ще не існує.**

## 3. Core team формується ще у pre-sale

Найкращий continuity дають люди, які вже бачили problem statement під час pre-sale:

- architect/system engineer;
- technical lead(s);
- engineering/delivery manager;
- domain experts.

Вони утворюють кістяк. Далі команда масштабується залежно від реального scope.

```text
pre-sale core
     ↓
contract
     ↓
core team retained
     +
newly staffed specialists
     ↓
delivery team
```

## 4. Важлива реальність: після контракту discovery може змінити картину

У лекції є досвід, коли до договору клієнт не розкриває весь контекст або використовує pre-sale task як capability check. Тому перший delivery input може відрізнятися від ранньої постановки.

Правильна реакція — не ображатися і не починати кодити старий Proposal, а **повторно зафіксувати actual scope, assumptions та gaps**.

Це ще один аргумент для traceability і change control.

## 5. Навчальний case: робот для автоматичного тестування PCB

Клієнтський input у лекції навмисно поданий як довгий, частково структурований усний потік. Ідея системи:

- готовий 6-DoF robot manipulator;
- custom end effector;
- три способи взаємодії з об'єктами: electromagnetic pickup, mechanical gripper, contact test matrix;
- automatic tool selection/orientation;
- controller/computing;
- computer vision;
- network communication;
- ROS 2 integration;
- reporting/cloud storage;
- operation поруч із людьми.

Цей case потрібен не для вибору конкретного robot brand. Він демонструє, **як із customer speech отримати engineering structure**.

## 6. Business analysis: перший крок — decomposition, не requirements

Business analyst/system analyst спочатку не має права одразу «вигадувати реквайменти». Спершу треба розкласти input на логічні domains/components.

Приклад decomposition з лекції:

```text
Customer statement
      ↓
1. Robot manipulator
2. End effector
3. Sensor / vision subsystem
4. Control subsystem
5. Communication
6. Functional safety
7. Test / reporting / cloud
```

Це створює карту, на якій уже можна ставити питання й шукати missing information.

## 7. Від chapters до user stories

Після decomposition лекція переходить до user stories як способу побачити систему з погляду actor/role.

Класична форма:

```text
As a <role>
I want <capability>
so that <value / outcome>
```

Приклад, близький до лекції:

> As an operator, I want to select and activate the required end-effector tool so that the robot can manipulate different object types without manual reconfiguration.

### Редакторське уточнення 02 — actor vs component

У транскрипті як «user» інколи виступає сам component/control subsystem. Це може бути корисною modeling technique для пошуку взаємодій, але **user story у класичному agile сенсі зазвичай описує потребу actor/stakeholder**. Поведінку компонентів краще далі формалізувати через system/software/hardware requirements або interface requirements.

## 8. Від user need до engineering requirements

Курс будує такий traceability chain:

```text
Customer need / speech
      ↓
Business decomposition
      ↓
User stories / stakeholder needs
      ↓
System requirements
      ↓
HW / SW / FW / Mechanical / Interface requirements
      ↓
Architecture / component description
      ↓
Implementation
      ↓
Verification & Validation
```

Це центральна інженерна ідея заняття: **кожний нижчий рівень має пояснювати, яку верхньорівневу потребу він реалізує.**

## 9. Яким має бути requirement

У лекції сформульовано кілька сильних правил, які варто зберегти.

### Atomic

Один requirement — одна перевірювана вимога, а не пакет різних умов, з'єднаних довгим реченням.

### Unambiguous

Уникати слів «достатньо», «швидко», «зручно», «надійно», якщо вони не визначені кількісно або через acceptance criterion.

### Testable / verifiable

Повинно бути зрозуміло, **як довести виконання**.

### Identifiable and traceable

Requirement має ID, version/change history та зв'язок із parent need/requirement і verification evidence.

### Consistent

Сукупність requirements не повинна мати прихованих суперечностей.

### Приклад

Погано:

> Robot shall position the tool very accurately.

Краще:

> SYS-POS-001: The robot shall position the active tool center point within ±0.2 mm of the commanded Cartesian position under the defined test load.

Тут ще треба визначити test conditions, reference frame і measurement method — саме так requirement стає дорослим.

## 10. System requirements vs component requirements

Лекція правильно розділяє:

### System requirement

Описує поведінку або властивість **системи як цілого** або interaction між великими компонентами.

### Hardware / software / firmware / mechanical requirement

Алокує частину системної поведінки конкретному engineering domain/component.

Приклад:

```text
SYS-COM-001
Robot controller and end-effector controller shall exchange command/status data through the defined system network.

        ↓ allocation

HW-COM-...
SW-COM-...
IF-COM-...
```

## 11. Редакторське уточнення — ROS 2, YOLO і safety

У case звучать ROS 2, YOLO, camera/LiDAR/RADAR як можливі рішення. Їх не треба перетворювати на requirements лише тому, що вони прозвучали у discovery.

- **ROS 2** — technology/platform choice; спочатку треба вимога до interaction/deployment, а вже потім рішення.
- **YOLO** — family of object-detection models; це не автоматично найкращий classifier/inspection method для PCB.
- **LiDAR/RADAR/camera** — candidate sensing technologies, а не універсальна відповідь на functional safety.
- Safety architecture для robot cell має виходити з risk assessment, operating modes і applicable standards; sensor type — наслідок analysis, а не starting assumption.

Це ключова дисципліна requirements engineering: **не змішувати need з premature solution.**

## 12. Перший architecture sketch

Коли system requirements і main components уже проглядаються, можна будувати першу topology/architecture visualization.

Навчальна схема case:

```text
                    Supervisory / Test Computer
                       │        │        │
                       │        │        └── Reports / storage
                       │        └────────── Vision / perception
                       │
                    System network
                  ┌────┴───────────┐
                  │                │
          Robot Controller   End-Effector Controller
                  │                │
          Robot Manipulator   Tool rotation / gripper /
                              magnet / contact matrix
                  └──────── mechanical coupling ───────┘
```

Це ще не detailed architecture. Її задача — **зробити gaps видимими**: interfaces, ownership, power, timing, safety boundary, data flow, physical coupling.

## 13. V-model як traceability, а не декоративна літера V

У лекції requirements переходять до implementation і назад до verification.

```text
Needs                    Validation
  ↓                         ↑
System requirements     System test
  ↓                         ↑
Component requirements  Integration test
  ↓                         ↑
Design / architecture   Unit/component verification
  ↓                         ↑
       Implementation
```

Сенс: test evidence має відповідати тому рівню requirement, який перевіряється.

## 14. Практична робота команд

Наприкінці заняття сформовано перший великий сценарій практики. Команди мають поводитися як маленькі service companies.

До наступної роботи треба:

1. сформувати команди;
2. визначити початкові ролі — engagement/business, technical lead, leadership;
3. придумати company identity;
4. підготувати business card / digital contact;
5. підготувати public-facing story/landing materials;
6. поводитися так, ніби завтра їдете на conference;
7. «вцепити» викладача як lead і добитися follow-up;
8. далі пройти meetings → RFI/RFQ/RFC → Proposal → decomposition → requirements.

Тобто перша атестаційна траєкторія перевіряє **не одну тему**, а весь шлях, який курс уже пройшов з 1 вересня.

## 15. Контрольні запитання

1. Чому staffing lead time треба показати ще до contract start?
2. Що робити, якщо actual scope після договору відрізняється від pre-sale picture?
3. Чому BA спочатку робить decomposition, а не пише requirements?
4. Чим stakeholder need, user story і system requirement відрізняються?
5. Що означає atomic requirement?
6. Чому requirement без verification method слабкий?
7. Чому technology name не завжди має бути requirement?
8. Що саме має показати перша architecture diagram?
9. Як V-model пов'язує requirement і test evidence?
10. Які артефакти має підготувати студентська «компанія» перед першою практикою?

## 16. Прогноз наступних 1–2 занять — станом на 22.09.2026

### Ймовірне заняття 07 — практичний lead-generation / initial meeting simulation

Логічне продовження вже задано домашнім завданням: команди презентують свої «компанії», проводять first contact, намагаються отримати follow-up і фіксують discovery questions. Очікувані артефакти: company one-pager, role map, contact card/QR, 2–3 cases або capability statements, список питань до ліда.

### Ймовірне заняття 08 — від follow-up до RFI/Proposal та requirement baseline

Після симуляції lead funnel природно перейти до конкретного customer case: отримати RFI/problem statement, відповісти, сформувати assumptions/open questions, high-level Proposal та першу traceability chain `need → system requirements → allocated requirements`.

**Важливо:** це прогноз, а не «заморожений факт» про те, що реально відбудеться. Після нового аплоаду фактичне заняття додається новим блоком, а цей прогноз не переписується.

## Перевірені посилання

- ROS 2 documentation: <https://docs.ros.org/en/jazzy/>
- AUTOSAR Classic Platform (приклад layered architecture): <https://www.autosar.org/standards/classic-platform>
- ISO 26262-3:2018 (приклад formal concept/HARA discipline у automotive): <https://www.iso.org/standard/68385.html>
