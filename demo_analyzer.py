
from qq_analyzer import Analyzer, ReversePaginator
from qq_crawler2 import Crawler2



def test_url_to_dataset():
   url = "https://allainews.com/news"

   crawler = Crawler2()
   crawler.enqueue_url(url)
   crawler.set_filter(url,
   [
      "/terms/", 
      "/privacy/", 
      "/accounts/", 
      "/filtered/", 
      "/videos/", 
      "/feed/", 
      "/topic/",
      "/source/",
      "/news/feed",
      "/term",
      "/about",
      "/podcasts",
      "/sources.md"
      ])
   crawler.run()

   ###########################
   urls = crawler.get_urls(url)

   analyzer = Analyzer()
   analyzer.open_json("storage/allainews-news.json")

   #analyzer.learn_file("template/keywords.html")

   print(f">> [Analyzer] :{len(analyzer.content.get('headings', dict()))}")
   for u in urls:
      if analyzer.learn_url(u, hhh_mask=["h1", "H1"]):
         print(f"[Analyzer] ...on [{len(urls)}]: {u}")
         time.sleep(2.0)
   analyzer.save_json()
   print(f"<< [Analyzer] :{len(analyzer.content.get('headings', dict()))}")

   exit(0)
   ####################### analyze keywords #######################
   stopwords = load_stopwords()

   prediction = Prediction()
   keywords = analyzer.content.get("keywords", list())
   content = analyzer.content.get("headings", dict())

   for string in content.keys():
      string = qq.translate(string)
      ngrams = qq.str_to_ngrams(string, stopwords)
      for tokens in ngrams:
         prediction.add_tokens(tokens)


   result = dict()
   for sentence in keywords:
      tokens = qq.str_tokenize_words(sentence)
      sz = len(tokens)
      grams = tuple(tokens[0:sz])

      count = 0
      if sz == 1:
         count = prediction.unigrams_freq_dict.get(grams, count)
      if sz == 2:
         count = prediction.bigrams_freq_dict.get(grams, count)
      if sz == 3:
         count = prediction.trigrams_freq_dict.get(grams, count) 

      if count > 0: result[sentence] = count

   print(f"keywords.sz={len(keywords)}, result.sz={len(result)}")



def test_dataset():
    u1 = "https://pythonexamples.org/"
    u2 = "https://kotlinandroid.org/"
    u3 = "https://www.javatpoint.com/"
    u4 = "http://neevo.net/"
    #u5 = "https://www.geeksforgeeks.org/generative-adversarial-network-gan/"
    #u5 = "https://javascriptcode.org/"
    #u5 = "https://www.javatpoint.com/python-variables"
    #u5 = "https://www.programiz.com/r"

    analyzer = Analyzer()
    #analyzer.learn_file('process/techopedia-train-db-v5.data')
    analyzer.open_json("./storage/_data.json")
    analyzer.learn_file('template/template.html')
    analyzer.learn_url(u1)
    analyzer.learn_url(u2)
    analyzer.learn_url(u3)
    analyzer.learn_url(u4)
    analyzer.save_json()


