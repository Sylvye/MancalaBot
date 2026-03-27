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

    while True:
        session = Mancala.main()

        session_record = {
            "timestamp": time.time(),
            "winner": session["winner"],
            "turns": session["turns"],
            "player": session["player"],
            "bot": session["bot"],
            "depth": session["depth"],
            "dynamic": session["dynamic"],
            "parallel": session["parallel"],
            "exec_time_data": session["exec_time_data"],
        }

        save_session(session_record)
        game_count += 1

        print(f"\nSaved game #{game_count} to {OUTPUT_FILE.name}")

        again = input("Play another game? (y/n): ").strip().lower()
        if again != "y":
            break


if __name__ == "__main__":
    main()