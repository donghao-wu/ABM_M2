# Donghao(Lucius) Wu Midterm Exercise 1 Sugarscape Model Modification

# StratScape: A Dynamic Socioeconomic Agent-Based Model

**StratScape** is an extension of the classic Sugarscape agent-based model, implemented using [Mesa](https://mesa.readthedocs.io/en/stable/). This model introduces original mechanisms to simulate real-world inequality dynamics, including:

- Non-linear living expenses
- Class-based environmental feedback
- Adaptive metabolism
- Stochastic sugar events

These features help us explore how micro-level behaviors generate emergent macro-level patterns of wealth, mobility, and spatial segregation.

---

## Original Mechanisms

### Non-Linear Living Expenses
Agents pay a cost of living based on the **logarithm of their recent wealth**, reflecting lifestyle inflation. The formula used is:
```python
expense = 1 + log(average_sugar + 1)
```

### Dynamic Sugar Regeneration

Grid cells track the class status of past occupants. Cells frequently visited by high-class agents regenerate sugar faster. This simulates wealth-based neighborhood investment.

### Adaptive Metabolism & Stochastic sugar events (Not included in the code yet)

*Potential solution for adaptive metabolism*
Agents' metabolism increases over time as a function of age and wealth, modeling rising consumption needs:

```python
metabolism = base + 0.01 * log(wealth + 1)
```

*Potential solution for stochastic sugar events*
Each step has a small probability of triggering a sugar boom or crash, adding volatility to the resource landscape. Adding a ramdon probability at each step which can either cause boom or crash.

## GUI and Visualization

The GUI displays:
- Agents as colored dots (blue = low, orange = middle, red = high)
- Sugar levels on the grid (yellow intensity)
- A dynamic **Gini coefficient plot** showing wealth inequality over time.

## How to Run

`solara run app.py`
