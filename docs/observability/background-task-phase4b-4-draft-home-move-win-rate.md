# Background Task Output: phase4b-4-draft-home-move-win-rate
Completed: 2026-06-13 13:51 UTC
Model: qwen3:14b
Wall time: 50.1s | Tokens: P=160 E=1205

## Output

Thinking...
Okay, I need to draft Phase 4b-4 for the synthetic energy supplier project,[8D[K
project, specifically focusing on the home move win rate. The user mentione[8D[K
mentioned looking at the MASTER_BACKLOG.md's Phase 4b section and following[9D[K
following the pattern from saas/churn_model.py and saas/clv_model.py. They [K
want a pure module with plain dict in/out, no sim/ imports. Also, they need[4D[K
need both the module and the test file as markdown code blocks with file pa[2D[K
paths.

First, I'll start with the home_move_win_rate.py module. The pattern from c[1D[K
churn_model.py and clv_model.py probably involves a function that takes a d[1D[K
dictionary of inputs and returns a dictionary of outputs. The function shou[4D[K
should calculate the win rate based on some factors. Since it's a synthetic[9D[K
synthetic model, I'll need to define parameters that influence the win rate[4D[K
rate, like customer tenure, satisfaction score, and maybe competition rate.[5D[K
rate.

For the function, I'll create a function called calculate_home_move_win_rat[27D[K
calculate_home_move_win_rate. The inputs might include customer_data, which[5D[K
which contains tenure, satisfaction, and competition_rate. The output shoul[5D[K
should be a win_rate between 0 and 1. The formula could be a weighted sum o[1D[K
of these factors. For example, higher tenure might decrease the win rate (c[2D[K
(customers are less likely to move), higher satisfaction increases it (they[5D[K
(they might leave if satisfied?), but maybe that's counterintuitive. Wait, [K
if a customer is satisfied, they might be less likely to leave, so maybe sa[2D[K
satisfaction has a negative weight. Competition rate could have a positive [K
impact, as more competition might make customers more likely to switch.

So, the formula could be something like: win_rate = (satisfaction_score * 0[1D[K
0.3) - (tenure_years * 0.1) + (competition_rate * 0.2). Then clamp it betwe[5D[K
between 0 and 1. That seems reasonable. I'll need to handle cases where inp[3D[K
inputs are missing by setting defaults.

Next, the test file. The test should check that the function returns the co[2D[K
correct win rate for given inputs. I'll use pytest's pytest.mark.parametriz[22D[K
pytest.mark.parametrize to test different scenarios. For example, a custome[7D[K
customer with high satisfaction, low tenure, and high competition should ha[2D[K
have a higher win rate. Another case with low satisfaction, high tenure, lo[2D[K
low competition should have a lower win rate. Also, test edge cases where i[1D[K
inputs are at the extremes.

I need to make sure that the code doesn't import anything from sim/ as per [K
the instructions. The module should be self-contained, using only standard [K
libraries. The tests will use pytest, so I'll include the necessary imports[7D[K
imports like pytest and assert statements.

Putting it all together, the home_move_win_rate.py will have the calculate [K
function, and the test file will have parametrized tests. I'll format them [K
as markdown code blocks with the appropriate file paths.
...done thinking.

```python
# saas/home_move_win_rate.py
def calculate_home_move_win_rate(customer_data: dict) -> dict:
    """
    Calculate probability of winning a home move customer based on:
    - Tenure (longer tenure = lower win rate)
    - Satisfaction score (higher = lower win rate)
    - Competition rate in area (higher = higher win rate)
    """
    # Default parameters
    params = {
        'tenure_weight': -0.1,
        'satisfaction_weight': -0.3,
        'competition_weight': 0.2,
        'base_rate': 0.15,
        'max_rate': 0.4,
        'min_rate': 0.05
    }
    
    # Extract inputs
    tenure_years = customer_data.get('tenure_years', 0)
    satisfaction_score = customer_data.get('satisfaction_score', 5)  # 1-10[4D[K
1-10 scale
    competition_rate = customer_data.get('competition_rate', 0.2)  # 0-1
    
    # Calculate win rate
    win_rate = (
        params['base_rate'] +
        (tenure_years * params['tenure_weight']) +
        (satisfaction_score * params['satisfaction_weight']) +
        (competition_rate * params['competition_weight'])
    )
    
    # Clamp between min and max rates
    win_rate = max(min(win_rate, params['max_rate']), params['min_rate'])
    
    return {'home_move_win_rate': win_rate}
```

```python
# tests/saas/test_home_move_win_rate.py
import pytest
from saas.home_move_win_rate import calculate_home_move_win_rate

@pytest.mark.parametrize("input_data, expected_rate", [
    # High competition, low satisfaction, short tenure = high win rate
    ({
        'tenure_years': 1,
        'satisfaction_score': 3,
        'competition_rate': 0.6
    }, 0.35),
    
    # Long tenure, high satisfaction, low competition = low win rate
    ({
        'tenure_years': 10,
        'satisfaction_score': 8,
        'competition_rate': 0.1
    }, 0.05),
    
    # Mid values
    ({
        'tenure_years': 5,
        'satisfaction_score': 5,
        'competition_rate': 0.3
    }, 0.15),
    
    # Missing inputs use defaults
    ({}, 0.15),
    
    # Edge case: max possible rate
    ({
        'tenure_years': 0,
        'satisfaction_score': 1,
        'competition_rate': 1.0
    }, 0.4)
])
def test_calculate_home_move_win_rate(input_data, expected_rate):
    result = calculate_home_move_win_rate(input_data)
    assert abs(result['home_move_win_rate'] - expected_rate) < 0.01
```
