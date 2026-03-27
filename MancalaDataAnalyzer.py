import json
from pathlib import Path
import matplotlib.pyplot as plt


INPUT_FILE = Path("mancala_exec_data.jsonl")


def load_sessions(path=INPUT_FILE):
    sessions = []
    if not path.exists():
        print(f"No data file found: {path}")
        return sessions

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                sessions.append(json.loads(line))

    return sessions


def flatten_exec_data(sessions):
    data = []
    for session in sessions:
        for row in session.get("exec_time_data", []):
            if len(row) == 3:
                complexity, serial, parallel = row
                data.append((complexity, serial, parallel))
    return data


def estimate_threshold(data, window=12, required_fraction=0.75):
    data = sorted(data, key=lambda x: x[0])
    if len(data) < window:
        return None

    for i in range(len(data) - window + 1):
        chunk = data[i:i + window]
        wins = sum(1 for _, s, p in chunk if p < s)
        if wins / window >= required_fraction:
            return chunk[0][0]

    return None


def plot_exec_time_data(data):
    if not data:
        print("No execution data found.")
        return

    data = sorted(data, key=lambda x: x[0])

    complexities = [x[0] for x in data]
    serial = [x[1] for x in data]
    parallel = [x[2] for x in data]
    delta = [p - s for _, s, p in data]
    ratio = [s / p if p > 0 else float("inf") for _, s, p in data]

    threshold = estimate_threshold(data)

    # 1. Raw times
    fig = plt.figure(figsize=(10, 6))
    plt.scatter(complexities, serial, label="Serial", alpha=0.6)
    plt.scatter(complexities, parallel, label="Parallel", alpha=0.6)
    if threshold is not None:
        plt.axvline(threshold, linestyle="--", label=f"Threshold ≈ {threshold:.0f}")
    plt.xlabel("Complexity")
    plt.ylabel("Execution time (s)")
    plt.title("Serial vs Parallel Time by Complexity")
    plt.legend()
    plt.grid(True)
    plt.xscale("log")
    plt.yscale("log")
    plt.show()
    plt.close(fig)

    # 2. Difference
    fig = plt.figure(figsize=(10, 6))
    plt.scatter(complexities, delta, alpha=0.6)
    plt.axhline(0, linestyle="--")
    if threshold is not None:
        plt.axvline(threshold, linestyle="--")
    plt.xlabel("Complexity")
    plt.ylabel("Parallel - Serial time (s)")
    plt.title("Parallel Advantage by Complexity")
    plt.grid(True)
    plt.xscale("log")
    plt.show()
    plt.close(fig)

    # 3. Ratio
    fig = plt.figure(figsize=(10, 6))
    plt.scatter(complexities, ratio, alpha=0.6)
    plt.axhline(1, linestyle="--")
    if threshold is not None:
        plt.axvline(threshold, linestyle="--")
    plt.xlabel("Complexity")
    plt.ylabel("Serial / Parallel")
    plt.title("Parallel Speedup Ratio by Complexity")
    plt.grid(True)
    plt.xscale("log")
    plt.show()
    plt.close(fig)

    if threshold is None:
        print("No stable threshold found yet.")
    else:
        print(f"Estimated threshold: {threshold:.0f}")


def main():
    sessions = load_sessions()
    print(f"Loaded {len(sessions)} saved game sessions.")

    data = flatten_exec_data(sessions)
    print(f"Loaded {len(data)} timing samples.")

    plot_exec_time_data(data)


if __name__ == "__main__":
    main()