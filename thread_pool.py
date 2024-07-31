
import threading
import queue
import time
import random
import json
from pathlib import Path
from qq_crawler2 import Crawler2


class Worker(threading.Thread):

    def __init__(self, data, stop_event, completion_callback, context = None):
        super().__init__()
        self.data = data
        self.stop_event = stop_event
        self.completion_callback = completion_callback
        self.context = context
    
    def run(self):
        if self.stop_event.is_set():
            return
        # Обработка данных (замените этот метод на вашу логику)
        print(f"Started processing: {self.data} {self.name}")

        if self.context: self.context(self.data)

        # После завершения обработки уведомляем управляющий поток
        self.completion_callback(self)

    def get_data(self):
        return self.data


class ThreadPool:

    def __init__(self, max_workers=4):
        self.data_queue = queue.Queue()
        self.max_workers = max_workers
        self.stop_event = threading.Event()
        self.active_threads = set()
        self.lock = threading.Lock()
        
        self.urls = dict()


    def open_json(self, filepath:str):
        path = Path(filepath)
        if path.exists():
            fd = open(filepath, 'r', encoding='utf-8')
            self.urls = json.load(fd)
            for domain in self.urls.keys():
                self.urls[domain] = set(self.urls[domain])
        self.filepath = filepath


    def save_json(self, filepath=""):
        if not filepath:
            filepath = self.filepath

        result = dict()
        # считывать self.urls нужно под self.lock, так как запись в self.urls выполняется из другого потока
        with self.lock:
            for host in self.urls.keys():
                result[host] = sorted(self.urls[host])

        with open(filepath, 'w', encoding='utf-8') as fd:
            json.dump(result, fd, ensure_ascii=False, indent=3)

    
    def manage_workers(self):
        while not self.stop_event.is_set() or not self.data_queue.empty() or self.active_threads:
            with self.lock:
                if len(self.active_threads) < self.max_workers and not self.data_queue.empty():
                    data, context = self.data_queue.get()
                    worker = Worker(data, self.stop_event, self.task_completed, context=context)
                    self.active_threads.add(worker)
                    worker.start()

            # Очистка завершенных потоков
            with self.lock:
                done_threads = [t for t in self.active_threads if not t.is_alive()]
                for thread in done_threads:
                    print("<< Clean-UP")
                    self.active_threads.remove(thread)
    
    def task_completed(self, worker: Worker):
        with self.lock:
            if worker.context: self.merge(worker.context)

            # Удаляем поток из активных потоков после завершения
            if worker in self.active_threads:
                print(f"<< {worker.name}")
                self.active_threads.remove(worker)


    def merge(self, crawler: Crawler2):
        for hostname, urls in crawler.urls.items():
            host_urls = self.urls.get(hostname, set())
            host_urls.update(urls)
            self.urls[hostname] = host_urls
            

    def start(self):
        self.manager_thread = threading.Thread(target=self.manage_workers)
        self.manager_thread.start()
    
    def add_data(self, data, context=None):
        self.data_queue.put((data, context))

    def stop(self):
        self.stop_event.set()
        self.manager_thread.join()
        # Ждем завершения всех активных потоков
        with self.lock:
            for thread in self.active_threads:
                thread.join()


    def is_active(self):
        with self.lock:
            return not self.stop_event.is_set()

    def is_finished(self):
        with self.lock:
            # Проверяем, пустая ли очередь данных и нет ли активных потоков
            return self.data_queue.empty() and not self.active_threads
        
    def __del__(self):
        self.stop()
        #print("<<__del__")

