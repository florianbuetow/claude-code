# How Wardley Maps Work: The Core Concept

Read this before writing any Wardley map. It explains *why* maps work, so your output is a useful
strategic artifact and not just syntactically valid DSL. For the syntax itself, see
[`wtg2-dsl-reference.md`](wtg2-dsl-reference.md).

## What Is a Wardley Map?

A **Wardley map** is a visual strategy tool that shows:

1. **What you need** to serve your users (value chain)
2. **How evolved** each component is (market maturity)
3. **What depends on what** (dependencies)
4. **Where to act** strategically (build/buy/outsource decisions)

Instead of drowning in strategy documents, you get a simple picture showing where you're strong,
where you're exposed, and where to act next.

---

## The Two Axes (The Coordinate System)

Every component in a Wardley map is plotted on two dimensions.

### Y-Axis (Vertical): Visibility / Value Chain Position

| Position | Meaning |
|----------|---------|
| **Top (high visibility)** | Visible to end-user; directly addresses user need |
| **Middle** | Intermediate capabilities |
| **Bottom (low visibility)** | Hidden from user; subordinate components |

- The **anchor** (user need) is always at the top.
- Below the anchor are needs the company seeks to meet.
- Below those are components required to meet those needs.
- Value flows **downward** through the chain.

### X-Axis (Horizontal): Evolution / Commoditization

In WTG2 the evolution axis is divided into four phases, addressed by roman numerals (`I`–`IV`):

| Phase | Stage | Description | Decision |
|-------|-------|-------------|----------|
| **I (left)** | **Genesis/Novel** | Novel, uncertain, research, high failure risk | Build |
| **II** | **Custom-built/Emerging** | Understood but unique, you build it | Build |
| **III** | **Product/Good** | Off-the-shelf, rental, you buy it | Buy |
| **IV (right)** | **Commodity/Best** | Utility, standard, you outsource it | Outsource |

- Components to the **left** are less evolved (rare, higher risk).
- Components to the **right** are more evolved (common, lower risk).
- Everything evolves from left → right over time.

---

## The Value Chain (Vertical Flow)

A Wardley map shows a **value chain** — the sequence of activities that create value for customers:

```
                    USER NEED (anchor)
                        ↓
                 What user actually wants
                        ↓
              Primary capabilities needed
                        ↓
           Supporting capabilities needed
                        ↓
         Subordinate/infrastructure components
```

**Example: Cup of Tea Shop**

```
    User wants cup of tea (anchor)
        ↓
    Customer interaction
        ↓
    Tea preparation
        ↓
    Hot water
        ↓
    Electricity/power
        ↓
    Power grid (commodity)
```

The person at the top thinks about tea, not about the power grid.

---

## Dependencies (Arrows Between Components)

Components are linked by **dependency lines**:

- `A -> B` means **A depends on B** (A needs B to work).
- Arrows show **flow direction** (data, value, control).
- If B fails, A fails.

**Example: Drone Courier**

```
User needs delivery -> Location Identifier -> Can I Deliver There? -> Stock -> Depots
```

If "Can I Deliver There?" fails (e.g., weather bad), the whole chain breaks.

---

## Evolution Stages (What Happens Over Time)

Everything evolves through four stages:

1. **Genesis (Novel, phase I)** → You create something new
   - High risk, high uncertainty — you **build** it
   - Example: First drone delivery service

2. **Custom-built (Emerging, phase II)** → You understand it but it's unique
   - Still risky, but understood — you **build** it (customize)
   - Example: Custom weather API for drones

3. **Product (Good, phase III)** → Off-the-shelf solution exists
   - Stable, vendor-supported — you **buy** it
   - Example: Standard GPS API

4. **Commodity (Best, phase IV)** → Utility, fully standardized
   - Low risk, cheapest — you **outsource** it
   - Example: Electricity, internet access

**Strategic insight:** Move components right when you want stability; keep components left when you
want differentiation.

---

## Strategic Decision-Making (Build/Buy/Outsource)

The map tells you **what to do** with each component:

