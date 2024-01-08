import re

# nltk.ngrams
def ngrams(content, n):
   ngramList = [tuple(content[i:i+n]) for i in range(len(content)-n+1)]
   return ngramList

def is_digit(word: str):
    w = re.sub(r'[$]?[-+]?[\d]*[.,\:]?[\d]+[ %\"\'\)\+]*', "", word)
    return not w

def is_complex_digit(word: str):
    w = re.sub(r'[$]?[-+]?[\d]*[.,\:]?[\d]+[ %\"\'\)\+]*[A-Za-z0-9]?', "", word)
    return not w

def is_date(value: str):
    # check formats: DD:MM:YYYY, DD.MM.YYYY, DD-MM-YYYY, DD/MM/YYYY
    pattern = r"^\d{1,2}(:|\.|\-|\/)\d{1,2}\1\d{4}$"
    return re.match(pattern, value) != None

def str_tokenize_words(s: str):
    s = re.findall("(\.?\w[\w'\.&-]*\w|\w\+*#?)", s)
    if s: return s
    return []

def is_word(word: str, stopwords=set()):
    #word = re.search("[\[\]\}\{=@\*]")
    if (re.sub("[A-Za-z0-9#\'\./_&+-]", "", word) == "") and len(word) > 1:
        if ((word not in stopwords) and not word.isdigit() and not is_complex_digit(word)) and not is_date(word):
            return True
    return False


def translate(txt: str):
    translation = {
        0xfffd: 0x0020, 0x00b7: 0x0020, 0xfeff: 0x0020, 0x2026: 0x0020, 0x2713: 0x0020, 0x205F: 0x0020, 0x202c: 0x0020, 
        0x202a: 0x0020, 0x200e: 0x0020, 0x200d: 0x0020, 0x200c: 0x0020, 0x200b: 0x0020, 0x2002: 0x0020, 0x2003: 0x0020, 
        0x2009: 0x0020, 0x2011: 0x002d, 0x2015: 0x002d, 0x201e: 0x0020, 0x2028: 0x0020, 0x2032: 0x0027, 0x2012: 0x002d, 
        0x0080: 0x0020, 0x0094: 0x0020, 0x009c: 0x0020, 0xFE0F: 0x0020, 0x200a: 0x0020, 0x202f: 0x0020, 0x2033: 0x0020, 
        0x2013: 0x0020, 0x00a0: 0x0020, 0x2705: 0x0020, 0x2714: 0x0020, # 0x2013: 0x002d
        0x2022: 0x0020, 0x2122: 0x0020, 0x2212: 0x002d, # 0x20ac: 0x00A4,
        0x201c: 0x0020, 0x201d: 0x0020, 0x021f: 0x0020, 0x0022: 0x0020, 0x2019: 0x0027, 0x2018: 0x0027, 0x201b: 0x0027, 
        0x0060: 0x0027, 0x00ab: 0x0020, 0x00bb: 0x0020, 0x2026: 0x002e, 0x2014: 0x0020 } # 0x2014: 0x002d

    txt = txt.translate(translation)
    #txt = re.sub("[^\u0020-\u022a]", " ", txt, re.UNICODE)
    txt = re.sub("[^\u0020-\u0500]", " ", txt, re.UNICODE)
    return txt.strip()


def str_to_ngrams(str_line: str, stopwords: set(), exclude = { "2d", "3d", "3g", "4g", "5g", "6g" }):
   
    line1 = str_line.replace(". ", "! ")
    line1 = re.sub('[!?;,:\[\]\(\)]', "!", line1)
    strips = [x.strip() for x in line1.split("!") if x !='']

    punctuation = " ©®-%$!?:,;\'\" @~&()=*_<=>{|}[/]^\\"
    result = []

    for item in strips:

        #words_list = [x.strip(" ") for x in item.split(" ") if (x != '')]
        #words_list = [x.strip(punctuation) if x not in self.dictionary else x for x in item.split(" ") if (x != '')]

        word_list = [x.strip(punctuation).rstrip(".") for x in item.split(" ") if (x.strip(punctuation) != '')]
        tokens = []
        for w in word_list:
            wlow = w.lower()
            if (w == "IT") or (wlow == "c#") or (wlow in exclude):
                tokens.append(wlow)
            else:
                wlow = wlow.strip("#")
                if is_word(wlow, stopwords):
                    tokens.append(wlow)

        if tokens: result.append(tokens)
    return result

##########################################

if __name__ == "__main__":

    print(is_date("00.01.2000"), is_date("00-01-2000"), is_date("00/01/2000"), is_date("00:01:2000"))

    d_test = [ "160", "160)", "160.0", "+160", "+160.0", "$0.2%", "$.225%", "$.225%", 
                "$.225%", "$.225%%", "$+.225%", "$,225%", "$:225%", "$+55%%%" ]
    for i in d_test: print(is_digit(i))

    for i in d_test: print(is_complex_digit(i + "v"))
    ################################################################################

    s = "John's mom went there, but he wasn't c++, c#, .net, Q&A/Q-A, #nope i_t IT at-all'. So' she said: 'Where are& viix.co. !!' 'A a'"
    
    list_1 = str_tokenize_words(s)

    print(list_1)

    print(str_to_ngrams(s, []))
