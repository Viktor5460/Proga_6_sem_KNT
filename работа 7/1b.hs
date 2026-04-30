harmonicPartialSums :: [Double]
harmonicPartialSums = tail (scanl (+) 0 terms)
  where
    terms = [1.0 / fromIntegral n | n <- [1 ..]]
