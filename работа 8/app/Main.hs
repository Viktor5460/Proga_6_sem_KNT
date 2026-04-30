module Main where

import BoardGame.BST
import Data.List (intercalate)
import Data.Maybe (fromMaybe)

sampleGames :: [Game]
sampleGames =
  [ Game 1 "Carcassonne" 2 45 7.4
  , Game 2 "Terraforming Mars" 1 120 8.3
  , Game 3 "Catan" 3 90 7.1
  , Game 4 "Pandemic" 2 60 7.6
  , Game 5 "Ticket to Ride" 2 60 7.5
  ]

main :: IO ()
main = do
  putStrLn "Лабораторная работа 8: простое бинарное дерево поиска"
  putStrLn "Предметная область: настольные игры"
  putStrLn "Команды: add, find, del, print, stats, demo, help, exit"
  repl (fromList sampleGames)

repl :: Tree Game -> IO ()
repl tree = do
  putStr "> "
  line <- getLine
  case words line of
    ["exit"] -> putStrLn "Завершено."
    ["help"] -> do
      putStrLn "add <id> <title_no_spaces> <minPlayers> <durationMin> <rating>"
      putStrLn "find <rating>"
      putStrLn "del <rating>"
      putStrLn "print"
      putStrLn "stats"
      putStrLn "demo"
      repl tree
    ["add", gid, t, p, d, r] ->
      let game = Game (read gid) t (read p) (read d) (read r)
      in do
        putStrLn "Игра добавлена."
        repl (insertGame game tree)
    ["find", r] -> do
      let result = findGameByRating (read r) tree
      putStrLn $ maybe "Не найдено." formatGame result
      repl tree
    ["del", r] -> do
      putStrLn "Удаление выполнено (если ключ существовал)."
      repl (deleteGameByRating (read r) tree)
    ["print"] -> do
      mapM_ (putStrLn . formatGame) (inorder tree)
      repl tree
    ["stats"] -> do
      putStrLn $ "Количество узлов: " ++ show (size tree)
      putStrLn $ "Высота дерева: " ++ show (height tree)
      repl tree
    ["demo"] -> do
      putStrLn "Текущие значения (inorder):"
      mapM_ (putStrLn . formatGame) (inorder tree)
      repl tree
    _ -> do
      putStrLn "Неизвестная команда. Введите help."
      repl tree

formatGame :: Game -> String
formatGame g =
  intercalate " | "
    [ "id=" ++ show (gameId g)
    , "title=" ++ title g
    , "players=" ++ show (minPlayers g)
    , "duration=" ++ show (durationMin g) ++ "m"
    , "rating=" ++ show (avgRating g)
    ]
