isProductOfThreeThreeDigitIntegers :: Integer -> Bool
isProductOfThreeThreeDigitIntegers n =
  existsForA td
  where
    td = [-999..-100] ++ [100..999]
    existsForA [] = False
    existsForA (a:as) = existsForB a td || existsForA as
    existsForB _ [] = False
    existsForB a (b:bs) =
      let p = a * b
      in if p /= 0 && n `mod` p == 0 && isThreeDigit (n `div` p)
           then True
           else existsForB a bs

    isThreeDigit x = abs x >= 100 && abs x <= 999
