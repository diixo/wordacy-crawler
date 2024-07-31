
from thread_pool import ThreadPool
from qq_crawler2 import Crawler2


def main():
    url = "https://goo.lc"
    processor = ThreadPool(max_workers=4)
    processor.start()

    crawler = Crawler2(delay=3, recursive=True)
    crawler.enqueue_url(url)
    processor.add_data(data=url, context=crawler)


    while not processor.is_finished():
        pass
    processor.stop()
    processor.save_json(filepath="test/demo_thread_pool.json")


if __name__ == "__main__":
    main()
