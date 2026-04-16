allWordsStartWithSameLetter :: String -> Bool
allWordsStartWithSameLetter s = checkFirst (skipSpaces s)
  where

    skipSpaces [] = []
    skipSpaces (' ':cs) = skipSpaces cs
    skipSpaces cs = cs


    checkFirst [] = True
    checkFirst (c:cs) = checkSame c (skipWord cs)


    skipWord [] = []
    skipWord (' ':cs) = cs
    skipWord (_:cs) = skipWord cs


    checkSame _ [] = True
    checkSame c rest =
      let rest2 = skipSpaces rest
      in checkAfter c rest2

    checkAfter _ [] = True
    checkAfter c (c2:cs2) = c2 == c && checkSame c (skipWord cs2)
