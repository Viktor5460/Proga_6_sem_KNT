naturalNumberDivisors :: Integer -> [Integer]
naturalNumberDivisors n = [d | d <- [1..n], n `mod` d == 0]
