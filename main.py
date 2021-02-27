k = 10
PPM_Model = [{} for i in range(k + 1)]
PPM_Model[0] = {'': {}}
result = [[]]
list_of_strings = []
PPM_Trie = {}


def getProb(char, subtable, drop):
    esc = 0
    sumcount = 0

    for key in subtable.keys():
        if key not in drop:
            sumcount += subtable[key]
            esc += 1

    if char == '<esc>':
        count = esc
    else:
        count = subtable[char]

    sumcount += esc
    if sumcount == 0 and count == 0:
        return 1
    return float(count / sumcount)


def match(char, string_):
    drop = []
    Foundmatch = False

    for i in range(len(string_) + 1):
        context = string_[i:]

        if context in PPM_Model[len(context)]:
            if char in PPM_Model[len(context)][context]:
                result.append([char])
                Foundmatch = True
                break
            else:
                if getProb('<esc>', PPM_Model[len(context)][context], drop) == .5 and result[-1][0] != '<esc>':
                    result.append(['<esc>'])

                for l in PPM_Model[len(context)][context].keys():
                    drop.append(l)

    if not Foundmatch:
        result.append([char])

    for i in range(len(string_) + 1):
        context = string_[i:]

        if context not in PPM_Model[len(context)]:
            PPM_Model[len(context)][context] = {}

        if char in PPM_Model[len(context)][context]:
            count = PPM_Model[len(context)][context][char]
            count += 1
        else:
            count = 1
        PPM_Model[len(context)][context][char] = count


def Preprocessing(path):
    print("Started pre-processing...")

    file = open('./Models/TrainingData', 'r')
    newtext = file.read()
    file.close()

    for i in range(len(newtext)):
        match(newtext[i], (newtext[0:i] if i <= k else newtext[i - k:i]))

    # HERE I WILL CREATE THE MODEL
    # I GENERATE THE PPM TRIE, and TRAVERSE IT
    # Then we filter the model to find the strings that apply best to our plain text
    # Then we pass the filtered results to the arithmetic coder.

    loop = 0

    while loop < k + 1:

        for char0 in PPM_Model[loop]:
            for char in PPM_Model[loop][char0]:
                key = char0 + char
                value = PPM_Model[loop][char0][char]
                PPM_Trie[key] = value

        loop += 1

    for loop in range(256):
        if chr(loop) not in PPM_Trie:
            PPM_Trie[chr(loop)] = 1

    print("Done pre-processing...")
    print("Searching for the largest matches of your file and our model.")
    file = open(path, 'r')
    text = file.read()
    file.close()

    # Matching by sliding window of variable size

    # window = 0
    # print("indexing...")
    # while window < len(text):
    #     windowSize = k
    #     while windowSize > 0:
    #
    #         if windowSize + window <= len(text):
    #             if text[window:(window + windowSize)] in model:
    #                 list_of_strings.append(text[window:(window + windowSize)])
    #                 break
    #         windowSize -= 1
    #     if windowSize == 0:
    #         break
    #
    #     window = window + windowSize

    # NOW I WILL FOLLOW THE TRIE TO SEE HOW MANY LARGEST STRINGS I CAN PUT TOGETHER BY FOLLOWING THE PPM MODEL
    # The purpose of doing it this way instead of a sliding window is that its computationally less expensive.
    # The encoder already has the full model, with all possible combinations and their probabilities, we are just computing it for the text to be encoded.

    character_index = 0

    while character_index < len(text):
        path_ = ''
        char0 = text[character_index]

        loop = 0
        while loop < k + 1:

            if char0 in PPM_Model[loop][path_]:
                path_ += char0
                loop += 1
                if loop + character_index < len(text):
                    char0 = text[character_index + loop]
                else:
                    break
            else:
                break
        character_index += loop
        list_of_strings.append(path_)

    print("Done Matching, Encoding now!")


def encode(MatchedStrings, minModel, fullRange):
    MatchedStrings.append('ø')
    L = 0
    H = 2 ** 32
    ranges = []
    ranges.append((H // 2))
    ranges.append((ranges[0] // 2))

    rescaleDepth = 0
    bitStream = []

    for string_ in MatchedStrings:

        freq = minModel[string_][0]
        upperBound = minModel[string_][1]
        lowerBound = upperBound - freq

        _range = H - L
        H = L + _range * upperBound // fullRange
        L = L + _range * lowerBound // fullRange

        needToRescale = True
        while needToRescale:
            if H < ranges[0]:
                bitStream.append(0)
                bitStream += [1] * rescaleDepth
                rescaleDepth = 0
                L *= 2
                H *= 2
            elif L >= ranges[0]:
                bitStream.append(1)
                bitStream += [0] * rescaleDepth
                rescaleDepth = 0
                L = 2 * (L - ranges[0])
                H = 2 * (H - ranges[0])
            elif L >= ranges[1] and H < 3 * ranges[1]:
                rescaleDepth += 1
                L = 2 * (L - ranges[1])
                H = 2 * (H - ranges[1])
            else:
                needToRescale = not needToRescale
    rescaleDepth += 1
    if L <= ranges[1]:
        bitStream.append(0)
        bitStream += [1] * rescaleDepth
    else:
        bitStream.append(1)
        bitStream += [0] * rescaleDepth

    return bitStream


def decode(bitStream, minModel, fullRange):
    prob = 0
    lastBitLoc = 1
    message = []

    L = 0
    H = (2 ** 32)
    ranges = []
    ranges.append((H // 2))
    ranges.append((ranges[0] // 2))

    while lastBitLoc <= 32 and lastBitLoc <= len(bitStream):
        if bitStream[lastBitLoc - 1] == 1:
            prob = prob + 2 ** (32 - lastBitLoc)
        lastBitLoc += 1

    flag = True

    while flag:

        for symbol in minModel:

            upperBound = minModel[symbol][1]
            lowerBound = upperBound - minModel[symbol][0]
            Range = H - L
            H_ = L + Range * upperBound // fullRange
            L_ = L + Range * lowerBound // fullRange

            if L_ <= prob < H_:
                if symbol == 'ø':
                    flag = not flag
                else:
                    message.append(symbol)
                    L = L_
                    H = H_
                break

        needToRescale = True
        while needToRescale:
            if H < ranges[0]:
                L *= 2
                H *= 2
                prob *= 2

                if lastBitLoc <= len(bitStream):
                    prob += bitStream[lastBitLoc - 1]
                    lastBitLoc += 1

            elif L >= ranges[0]:
                L = 2 * (L - ranges[0])
                H = 2 * (H - ranges[0])
                prob = 2 * (prob - ranges[0])
                if lastBitLoc <= len(bitStream):
                    prob += bitStream[lastBitLoc - 1]
                    lastBitLoc += 1
            elif L >= ranges[1] and H < 3 * ranges[1]:
                L = 2 * (L - ranges[1])
                H = 2 * (H - ranges[1])
                prob = 2 * (prob - ranges[1])
                if lastBitLoc <= len(bitStream):
                    prob += bitStream[lastBitLoc - 1]
                    lastBitLoc += 1
            else:
                needToRescale = not needToRescale

    return message
