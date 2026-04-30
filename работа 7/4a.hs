data PrimeFactorNumber = PrimeFactorNumber Integer [(Integer, Int)]
  deriving (Eq)

instance Show PrimeFactorNumber where
  show n = show (toIntegerPF n)

fromIntegerPF :: Integer -> PrimeFactorNumber
fromIntegerPF 0 = PrimeFactorNumber 0 []
fromIntegerPF n = PrimeFactorNumber (signum n) (factorize (abs n) 2)

toIntegerPF :: PrimeFactorNumber -> Integer
toIntegerPF (PrimeFactorNumber 0 _) = 0
toIntegerPF (PrimeFactorNumber s fs) = s * product [p ^ e | (p, e) <- fs]

gcdPF :: PrimeFactorNumber -> PrimeFactorNumber -> PrimeFactorNumber
gcdPF (PrimeFactorNumber 0 _) b = absPF b
gcdPF a (PrimeFactorNumber 0 _) = absPF a
gcdPF (PrimeFactorNumber _ fa) (PrimeFactorNumber _ fb) =
  PrimeFactorNumber 1 (mergeMin fa fb)

lcmPF :: PrimeFactorNumber -> PrimeFactorNumber -> PrimeFactorNumber
lcmPF (PrimeFactorNumber 0 _) _ = PrimeFactorNumber 0 []
lcmPF _ (PrimeFactorNumber 0 _) = PrimeFactorNumber 0 []
lcmPF (PrimeFactorNumber _ fa) (PrimeFactorNumber _ fb) =
  PrimeFactorNumber 1 (mergeMax fa fb)

absPF :: PrimeFactorNumber -> PrimeFactorNumber
absPF (PrimeFactorNumber 0 _) = PrimeFactorNumber 0 []
absPF (PrimeFactorNumber _ fs) = PrimeFactorNumber 1 fs

factorize :: Integer -> Integer -> [(Integer, Int)]
factorize 1 _ = []
factorize n d
  | d * d > n = [(n, 1)]
  | n `mod` d == 0 = (d, multiplicity) : factorize reduced (d + 1)
  | otherwise = factorize n (d + 1)
  where
    (multiplicity, reduced) = extractPower n d 0

extractPower :: Integer -> Integer -> Int -> (Int, Integer)
extractPower n d k
  | n `mod` d == 0 = extractPower (n `div` d) d (k + 1)
  | otherwise = (k, n)

mergeMin :: [(Integer, Int)] -> [(Integer, Int)] -> [(Integer, Int)]
mergeMin [] _ = []
mergeMin _ [] = []
mergeMin ((pa, ea) : as) ((pb, eb) : bs)
  | pa == pb = (pa, min ea eb) : mergeMin as bs
  | pa < pb = mergeMin as ((pb, eb) : bs)
  | otherwise = mergeMin ((pa, ea) : as) bs

mergeMax :: [(Integer, Int)] -> [(Integer, Int)] -> [(Integer, Int)]
mergeMax [] bs = bs
mergeMax as [] = as
mergeMax ((pa, ea) : as) ((pb, eb) : bs)
  | pa == pb = (pa, max ea eb) : mergeMax as bs
  | pa < pb = (pa, ea) : mergeMax as ((pb, eb) : bs)
  | otherwise = (pb, eb) : mergeMax ((pa, ea) : as) bs