def test_aixploria():
    crawler = Crawler2(delay=3, recursive=False)
    crawler.open_hostnames("db-hostnames.json")

    crawler.enqueue_url("https://www.aixploria.com/en")

    crawler.enqueue_url("https://www.aixploria.com/en/category/3d-model/" , 5)
    crawler.enqueue_url("https://www.aixploria.com/en/category/ai-chat-assistant/", 3)
    crawler.enqueue_url("https://www.aixploria.com/en/category/ai-detection-en/", 4)
    crawler.enqueue_url("https://www.aixploria.com/en/category/ia-useful/", 3)

    crawler.enqueue_url("https://www.aixploria.com/en/category/amazing/", 10)
    crawler.enqueue_url("https://www.aixploria.com/en/category/art-en/", 11)
    crawler.enqueue_url("https://www.aixploria.com/en/category/assistant-code-en/", 5)
    crawler.enqueue_url("https://www.aixploria.com/en/category/audio-editing/", 4)

    crawler.enqueue_url("https://www.aixploria.com/en/category/ai-autonomous/", 3)
    crawler.enqueue_url("https://www.aixploria.com/en/category/avatars-en/", 5)
    crawler.enqueue_url("https://www.aixploria.com/en/category/business-study/", 13)
    crawler.enqueue_url("https://www.aixploria.com/en/category/chatbot-ai/", 9)

    crawler.enqueue_url("https://www.aixploria.com/en/category/dating-relationships-ai/", 2)
    crawler.enqueue_url("https://www.aixploria.com/en/category/developer-tools/", 8)
    crawler.enqueue_url("https://www.aixploria.com/en/category/e-commerce-en/", 7)
    crawler.enqueue_url("https://www.aixploria.com/en/category/e-mail-en/", 5)

    crawler.enqueue_url("https://www.aixploria.com/en/category/education-en/" , 16)
    crawler.enqueue_url("https://www.aixploria.com/en/category/extensions-chatgpt/", 8)
    crawler.enqueue_url("https://www.aixploria.com/en/category/face-swap-deepfake-en/", 2)
    crawler.enqueue_url("https://www.aixploria.com/en/category/fashion-en/", 2)

    crawler.enqueue_url("https://www.aixploria.com/en/category/featured-en/", 3)
    crawler.enqueue_url("https://www.aixploria.com/en/category/files-spreadsheets/", 6)
    crawler.enqueue_url("https://www.aixploria.com/en/category/finance-en/", 5)
    crawler.enqueue_url("https://www.aixploria.com/en/category/games-en/", 4)

    crawler.enqueue_url("https://www.aixploria.com/en/category/github-project-ai/", 7)
    crawler.enqueue_url("https://www.aixploria.com/en/category/healthcare/", 3)
    crawler.enqueue_url("https://www.aixploria.com/en/category/human-resources-ai/", 6)
    crawler.enqueue_url("https://www.aixploria.com/en/category/image-editing/", 12)

    crawler.enqueue_url("https://www.aixploria.com/en/category/image-ai-en/", 15)
    crawler.enqueue_url("https://www.aixploria.com/en/category/imminent-release/", 8)
    crawler.enqueue_url("https://www.aixploria.com/en/category/last-ai-en/", 124)
    crawler.enqueue_url("https://www.aixploria.com/en/category/legal-assistants/", 2)

    crawler.enqueue_url("https://www.aixploria.com/en/category/life-assistants/", 16)
    crawler.enqueue_url("https://www.aixploria.com/en/category/llm-model-ai-en/", 5)
    crawler.enqueue_url("https://www.aixploria.com/en/category/logo-creation/", 2)
    crawler.enqueue_url("https://www.aixploria.com/en/category/marketing-ai/", 8)

    crawler.enqueue_url("https://www.aixploria.com/en/category/memory-en/", 2)
    crawler.enqueue_url("https://www.aixploria.com/en/category/music/", 7)
    crawler.enqueue_url("https://www.aixploria.com/en/category/no-code-en/", 9)
    crawler.enqueue_url("https://www.aixploria.com/en/category/popular-ai-tools/", 5)

    crawler.enqueue_url("https://www.aixploria.com/en/category/presentation-en/", 2)
    crawler.enqueue_url("https://www.aixploria.com/en/category/productivity-en/", 19)
    crawler.enqueue_url("https://www.aixploria.com/en/category/prompts-help/", 6)
    crawler.enqueue_url("https://www.aixploria.com/en/category/real-estate/", 3)

    crawler.enqueue_url("https://www.aixploria.com/en/category/research-science-en/", 4)
    crawler.enqueue_url("https://www.aixploria.com/en/category/robots-devices-ai/", 1)
    crawler.enqueue_url("https://www.aixploria.com/en/category/search-engine/", 5)
    crawler.enqueue_url("https://www.aixploria.com/en/category/social-assistants-en/", 11)

    crawler.enqueue_url("https://www.aixploria.com/en/category/storytelling-generator/", 4)
    crawler.enqueue_url("https://www.aixploria.com/en/category/ai-summarizer/", 6)
    crawler.enqueue_url("https://www.aixploria.com/en/category/ai-text-generators/", 6)
    crawler.enqueue_url("https://www.aixploria.com/en/category/voice-reading/", 5)

    crawler.enqueue_url("https://www.aixploria.com/en/category/text-to-video-en/", 3)
    crawler.enqueue_url("https://www.aixploria.com/en/category/transcriber/", 6)
    crawler.enqueue_url("https://www.aixploria.com/en/category/translation-ai/", 3)
    crawler.enqueue_url("https://www.aixploria.com/en/category/travel/", 3)
    crawler.enqueue_url("https://www.aixploria.com/en/category/video-edition/", 8)
    crawler.enqueue_url("https://www.aixploria.com/en/category/video-generators/", 9)
    crawler.enqueue_url("https://www.aixploria.com/en/category/ai-voice-cloning/", 2)
    crawler.enqueue_url("https://www.aixploria.com/en/category/websites-ai/", 7)
    crawler.enqueue_url("https://www.aixploria.com/en/category/writing-web-seo/", 11)

    #crawler.run()
    #crawler.save_hostnames("db-hostnames.json")

    indexing = list(range(6))
    paginator = ReversePaginator(indexing, 5)

    print(paginator.get_page(1))


def test_opentools_ai():
    crawler = Crawler2(delay=3, recursive=True)
    crawler.open_hostnames("db-hostnames_v2.json")
    crawler.open_json("db-urls_v2.json")

    crawler.enqueue_url("https://topai.tools")
    crawler.run()
    crawler.save_hostnames("db-hostnames_v2.json")
    crawler.save_json("db-urls_v2.json")


if __name__ == "__main__":
    #test_url_to_dataset()
    #test_with_ssl()
    #test_dataset()

    #test_aixploria()
    test_opentools_ai()

