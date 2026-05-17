## How to execute

`
uv run scripts/analysis_1.py
`

## Statistics explanation

From Claude:

r (Pearson correlation coefficient):

* Ranges from -1 to +1
* Measures the strength and direction of the linear relationship
* r = 1 → perfect positive correlation (more feeding = more weight gain)
* r = 0 → no linear relationship
* r = -1 → perfect negative correlation
* As a rough guide: < 0.3 weak, 0.3–0.6 moderate, > 0.6 strong

p-value:

* The probability of seeing this result by pure random chance, assuming there is actually no relationship
* p < 0.05 → statistically significant (conventionally)
* p = 0.165 (your earlier result) means there's a 16.5% chance the pattern is just noise — too high to trust it

Together: r tells you how strong the relationship looks, p tells you how much to trust that it's real and not just a coincidence given your sample size. With small n, you can have a decent r but a high p — meaning the signal looks promising but you don't have enough data to be confident yet.


## Conclusions

### Until Week May 16 2026

This data is not taking into account baby's first week (hospital).

#### Feeding
Baby is increasing total feeding.
Increase in breastmilk feeding and decrease in formula feeding for the first 4 weeks.

#### Feeding vs diapers

Heavy feeding days are related to heavy wet diaper days.
Poop diapers do not have a strong correlation.

#### Feeding vs weight gain

Although it is obvious that he is gaining weight and he is being fed enough, still cannot draw any conclusions with this data.