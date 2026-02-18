import asyncio

from inventurgui.main import frontend, backend

warehouses, markdown = asyncio.run(backend())
frontend(warehouses, markdown)