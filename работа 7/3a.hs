fractionApproximations :: Integer -> Integer -> [Double]
fractionApproximations _ 0 = error "Denominator must be non-zero"
fractionApproximations num den = [roundTo decimals value | decimals <- [1 ..]]
  where
    value = fromIntegral num / fromIntegral den

    roundTo digits x =
      fromIntegral (round (x * scale digits)) / scale digits

    scale digits = fromIntegral (10 ^ digits) :: Double
