integerPoints2D :: [(Integer, Integer)]
integerPoints2D = concat [points d | d <- [0 ..]]
  where
    points d =
      [ (x, y)
      | x <- [-d .. d]
      , y <- [-d .. d]
      , abs x + abs y == d
      ]
