import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_history = {}  # тип: Dict[str, deque]

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        # Очищаємо старі таймстампи для користувача
        if user_id not in self.user_history:
            return
        dq = self.user_history[user_id]
        while dq and dq[0] <= current_time - self.window_size:
            dq.popleft()
        # Видаляємо користувача, якщо немає повідомлень
        if not dq:
            del self.user_history[user_id]

    def can_send_message(self, user_id: str) -> bool:
        now = time.time()
        self._cleanup_window(user_id, now)
        dq = self.user_history.get(user_id, deque())
        return len(dq) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        now = time.time()
        self._cleanup_window(user_id, now)
        dq = self.user_history.get(user_id)
        if dq is None:
            dq = deque()
            self.user_history[user_id] = dq
        if len(dq) < self.max_requests:
            dq.append(now)
            return True
        return False

    def time_until_next_allowed(self, user_id: str) -> float:
        now = time.time()
        self._cleanup_window(user_id, now)
        dq = self.user_history.get(user_id)
        if dq is None or len(dq) < self.max_requests:
            return 0.0
        # Повертаємо час, до якого повідомлення є дозволене
        return max(0.0, dq[0] + self.window_size - now)

# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
