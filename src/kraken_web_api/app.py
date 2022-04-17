import asyncio
import logging

from kraken_web_api.websocket import WebSocket


def on_update():
    pass


class Runner:
    async def start(self):
        async with WebSocket(socket_log_level=logging.INFO) as self.client:
            task_subscribe = asyncio.create_task(self.client.subscribe_orders_book("ETH/BTC", 10, on_update))
            await task_subscribe
            # await asyncio.sleep(3)
            while True:
                await asyncio.sleep(0)
        # self.client = WebSocket(socket_log_level=logging.INFO)
        # task_connect_public = asyncio.create_task(self.client.subscribe_orders_book(on_update))
        # await task_connect_public
        # await asyncio.sleep(10)

    async def stop(self):
        await self.client.unsubscribe_all()
        await self.client._disconnect_all()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s  %(name)s  %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    runner = Runner()
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(runner.start())
    except KeyboardInterrupt:
        print("keyb interrupt")
        loop.run_until_complete(runner.stop())
