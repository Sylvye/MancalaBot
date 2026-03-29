import json
import time
from pathlib import Path
import Mancala


OUTPUT_FILE = Path("mancala_exec_data.jsonl")


def save_session(session, output_file=OUTPUT_FILE):
    with output_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(session) + "\n")


def main():
    print("Mancala data collection")
    print(f"Saving to: {OUTPUT_FILE.resolve()}")
    print("Play games normally. After each game, its timing data will be appended.\n")

    game_count = 0

    prompts = input("Show human-only prompts? (y/n): ").strip().lower()
    prompts = False if prompts == "n" else True
    keepPlayers = input("Keep players? (y/n): ").strip().lower()
    keepPlayers = True if keepPlayers == "y" else False
    maxGames = input("Max games? (int): ").strip().lower()
    maxGames = int(maxGames)
    if maxGames <= 0:
        maxGames = float("inf")

    p1 = None
    p2 = None

    while True:
        session = Mancala.main(p1=p1, p2=p2, doPrompts=prompts)

        session_record = {
            "timestamp": time.time(),
            "winner": session["winner"],
            "turns": session["turns"],
            "p1": session["p1"],
            "p2": session["p2"],
            "depth": session["depth"],
            "dynamic": session["dynamic"],
            "parallel": session["parallel"],
            "exec_time_data": session["exec_time_data"],
        }

        if keepPlayers:
            p1 = session["p1"]
            p2 = session["p2"]

        save_session(session_record)
        game_count += 1

        print(f"\nSaved game #{game_count} to {OUTPUT_FILE.name}")

        if game_count >= maxGames:
            break

        if prompts:
            again = input("Play another game? (y/n): ").strip().lower()
            if again != "y":
                break


if __name__ == "__main__":
    main()