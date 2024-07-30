import threading
import queue
import time
import random


class Worker(threading.Thread):

    def __init__(self, data, stop_event, completion_callback):
        super().__init__()
        self.data = data
        self.stop_event = stop_event
        self.completion_callback = completion_callback
    
    def run(self):
        if self.stop_event.is_set():
            return
        # Обработка данных (замените этот метод на вашу логику)
        print(f"Started processing: {self.data} {self.name}")
        time.sleep(random.randint(1, 5))  # Имитация времени обработки

        # После завершения обработки уведомляем управляющий поток
        self.completion_callback(self)


class ThreadPool:

    def __init__(self, max_workers=4):
        self.data_queue = queue.Queue()
        self.max_workers = max_workers
        self.stop_event = threading.Event()
        self.active_threads = set()
        self.lock = threading.Lock()
    
    def manage_workers(self):
        while not self.stop_event.is_set() or not self.data_queue.empty() or self.active_threads:
            with self.lock:
                if len(self.active_threads) < self.max_workers and not self.data_queue.empty():
                    data = self.data_queue.get()
                    worker = Worker(data, self.stop_event, self.task_completed)
                    self.active_threads.add(worker)
                    worker.start()

            # Очистка завершенных потоков
            with self.lock:
                done_threads = [t for t in self.active_threads if not t.is_alive()]
                for thread in done_threads:
                    print("<< Clean-UP")
                    self.active_threads.remove(thread)
    
    def task_completed(self, thread):
        with self.lock:
            # Удаляем поток из активных потоков после завершения
            if thread in self.active_threads:
                print(f"<< {thread.name}")
                self.active_threads.remove(thread)
    
    def start(self):
        self.manager_thread = threading.Thread(target=self.manage_workers)
        self.manager_thread.start()
    
    def add_data(self, data):
        self.data_queue.put(data)

    def stop(self):
        self.stop_event.set()
        self.manager_thread.join()
        # Ждем завершения всех активных потоков
        with self.lock:
            for thread in self.active_threads:
                thread.join()


    def is_finished(self):
        with self.lock:
            # Проверяем, пустая ли очередь данных и нет ли активных потоков
            return self.data_queue.empty() and not self.active_threads
        
    def __del__(self):
        self.stop()
        print("<<__del__")


def main():
    processor = ThreadPool(max_workers=4)
    processor.start()

    for i in range(20):
        processor.add_data(f"data_{i}")

    # Завершение работы
    while not processor.is_finished():
        pass
    processor.stop()

if __name__ == "__main__":
    main()
