# MyFaceitStats

**My name is Yusuf Arhan Doyaroglu. This is my DSA210 term project.**

## Motivation


FACEIT is a competitive gaming platform that hosts professional Counter-Strike 2 (CS2) matches. In FACEIT matches, players are often judged by their KD (Kill/Death ratio). KD is easy to read, but it can miss what really wins rounds. A player can keep a good KD by getting late kills, while another player can take hard entry duels that open the site and help the team but lower KD. The first duel in a round changes the state from 5v5 to 5v4 or 4v5. With a 5v4 lead, teams trade more safely, take map control more easily, and close the round more often. Because of this, entry actions may explain winning better than KD, especially early in the round.

**This project focuses on two key questions:**
1. Do entry signals relate to **win/loss** and **score difference** more strongly than KD?
2. When we include simple controls like **ADR**, **KR**, **map**, and **overtime**, do entry signals improve prediction of **match result** compared with using KD alone?



## Data Sources

### **1. Faceit API Data**
- **Source**: [FACEIT Data API](https://docs.faceit.com/docs/data-api/)
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
     - **Features**: Automated data collection from 500 most recent CS2 matches, with error handling for missing statistics, timestamp conversion, overtime detection, and derived metrics calculation.
     - 📎 [`faceit_data_api.py`](./faceit_data_api.py)
