
from thread_pool import ThreadPool
from crawler_queue import CrawlerQueue


def main():
    url = "https://goo.lc"
    processor = ThreadPool(max_workers=4)
    processor.start()

    crawler = CrawlerQueue(delay=3, recursive=True)
    crawler.enqueue_url(url)
    processor.add_data(data=url, context=crawler)


    while not processor.is_finished():
        pass
    processor.stop()
    processor.save_json(filepath="test/demo_thread_pool.json")


if __name__ == "__main__":
    main()
