maxOfAverages :: [[Int]] -> Double
maxOfAverages [] = 0
maxOfAverages (xs:xss) = bestAvg xs xss
  where
    bestAvg best [] = avg best
    bestAvg best (ys:yss) =
      if avg ys > avg best
        then bestAvg ys yss
        else bestAvg best yss

    avg ys = intToDouble (sum ys) / intToDouble (length ys)

    intToDouble n
      | n == 0 = 0
      | n > 0 = 1.0 + intToDouble (n - 1)
      | otherwise = - (intToDouble (-n))
