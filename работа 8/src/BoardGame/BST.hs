module BoardGame.BST
  ( Game(..)
  , Tree(..)
  , emptyTree
  , insertGame
  , findGameByRating
  , deleteGameByRating
  , fromList
  , inorder
  , size
  , height
  ) where

-- Модель данных из проекта по настольным играм.
data Game = Game
  { gameId :: Int
  , title :: String
  , minPlayers :: Int
  , durationMin :: Int
  , avgRating :: Double
  } deriving (Eq, Show)

instance Ord Game where
  compare a b = compare (avgRating a, gameId a) (avgRating b, gameId b)

data Tree a
  = Empty
  | Node (Tree a) a (Tree a)
  deriving (Eq, Show)

emptyTree :: Tree a
emptyTree = Empty

insertGame :: Game -> Tree Game -> Tree Game
insertGame x Empty = Node Empty x Empty
insertGame x (Node l v r)
  | x < v = Node (insertGame x l) v r
  | x > v = Node l v (insertGame x r)
  | otherwise = Node l x r

findGameByRating :: Double -> Tree Game -> Maybe Game
findGameByRating _ Empty = Nothing
findGameByRating rating (Node l v r)
  | rating < avgRating v = findGameByRating rating l
  | rating > avgRating v = findGameByRating rating r
  | otherwise = Just v

deleteGameByRating :: Double -> Tree Game -> Tree Game
deleteGameByRating _ Empty = Empty
deleteGameByRating rating (Node l v r)
  | rating < avgRating v = Node (deleteGameByRating rating l) v r
  | rating > avgRating v = Node l v (deleteGameByRating rating r)
  | otherwise = deleteCurrentNode l r

fromList :: [Game] -> Tree Game
fromList = foldr insertGame emptyTree

inorder :: Tree a -> [a]
inorder Empty = []
inorder (Node l v r) = inorder l ++ [v] ++ inorder r

size :: Tree a -> Int
size Empty = 0
size (Node l _ r) = 1 + size l + size r

height :: Tree a -> Int
height Empty = 0
height (Node l _ r) = 1 + max (height l) (height r)

-- Удаление узла бинарного дерева поиска.
deleteCurrentNode :: Tree Game -> Tree Game -> Tree Game
deleteCurrentNode Empty r = r
deleteCurrentNode l Empty = l
deleteCurrentNode l r =
  let successor = minNode r
  in Node l successor (deleteGameByRating (avgRating successor) r)

minNode :: Tree Game -> Game
minNode Empty = error "minNode: empty tree"
minNode (Node Empty v _) = v
minNode (Node l _ _) = minNode l
