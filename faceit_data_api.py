import os, time, requests, pandas as pd
from datetime import datetime

API_KEY = ""  # API key provided by Faceit API
NICK    = ""  # Your Faceit username
GAME    = "cs2"                      


HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_player(nick, game=GAME):
    r = requests.get("https://open.faceit.com/data/v4/players",
                     headers=HEADERS, params={"nickname": nick, "game": game})
    if r.status_code == 401:
        raise SystemExit("401 Unauthorized: Invalid/cancelled API key. Please regenerate and update.")
    r.raise_for_status()
    return r.json()

def get_recent_match_ids(player_id, game=GAME, limit=200, offset=0):
    r = requests.get(f"https://open.faceit.com/data/v4/players/{player_id}/history",
                     headers=HEADERS, params={"game": game, "limit": limit, "offset": offset})
    r.raise_for_status()
    return [it["match_id"] for it in r.json().get("items", [])]

def get_match_stats(match_id):
    r = requests.get(f"https://open.faceit.com/data/v4/matches/{match_id}/stats",
                     headers=HEADERS)
    if r.status_code == 404:
        return None  # No stats data available
    r.raise_for_status()
    return r.json()

def get_match_details(match_id):
    r = requests.get(f"https://open.faceit.com/data/v4/matches/{match_id}",
                     headers=HEADERS)
    r.raise_for_status()
    return r.json()

def extract_my_rows(stats_json, match_details, my_nickname):
    rows = []
    # Get date information from match details and convert Unix timestamp to date format
    started_at_timestamp = match_details.get("started_at", "")
    if started_at_timestamp:
        try:
            match_date = datetime.fromtimestamp(started_at_timestamp).strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            match_date = str(started_at_timestamp)
    else:
        match_date = ""
    
    # Get result information
    results = match_details.get("results", {})
    winner = results.get("winner", "")
    
    # Get match duration and rounds information
    started_at = match_details.get("started_at", 0)
    finished_at = match_details.get("finished_at", 0)
    match_duration = finished_at - started_at if finished_at and started_at else 0
    rounds_played = 0
    overtime = False
    
    # Find which team the player is on and get team scores
    my_faction = None
    my_team_score = 0
    enemy_team_score = 0
    teams = match_details.get("teams", {})
    
    for faction_id, team_data in teams.items():
        roster = team_data.get("roster", [])
        for player in roster:
            if player.get("nickname") == my_nickname:
                my_faction = faction_id
                break
        if my_faction:
            break
    
    # Get team scores from match results
    results = match_details.get("results", {})
    faction1_score = results.get("faction1", {}).get("score", 0)
    faction2_score = results.get("faction2", {}).get("score", 0)
    
    if my_faction == "faction1":
        my_team_score = faction1_score
        enemy_team_score = faction2_score
    elif my_faction == "faction2":
        my_team_score = faction2_score
        enemy_team_score = faction1_score
    
    # Determine the result
    if my_faction and winner:
        if my_faction == winner:
            result = "Win"
        else:
            result = "Loss"
    else:
        result = ""
    
    # Calculate round difference
    round_difference = my_team_score - enemy_team_score
    
    for rnd in stats_json.get("rounds", []):
        map_name = rnd.get("round_stats", {}).get("Map")
        rounds_played = int(rnd.get("round_stats", {}).get("Rounds", 0) or 0)
        
        # Check for overtime (25+ rounds in CS2)
        if rounds_played >= 25:
            overtime = True
        
        # Get team scores from round stats
        score_string = rnd.get("round_stats", {}).get("Score", "0 / 0")
        winner_team_id = rnd.get("round_stats", {}).get("Winner", "")
        
        if " / " in score_string:
            scores = score_string.split(" / ")
            winner_score = int(scores[0]) if len(scores) > 0 else 0
            loser_score = int(scores[1]) if len(scores) > 1 else 0
        else:
            winner_score = loser_score = 0
        
        for team in rnd.get("teams", []):
            for p in team.get("players", []):
                if p.get("nickname") == my_nickname:
                    s = p.get("player_stats", {})
                    
                    # Get additional performance metrics
                    adr = float(s.get("ADR", 0) or 0)
                    first_kills = int(s.get("First Kills", 0) or 0)
                    entry_count = int(s.get("Entry Count", 0) or 0)
                    entry_wins = int(s.get("Entry Wins", 0) or 0)
                    first_deaths = entry_count - entry_wins  # First deaths = entry attempts - entry wins

                    # Determine which team the player is on and get correct scores
                    team_id = team.get("team_id", "")
                    if team_id == winner_team_id:
                        my_team_score = winner_score
                        enemy_team_score = loser_score
                    else:
                        my_team_score = loser_score
                        enemy_team_score = winner_score
                    
                    # Calculate round difference
                    round_difference = my_team_score - enemy_team_score
                    
                    rows.append({
                        # Basic Information
                        "date": match_date,
                        "map": map_name,
                        "result": result,
                        
                        # Basic Performance
                        "kills": int(s.get("Kills", 0)),
                        "deaths": int(s.get("Deaths", 0)),
                        "assists": int(s.get("Assists", 0)),
                        "hs": int(s.get("Headshots", 0)),
                        "hs_percent": float(str(s.get("Headshots %", 0)).replace("%","")),
                        "kd": float(s.get("K/D Ratio", 0) or 0),
                        "kr": float(s.get("K/R Ratio", 0) or 0),
                        "mvps": int(s.get("MVPs", 0)),
                        
                        # Detailed Performance
                        "adr": adr,
                        "first_kills": first_kills,
                        "first_deaths": first_deaths,
                        "entry_count": entry_count,
                        "entry_wins": entry_wins,
                        
                        # Match Information
                        "rounds_played": rounds_played,
                        "overtime": overtime,
                        "match_duration_min": round(match_duration / 60, 1),
                        
                        # Team Scores
                        "my_team_score": my_team_score,
                        "enemy_team_score": enemy_team_score,
                        "round_difference": round_difference
                    })
    return rows

def main():
    player = get_player(NICK)
    pid = player["player_id"]
    
    # Get 500 matches in 5 batches of 100 (API limit is 100 per request)
    all_match_ids = []
    for batch in range(5):
        offset = batch * 100
        print(f"Fetching matches batch {batch + 1}/5 (offset: {offset})...")
        batch_match_ids = get_recent_match_ids(pid, limit=100, offset=offset)
        if not batch_match_ids:
            print(f"  → No more matches found at offset {offset}")
            break
        all_match_ids.extend(batch_match_ids)
        print(f"  → Got {len(batch_match_ids)} matches (total so far: {len(all_match_ids)})")
    
    all_rows = []
    total_matches = len(all_match_ids)
    print(f"\nProcessing {total_matches} matches...")
    
    for i, mid in enumerate(all_match_ids, 1):
        print(f"Processing match {i}/{total_matches} (ID: {mid})")
        stats = get_match_stats(mid)
        if stats is None:  # Skip if no stats data available
            print(f"  → Skipped (no stats data)")
            continue
        match_details = get_match_details(mid)
        all_rows.extend(extract_my_rows(stats, match_details, NICK))
    
    df = pd.DataFrame(all_rows).sort_values("date", ascending=False)
    df.to_csv("my_faceit_matches.csv", index=False)
    print(f"Saved: {len(df)} matches → my_faceit_matches.csv")

if __name__ == "__main__":
    main()