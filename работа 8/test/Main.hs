module Main where

import BoardGame.BST

main :: IO ()
main = do
  putStrLn "Тесты для работы 8 (BST):"
  run "insert + inorder sort" testInsertSorted
  run "find existing" testFindExisting
  run "find missing" testFindMissing
  run "delete" testDelete

run :: String -> Bool -> IO ()
run name ok =
  putStrLn $ name ++ ": " ++ if ok then "OK" else "FAIL"

g1, g2, g3 :: Game
g1 = Game 1 "A" 2 30 6.8
g2 = Game 2 "B" 2 40 8.2
g3 = Game 3 "C" 4 60 7.5

baseTree :: Tree Game
baseTree = fromList [g1, g2, g3]

testInsertSorted :: Bool
testInsertSorted =
  map avgRating (inorder baseTree) == [6.8, 7.5, 8.2]

testFindExisting :: Bool
testFindExisting =
  case findGameByRating 7.5 baseTree of
    Just g -> gameId g == 3
    Nothing -> False

testFindMissing :: Bool
testFindMissing =
  findGameByRating 9.9 baseTree == Nothing

testDelete :: Bool
testDelete =
  let t2 = deleteGameByRating 7.5 baseTree
  in map avgRating (inorder t2) == [6.8, 8.2]
