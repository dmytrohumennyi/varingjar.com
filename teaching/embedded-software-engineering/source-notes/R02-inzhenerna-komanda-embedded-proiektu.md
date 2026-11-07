---
title: "Лекція 02 — Інженерна команда embedded-проєкту"
date: 2026-09-02
session: 02
source_transcript: ../source-transcripts/2026-09-02.md
status: frozen
frozen_at: 2026-09-28
revision_policy: "Після реконструкції 2026-09-28 цей матеріал не переписується; наступні лекції лише додаються."
---

# Лекція 02. Інженерна команда embedded-проєкту

> **Хронологія:** 02.09.2026 · друге заняття.  
> **Первинне джерело:** [повний транскрипт](../source-transcripts/2026-09-02.md).  
> **Зв'язок:** продовження лекції 01 — від визначення embedded до людей, компонентів і фізичного delivery.

## 1. Від software stack до фізичного виробу

На попередньому занятті embedded було показано як software, що працює на наперед визначеному hardware. Тепер ця ідея розгортається у повний engineering chain.

```text
Application
   ↓
Middleware / OS / services
   ↓
HAL / drivers
   ↓
MCU / SoC
   ↓
PHY / transceivers / power / protection
   ↓
PCB + mechanics + connectors
   ↓
physical environment
```

У реальному виробі вибір MCU/SoC не закриває hardware design. Потрібні power rails, reset/clock, memory за потреби, protection, фізичні інтерфейси, роз'єми, PCB, тепловий режим, корпус, виробництво й інтеграція.

## 2. Hardware engineer: target — лише початок

У лекції hardware stream декомпозується від вибору target до оточення, яке робить цей target придатним до реальної експлуатації.

### 2.1. Мінімальний набір питань

- Який MCU/SoC/DSP/FPGA потрібен за compute, memory, peripherals та lifecycle?
- Як він живиться?
- Як запускається і reset-иться?
- Які clock sources потрібні?
- Які зовнішні інтерфейси треба реалізувати?
- Який electrical protection потрібен?
- Які EMC/ESD вимоги накладає середовище?
- Як плата охолоджується і монтується?
- Чи доступні компоненти для потрібного обсягу виробництва?

### 2.2. Логічний та фізичний рівні інтерфейсу

MCU може мати цифрову peripheral-функцію, але це не означає, що її pins можна напряму вивести на кабель або мережу. Для багатьох інтерфейсів потрібен **transceiver / PHY**, який формує фізичний рівень.

Приклад з CAN:

```text
CAN controller in MCU
       ↓ TX/RX logic
CAN transceiver
       ↓ differential physical signal
CAN_H / CAN_L bus
```

### Редакторське уточнення 01 — CAN та galvanic isolation

Усна теза «CAN є гальванічно розв'язаним інтерфейсом» занадто сильна. **CAN transceiver** перетворює цифрові сигнали controller-а у фізичні, зазвичай диференційні, сигнали середовища передачі. **Galvanic isolation — окремий design choice**, який додають, коли це потрібно системі; CAN сам по собі не гарантує ізоляцію.

Офіційний термінологічний довідник CiA: <https://www.can-cia.org/fileadmin/cia/documents/brochures/can_dictionary_v13_2026.pdf>

## 3. ESD, EMC та shielding — не одне й те саме

Лекція правильно підводить до думки, що physical robustness не можна відкласти «на потім». Але варто розвести поняття:

| Поняття | Сенс |
|---|---|
| ESD | короткочасний електростатичний розряд; потрібні protection paths, layout, components, grounding strategy |
| EMC | здатність виробу нормально працювати у своєму electromagnetic environment і не створювати неприйнятних завад |
| EMI | electromagnetic interference — завади, які система випромінює або сприймає |
| Shielding | один із засобів EMC/EMI control; не універсальна «ESD шапочка» |

Тобто metal shield, TVS diode, common-mode choke, galvanic isolation, filtering, grounding і PCB layout вирішують різні частини проблеми.

## 4. Три базові engineering streams

Лекція зводить core embedded team до трьох взаємозалежних потоків:

```text
             SYSTEM / PRODUCT
             /      |       \
      Firmware   Hardware   Mechanics
             \      |       /
               Integration
```

### Firmware / Software

Від application logic до low-level drivers, boot/update, diagnostics, communication, timing та тестів.

### Hardware

Schematic, component selection, PCB/layout, power, interfaces, protection, prototype bring-up, manufacturing support.

### Mechanics

Enclosure, mounting, interfaces, thermal paths, accessibility, manufacturability, protection від фізичного середовища.

Ключове: ці streams не можуть чесно працювати як три незалежні команди з інтеграцією «в останній день». Mechanical envelope впливає на PCB, PCB — на connector placement і firmware bring-up, power/thermal limits — на software modes, а testability вимагає рішень усіх трьох потоків.

