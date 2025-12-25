# MyFaceitStats

**My name is Yusuf Arhan Doyaroglu. This is my DSA210 term project.**

## Motivation

**FACEIT** is a competitive gaming platform for esports. **Counter-Strike 2 (CS2)** is a tactical first-person shooter game where two teams of 5 players compete in matches consisting of multiple rounds. Teams alternate between attacking and defending positions, and each round is won by eliminating the enemy team or completing an objective.

In FACEIT matches, players are often judged by their **KD (Kill/Death ratio)**—a traditional performance metric calculated as kills divided by deaths. However, KD is easy to read but can miss what really wins rounds. A player can maintain a good KD by getting late kills (after the round outcome is largely decided), while another player might take hard **entry duels** (the first combat encounter in a round) that open the site and help the team but lower their KD. The first duel in a round changes the state from 5v5 to 5v4 or 4v5. With a 5v4 numerical advantage, teams trade more safely, take map control more easily, and close the round more often. Because of this, entry actions may explain winning better than KD, especially early in the round.

**This project focuses on two key questions:**
1. Do entry signals relate to **win/loss** and **score difference** more strongly than KD?
2. When we include simple controls like **ADR**, **KR**, **map**, and **overtime**, do entry signals improve prediction of **match result** compared with using KD alone?



## Data Sources

**Note**: This is not a public dataset. The data consists of my private match statistics collected from my own FACEIT account via the FACEIT API.

### **1. Faceit API Data**
- **Source**: [FACEIT Data API](https://docs.faceit.com/docs/data-api/)
- **Data Type**: My private match statistics
- **Key Features**:
  - `date` : Match date and time.
  - `map` : Map name. Kept in the file but not used in models.
  - `result` : Win or Loss.
  - `kills` : Total kills.
  - `deaths` : Total deaths.
  - `assists` : Total assists.
  - `hs` : Headshot kills.
  - `hs_percent` : Headshot percentage.
  - `kd` : Kill to death ratio.
  - `kr` : Kills per round.
  - `mvps` : MVP rounds.
  - `adr` : Average damage per round.
  - `first_kills` : Rounds with the first kill.
  - `first_deaths` : Rounds with the first death.
  - `entry_count` : Entry duels taken.
  - `entry_wins` : Entry duels won.
  - `rounds_played` : Total rounds.
  - `overtime` : True or False.
  - `match_duration_min` : Match duration in minutes.
  - `my_team_score` : Final score for my team.
  - `enemy_team_score` : Final score for the other team.
  - `round_difference` : `my_team_score - enemy_team_score`.

---

## **Data Collection**
1. **Faceit API Data**:
   - **API Integration**: Fetched data using the **FACEIT Data API** (v4).
     - **Tools**: Python `requests` library with a registered [FACEIT API key](https://faceit.com/developers).
     - **Features**: Automated data collection from 100 most recent CS2 matches, with error handling for missing statistics, timestamp conversion, overtime detection, and derived metrics calculation.
     - 📎 [`faceit_data_api.py`](./faceit_data_api.py)

## **Hypothesis Testing**

1. **H1: Entry win rate is positively associated with winning the match.**
   - **H0**: Entry-related signals (especially `entry_win_rate`) are not associated with `result` (win/loss).
   - **H1**: Higher entry-related signals (especially `entry_win_rate`) are positively associated with `result` (win/loss).
   - **Variables**:
     - `entry_rate` = `entry_count` / `rounds_played`
     - `entry_win_rate` = `entry_wins` / max(`entry_count`, 1)
     - `result` ∈ {win, loss}

2. **H2: A more positive `first_kills − first_deaths` balance is associated with a larger `round_difference`.**
   - **H0**: `fk_fd_diff` has no association with `round_difference`.
   - **H1**: `fk_fd_diff` has a positive association with `round_difference`.
   - **Variables**:
     - `fk_fd_diff` = `first_kills` - `first_deaths`
     - `round_difference` = `my_team_score` - `enemy_team_score`

3. **H3: Entry-related signals add predictive value beyond `KD` when basic controls are included.**
   - **H0**: Adding entry features does not improve predictive performance beyond `KD` + `ADR` + `KR` + `map` + `overtime`.
   - **H1**: Adding entry features improves predictive performance beyond `KD` + `ADR` + `KR` + `map` + `overtime`.
   - **Variables**:
     - Base controls: `KD`, `ADR`, `KR`, `map`, `overtime`
     - Entry features: `entry_rate`, `entry_win_rate`, `first_kills`, `first_deaths`

---

### **Statistical Tests**

**H1: Entry win rate is positively associated with winning the match**
- SUPPORTED
- Pearson correlation: r=0.162, p=0.0003
- Partial correlation (map+month control): r=0.159, p=0.0005

**H2: A more positive first_kills - first_deaths balance is associated with a larger round_difference**
- NOT SUPPORTED
- Pearson correlation: r=-0.0026, p=0.9547
- Partial correlation (map+month control): r=-0.0009, p=0.9842

**H3: Entry-related signals add predictive value beyond KD when basic controls are included**
- PARTIALLY SUPPORTED
- entry_win_rate: r=0.162, p=0.0003
- first_kills: r=0.128, p=0.0049
- first_deaths: r=-0.147, p=0.0012
- entry_rate: r=-0.030, p=0.514

### **Machine Learning Results**

**H1: Entry win rate is positively associated with winning the match**
- PARTIALLY SUPPORTED
- Test Accuracy: 72.16%
- ROC-AUC: 0.8452
- entry_win_rate coefficient: +0.1029 (ranks 5th after KD/ADR/KR)

**H2: A more positive first_kills - first_deaths balance is associated with a larger round_difference**
- NOT SUPPORTED
- Linear Regression Test R²: -0.0085
- Random Forest Test R²: -0.1458

**H3: Entry-related signals add predictive value beyond KD when basic controls are included**
- NOT SUPPORTED
- Base Model (KD+ADR+KR) Accuracy: 76.29%
- Full Model (Base+Entry) Accuracy: 72.16%
- Base Model AUC: 0.8678 vs Full Model AUC: 0.8452

### **Key Findings**
- Traditional metrics (KD, ADR, KR) are strongest predictors (KD: r=0.47)
- Entry win rate shows statistical significance but limited practical value
- Simpler models outperform complex ones
- Round margins unpredictable from individual stats alone

