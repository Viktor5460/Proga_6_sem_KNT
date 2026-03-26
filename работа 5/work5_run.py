import csv
import json
import random
import re
import subprocess
from collections import Counter
from itertools import combinations
from pathlib import Path


# Основные пути внутри папки работы.
ROOT = Path(__file__).resolve().parent
PROLOG_FILE = ROOT / "prolog_maximal_coalitions.pl"
FACTS_FILE = ROOT / "played_facts.pl"
REPORT_FILE = ROOT / "report.txt"
SOURCE_GAMES_FILE = ROOT / "games_data.py"

# Главные параметры эксперимента.
PLAYERS_COUNT = 10
MATCHES_COUNT = 20
GAMES_COUNT = 5
SEED = 41 # для генерации случайных чисел (для возможности воспроизведения результатов)


def load_games():
    # Читаем встроенный CSV из локального файла.
    text = SOURCE_GAMES_FILE.read_text(encoding="utf-8")
    m = re.search(r'CSV_DATA\s*=\s*r?"""(.*?)"""', text, flags=re.DOTALL)
    if not m:
        raise RuntimeError("Не найден CSV_DATA в games_data.py")
    reader = csv.reader(m.group(1).strip().splitlines(), delimiter=",", quotechar='"')

    all_games = []
    for row in reader:
        if len(row) < 4:
            continue
        name = row[0].strip()
        min_p = int(row[2])
        max_p = int(row[3])
        if min_p > 0 and max_p >= min_p:
            all_games.append((name, min_p, max_p))

    if len(all_games) < 1:
        raise RuntimeError("Список игр пуст")
    if GAMES_COUNT > len(all_games):
        raise RuntimeError(f"GAMES_COUNT={GAMES_COUNT} больше доступного количества игр ({len(all_games)})")

    return all_games


def generate_dataset():
    # Фиксированный seed => воспроизводимые данные между запусками.
    rng = random.Random(SEED)
    players = [f"player_{i:03d}" for i in range(1, PLAYERS_COUNT + 1)]
    all_games = load_games()

    # Если GAMES_COUNT меньше общего числа игр, берется случайная подвыборка.
    if GAMES_COUNT == len(all_games):
        games = list(all_games)
    else:
        games = rng.sample(all_games, GAMES_COUNT)

    game_counter = Counter()
    player_counter = Counter()
    edges = set()

    for _ in range(MATCHES_COUNT):
        # Для каждой партии случайно выбираем игру и допустимое число участников.
        game_name, min_p, max_p = rng.choice(games)
        k = rng.randint(min_p, max_p)
        selected = rng.sample(players, k)

        game_counter[game_name] += 1
        player_counter.update(selected)

        # Каждая пара участников одной партии формирует ребро played(A,B).
        for a, b in combinations(sorted(selected), 2):
            edges.add((a, b))

    return edges, game_counter, player_counter, games, players


def write_facts(edges):
    # Пишем факты в формате Prolog: played('player_001','player_007').
    lines = [f"played('{a}', '{b}')." for a, b in sorted(edges)]
    FACTS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_prolog():
    # Запускаем SWI-Prolog как внешний процесс и просим вернуть JSON.
    cmd = [
        "swipl",
        "-q",
        "-s",
        str(PROLOG_FILE),
        "-s",
        str(FACTS_FILE),
        "-g",
        "maximal_coalitions_json(Json), writeln(Json)",
        "-t",
        "halt",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"Ошибка Prolog:\n{proc.stderr}")

    out = proc.stdout.strip()
    # В stdout может быть служебный текст, поэтому извлекаем JSON по скобкам.
    i, j = out.find("{"), out.rfind("}")
    if i == -1 or j == -1 or j <= i:
        raise RuntimeError(f"Не удалось извлечь JSON:\n{out}")
    return json.loads(out[i : j + 1])


def format_report(
    games: list[tuple[str, int, int]],
    players: list[str],
    game_counter: Counter,
    player_counter: Counter,
    coalitions: list[list[str]],
) -> str:
    # Сортируем коалиции: сначала большие, затем лексикографически.
    sorted_coalitions = sorted(coalitions, key=lambda c: (-len(c), c))
    sorted_games = sorted(g[0] for g in games)
    sorted_players = sorted(players)

    most_game, most_game_count = game_counter.most_common(1)[0]
    most_player, most_player_count = player_counter.most_common(1)[0]

    lines: list[str] = []
    lines.append("ОТЧЕТ РАБОТА 5")
    lines.append("")
    lines.append(f"Количество партий: {MATCHES_COUNT}")
    lines.append(f"Количество игр: {len(games)}")
    lines.append(f"Количество игроков: {len(players)}")
    lines.append("")
    lines.append(f"Игрок, который сыграл больше всего партий: {most_player} ({most_player_count})")
    lines.append(f"Игра, в которую сыграли больше всего партий: {most_game} ({most_game_count})")
    lines.append("")
    lines.append("СПИСОК ВСЕХ МАКСИМАЛЬНЫХ КОАЛИЦИЙ (сначала больше по размеру):")
    lines.append(f"Всего коалиций: {len(sorted_coalitions)}")
    for idx, coalition in enumerate(sorted_coalitions, 1):
        lines.append(f"{idx}. size={len(coalition)} -> {', '.join(coalition)}")
    lines.append("")
    lines.append("СПИСОК ВСЕХ ИГР:")
    for idx, game_name in enumerate(sorted_games, 1):
        lines.append(f"{idx}. {game_name}")
    lines.append("")
    lines.append("СПИСОК ВСЕХ ИГРОКОВ:")
    for idx, player_id in enumerate(sorted_players, 1):
        lines.append(f"{idx}. {player_id}")
    lines.append("")
    return "\n".join(lines)


def main():
    # 1) Генерация данных и статистики
    edges, game_counter, player_counter, games, players = generate_dataset()
    # 2) Передача графа в Prolog
    write_facts(edges)
    result = run_prolog()

    coalitions = result.get("coalitions", [])

    # 3) Сборка и запись итогового отчета
    report_text = format_report(games, players, game_counter, player_counter, coalitions)
    REPORT_FILE.write_text(report_text, encoding="utf-8")
    print(f"Готово. Отчет сохранен в файл: {REPORT_FILE.name}")
    print(f"Факты Prolog сохранены в файл: {FACTS_FILE.name}")


if __name__ == "__main__":
    main()
