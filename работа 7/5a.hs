data FiniteField = FiniteField Integer Integer
  deriving (Eq)

instance Show FiniteField where
  show (FiniteField q x) = show x ++ " (mod " ++ show q ++ ")"

mkField :: Integer -> Integer -> FiniteField
mkField q x
  | q <= 1 = error "Field order must be greater than 1"
  | otherwise = FiniteField q (normalize q x)

addF :: FiniteField -> FiniteField -> FiniteField
addF (FiniteField q a) (FiniteField q2 b)
  | q /= q2 = error "Different field orders"
  | otherwise = FiniteField q (normalize q (a + b))

mulF :: FiniteField -> FiniteField -> FiniteField
mulF (FiniteField q a) (FiniteField q2 b)
  | q /= q2 = error "Different field orders"
  | otherwise = FiniteField q (normalize q (a * b))

negF :: FiniteField -> FiniteField
negF (FiniteField q a) = FiniteField q (normalize q (-a))

invF :: FiniteField -> FiniteField
invF (FiniteField q 0) = error "Zero has no inverse"
invF (FiniteField q a)
  | g /= 1 = error "Inverse does not exist for this element and order"
  | otherwise = FiniteField q (normalize q x)
  where
    (g, x, _) = extendedGCD a q

normalize :: Integer -> Integer -> Integer
normalize q x = ((x `mod` q) + q) `mod` q

extendedGCD :: Integer -> Integer -> (Integer, Integer, Integer)
extendedGCD a 0 = (abs a, signum a, 0)
extendedGCD a b = (g, y, x - (a `div` b) * y)
  where
    (g, x, y) = extendedGCD b (a `mod` b)
