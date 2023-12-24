import asyncio

class TransactionManager:
    def __init__(self):
        self.transactions = {}
        self.transaction_id_counter = 0
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:
            transaction_id = self.transaction_id_counter
            self.transaction_id_counter += 1
            self.transactions[transaction_id] = []
            return Transaction(self, transaction_id)

    async def __aexit__(self, exc_type, exc, tb):
        pass  # You can add cleanup logic if needed

    def add_operation(self, transaction_id, operation_result):
        self.transactions[transaction_id].append(operation_result)

class Transaction:
    def __init__(self, manager, transaction_id):
        self.manager = manager
        self.transaction_id = transaction_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass  # You can add cleanup logic if needed

    def record_operation(self, operation_result):
        self.manager.add_operation(self.transaction_id, operation_result)

# Example usage
transact = TransactionManager()

async def other_code():
    # Some asynchronous operations
    await asyncio.sleep(1)
    return "Op1 Result"

async def main():
    async with transact as transaction:
        result_op1 = await other_code()

        # You can call other functions and their results will be automatically recorded in the transaction
        result_op2 = await other_code()
    print("taco")

if __name__ == "__main__":
    asyncio.run(main())
