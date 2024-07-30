
from thread_pool import ThreadPool


def main():
    processor = ThreadPool(max_workers=4)
    processor.start()

    for i in range(20):
        processor.add_data(f"data_{i}")


    while not processor.is_finished():
        pass
    processor.stop()


if __name__ == "__main__":
    main()
