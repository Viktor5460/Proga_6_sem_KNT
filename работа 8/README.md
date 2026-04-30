# Работа 8 

Реализована структура данных **бинарное дерево поиска**
для проекта BoardGameAdvisor. 

## Что в папке

- `src/BoardGame/BST.hs` — реализация структуры и операций;
- `app/Main.hs` — консольное приложение для демонстрации;
- `test/Main.hs` — тесты;


## Что умеет программа

- добавить игру: `add <id> <title_no_spaces> <minPlayers> <durationMin> <rating>`
- найти игру по рейтингу: `find <rating>`
- удалить игру по рейтингу: `del <rating>`
- вывести все игры по возрастанию ключа: `print`
- показать параметры дерева: `stats`
- подсказка: `help`
- выход: `exit`

## Запуск

Через Stack:

```bash
stack runghc -- app/Main.hs
stack runghc -- -isrc test/Main.hs
```





