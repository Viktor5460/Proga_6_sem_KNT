notDivisibleBy4UpTo100 :: [Int]
notDivisibleBy4UpTo100 = [x | x <- [1..100], x `mod` 4 /= 0]
