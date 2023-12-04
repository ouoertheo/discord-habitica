import unittest
from  app.events import event_service


class TestEvent:
    type = "true_flag"
    def __init__(self, value: bool) -> None:
        self.value = value

class EventTest(unittest.IsolatedAsyncioTestCase):
    async def test_post_event(self):
        class FoodAsync:
            def __init__(self) -> None:
                self.true_flag = False
            async def set_true_flag(self, data:TestEvent):
                self.true_flag = data.value
        class FoodSync:
            def __init__(self) -> None:
                self.true_flag = False
            def set_true_flag(self, data:TestEvent):
                self.true_flag = data.value
        spam = FoodAsync()
        eggs = FoodSync()
        event_service.subscribe(TestEvent.type,spam.set_true_flag)
        event_service.subscribe(TestEvent.type,eggs.set_true_flag)
        await event_service.post_event(TestEvent(True))
        self.assertEqual(spam.true_flag, True)
        self.assertEqual(eggs.true_flag, True)