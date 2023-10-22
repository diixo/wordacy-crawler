import re
import qq_parser as qq

s = "John's mom went there, but he wasn't c++, c#, .net, Q&A/Q-A, #nope i_t IT at-all'. So' she said: 'Where are& viix.co. !!' 'A a'"

def str_to_ngrams(str_line: str, stopwords: set()):
   
    line1 = str_line.replace(". ", "! ")
    line1 = re.sub('[!?;,:\[\]\(\)]', "!", line1)
    strips = [x.strip() for x in line1.split("!") if x !='']

    punctuation = " ©®-%$!?:,;\'\" @~&()=*_<=>{|}[/]^\\"
    result = []
    exclude = { "2d", "3d", "3g", "4g", "5g", "6g" }

    for item in strips:

        #words_list = [x.strip(" ") for x in item.split(" ") if (x != '')]
        #words_list = [x.strip(punctuation) if x not in self.dictionary else x for x in item.split(" ") if (x != '')]

        word_list = [x.strip(punctuation) for x in item.split(" ") if (x.strip(punctuation) != '')]
        tokens = []
        for w in word_list:
            wlow = w.lower()
            if (w == "IT") or (wlow == "c#") or (wlow in exclude):
                tokens.append(wlow)
            else:
                wlow = wlow.strip("#")
                if qq.is_word(wlow, stopwords):
                    tokens.append(wlow)

        if tokens: result.append(tokens)
    return result
