# Shared module (e.g., task_manager.py)
import threading
import queue


class TaskManager:
    """Класс для управления потоками программы"""

    def __init__(self):
        self.task_queue = queue.Queue()
        self.active_threads = 0
        self.running = True

    def add_task(self, target_func, args=()):
        """Add tasks to the queue and auto-start processing"""
        self.task_queue.put((target_func, args))
        if self.active_threads == 0:
            self._start_processing()

    def _start_processing(self):
        """Start worker threads"""
        thread = threading.Thread(target=self._worker, daemon=True)
        thread.start()

    def _worker(self):
        """Process tasks from the queue"""
        self.active_threads += 1
        while self.running and not self.task_queue.empty():
            func, args = self.task_queue.get()
            try:
                func(*args)  # Execute the task
            finally:
                self.task_queue.task_done()
        self.active_threads -= 1


# Global instance
task_manager = TaskManager()
