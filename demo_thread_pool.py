
from thread_pool import ThreadPool
from qq_crawler2 import Crawler2


def main():
    processor = ThreadPool(max_workers=4)
    processor.start()

    crawler = Crawler2(delay=3, recursive=True)
    processor.add_data("https://goo.lc", context=crawler)


    while not processor.is_finished():
        pass
    processor.stop()
    processor.save_json(filepath="test/demo_thread_pool.json")



if __name__ == "__main__":
    main()
