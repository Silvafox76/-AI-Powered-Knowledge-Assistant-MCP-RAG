
import queue
import threading
import time

class IngestionTaskQueue:
    def __init__(self, ingestion_manager):
        self.ingestion_manager = ingestion_manager
        self.task_queue = queue.Queue()
        self.workers = []
        self.running = False

    def add_task(self, file_path: str, file_type: str):
        self.task_queue.put((file_path, file_type))

    def _worker(self):
        while self.running:
            try:
                file_path, file_type = self.task_queue.get(timeout=1)
                print(f"Processing ingestion task: {file_path} ({file_type})")
                self.ingestion_manager.ingest_document(file_path, file_type)
                self.task_queue.task_done()
            except queue.Empty:
                time.sleep(0.1) # Small delay to prevent busy-waiting
            except Exception as e:
                print(f"Error processing ingestion task: {e}")
                self.task_queue.task_done() # Mark as done even on error to prevent blocking

    def start_workers(self, num_workers=2):
        if not self.running:
            self.running = True
            for _ in range(num_workers):
                worker = threading.Thread(target=self._worker)
                worker.daemon = True  # Allow main program to exit even if workers are running
                worker.start()
                self.workers.append(worker)
            print(f"Started {num_workers} ingestion workers.")

    def stop_workers(self):
        if self.running:
            self.running = False
            for worker in self.workers:
                worker.join(timeout=5) # Give workers some time to finish current tasks
            self.workers = []
            print("Stopped ingestion workers.")

if __name__ == "__main__":
    # This block is for testing the task queue independently
    class MockIngestionManager:
        def ingest_document(self, file_path, file_type):
            print(f"Mocking ingestion of {file_path} ({file_type})")
            time.sleep(0.5) # Simulate work

    mock_manager = MockIngestionManager()
    task_queue = IngestionTaskQueue(mock_manager)

    task_queue.start_workers(num_workers=1)

    task_queue.add_task("doc1.pdf", "pdf")
    task_queue.add_task("notes.txt", "txt")
    task_queue.add_task("report.docx", "docx")

    # Give some time for tasks to be processed
    time.sleep(3)

    task_queue.stop_workers()
    print("Task queue test complete.")