## 5. Architect / system engineer: з'єднати рішення до того, як їх треба інтегрувати

Архітектор у логіці лекції — не «начальник інженерів», а роль, яка тримає цілісність рішення:

- перетворює product need у системну структуру;
- узгоджує interfaces між streams;
- виявляє trade-offs;
- прив'язує рішення до standards/constraints;
- допомагає формувати team composition;
- не дає локальній оптимізації одного stream зламати систему в цілому.

На ранній pre-sale стадії ця роль також допомагає зрозуміти, **яку компетенцію треба показати клієнту** і чи здатна команда реально виконати майбутню роботу.

## 6. Servant manager / servant leader

Лекція окремо вводить management-функцію як **service to team**, а не вертикальне командування.

Практичний зміст:

- зняти blocker між hardware і mechanics;
- донести technical issue клієнту;
- організувати legal/procurement/escalation;
- знайти зовнішнього експерта;
- захистити engineering time від організаційного шуму;
- забезпечити рішення там, де інженер не має authority або контексту.

Таким чином manager і architect працюють поруч, але вирішують різні задачі: architecture тримає технічну цілісність, management — організаційний потік і можливість команди виконати роботу.

## 7. Embedded має supply chain

На відміну від чистого software delivery, embedded прив'язаний до фізичного світу. У лекції з цього виростає окремий ланцюг:

```text
Design
  ↓
component sourcing
  ↓
PCB / mechanical fabrication
  ↓
assembly
  ↓
shipping / customs
  ↓
bring-up
  ↓
rework / next iteration
```

Тому engineering plan залежить не лише від velocity розробників, а й від component availability, lead time, виробничих слотів, логістики і можливості повторної ітерації.

### Редакторське уточнення 02 — vendor/country risk

У лекції є емоційні приклади про конкретних виробників і країни. У конспекті їх краще узагальнити до **supply-chain risk**: lifecycle/NRND/EOL, long-term availability, second-source strategy, геополітичні або export-control обмеження, vendor lock-in, volatility ціни, якість support та traceability component origin. Це перевірювані інженерні критерії; вони сильніші за узагальнення про походження бренду.

## 8. Cost optimization у mass production

В embedded одинична різниця в BOM може масштабуватися на тисячі або мільйони виробів. Тому trade-off «інтегрований дорогий SoC проти простішого MCU + зовнішні PHY» не має універсальної відповіді.

Для рішення треба рахувати:

```text
unit BOM
+ PCB area
+ assembly complexity
+ test cost
+ engineering effort
+ supply risk
+ certification impact
+ lifecycle cost
```

Локально дешевший компонент може зробити дорожчим виробництво або support. І навпаки — дорожчий IC може зменшити BOM/area/assembly.

## 9. Практична організація студентських команд

Наприкінці заняття курс переходить від загальної теорії до групової роботи. Студенти мають самоорганізуватися у невеликі команди. Це не просто адміністративне розбиття: надалі кожна команда буде моделювати компанію, а ролі всередині неї змінюватимуться від business/pre-sale до engineering/delivery.

Початкове правило: **команда має бути достатньо малою, щоб домовлятися, і достатньо повною, щоб розподіляти ролі.**

## 10. Контрольні запитання

1. Чому peripheral controller в MCU ще не дорівнює готовому фізичному інтерфейсу?
2. Яку функцію виконує CAN transceiver?
3. Чому galvanic isolation не слід ототожнювати з CAN?
4. Чим ESD відрізняється від EMC?
5. Які три engineering streams утворюють core embedded team у цьому курсі?
6. Де проходить межа між architect і manager?
7. Чому procurement і logistics можуть потрапити на critical path проєкту?
8. Чому найнижча BOM ціна не завжди означає найнижчу system cost?

## 11. Схема для запам'ятовування

```text
                  CLIENT / PRODUCT NEED
                           │
                    System Architect
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
   Firmware            Hardware            Mechanics
       │                   │                   │
       └────────────── Integration ────────────┘
                           │
                 Test / Manufacturing
                           │
             Procurement / Logistics
                           │
                        Delivery

         Servant Manager removes cross-cutting blockers
```

## 12. Місток до 08.09.2026

Тепер у нас вже є команда, яка потенційно здатна щось розробити. Наступне питання: **звідки взяти роботу?** Тому курс переходить до service business development: як невідома компанія стає видимою, як виникає довіра і як контакт перетворюється на lead.

## Перевірені посилання

- AUTOSAR Classic Platform — layered architecture: <https://www.autosar.org/standards/classic-platform>
- CAN in Automation, CAN Dictionary 2026: <https://www.can-cia.org/fileadmin/cia/documents/brochures/can_dictionary_v13_2026.pdf>