| Evolution Phase | Decision | Reason |
|-----------------|----------|--------|
| **Genesis (I, left)** | **Build** | Novel tech = differentiation opportunity |
| **Custom (II)** | **Build** | Still unique, worth customizing |
| **Product (III)** | **Buy** | Off-the-shelf exists, cheaper to buy |
| **Commodity (IV, right)** | **Outsource** | Utility, cheapest to rent |

**Example: E-Commerce Platform**

```
Payment Processing (IV) -> BUY (commoditized APIs)
Fraud Detection (II)    -> BUILD (needs customization)
Shopping Cart (III)     -> BUILD (UX differentiation)
```

You build what differentiates you, buy what's commoditized.

---

## Situational Awareness (The Real Power)

Wardley maps give you **situational awareness** — understanding where value flows in your industry,
where it stagnates, where new value will emerge, what you're exposed to, and what opportunities
exist. Instead of guessing, you see the **logic of your industry**.

**Example insights from a map:**

- "Our core differentiation (shopping cart) is becoming commoditized → we're losing advantage"
- "We're building payment processing when APIs are commoditized → wasteful"
- "Weather data is custom (left) → we need to build expertise there"
- "Power grid is commodity (right) → outsource completely"

---

## Why Maps Beat Other Tools

| Tool | Problem | Wardley Map Solution |
|------|---------|---------------------|
| **SWOT** | Categories, no tactics | Shows relationships + actionable intelligence |
| **Mind maps** | No structure, no evolution | Structured value chain + evolution axis |
| **Process maps** | No market context | Shows market pressures + competition |
| **Strategy docs** | Too long, hard to update | Simple picture, easy to iterate |

---

## The Strategic Elements (Wardley Mapping Framework)

Wardley Mapping isn't just the map — it's a complete framework:

1. **Purpose** — The moral imperative ("the game"): what are you trying to achieve?
2. **Landscape** — The map: what exists, what depends on what, where you're strong/exposed.
3. **Climate** — External forces: market pressures, technology evolution, regulatory changes.
4. **Doctrine** — Universal principles for success (e.g. "user needs first", "adapt quickly").
5. **Leadership** — Making decisions using the map + doctrine + climate.

The map is just one piece — it enables better leadership decisions.

---

## When to Use Wardley Maps

**Create a map when:**

- Starting a new product/service
- Evaluating build/buy/outsource decisions
- Understanding ecosystem dependencies
- Identifying innovation opportunities
- Communicating strategy to stakeholders
- Doing pre-mortem analysis (what could fail?)
- Anticipating market disruption

**Don't use when:**

- You need detailed implementation specs
- You're solving tactical bugs
- You just want a pretty diagram (maps must be useful)

---

## Key Principles (Doctrine)

1. **Start with user needs** — Not business needs, not "we want X"
2. **Map what exists** — Not what you wish existed
3. **Be imperfect** — A useful map is better than a perfect one
4. **Map → Conversation → Decision** — The map enables discussion, not replaces it
5. **Multiple snapshots** — Map at different times to see evolution
6. **Challenge assumptions** — "Is this really commodity?" "Do we need this?"
7. **User-centric** — Orient towards the customer, not the company

---

## Example: Reading a Drone Courier Map

```
    User wants stuff quickly (anchor)          ← top, high visibility
           ↓
    Location Identifier (IV)                   ← Commodity (buy), visible
           ↓
    Can I Deliver There? (III)                 ← Product (buy), moderate visibility
           ↓              ↓              ↓
        Stock (III)   Weather (II)   Range of Drones (I)
         (buy)         (build)        (build - novel!)
```

**Insights:**

- User need is high-visibility (top) — correct.
- Location ID is commodity — buy GPS API.
- Weather is custom — build expertise (differentiation).
- Drone range is genesis — definitely build (novel tech).
- If drone tech becomes commodity, we lose advantage.

This tells you: **Build weather expertise, buy GPS, invest in drone innovation**.

---

## The Bottom Line

Wardley maps help you make **decisions you'll defend in 3 years, not decisions you'll regret in
3 months**. They reveal where you're strong, where you're exposed, where to act next, what to build
vs. buy vs. outsource, and how your industry will evolve. The map is a **snapshot** — make multiple
over time to see patterns you can't see in a single view.
