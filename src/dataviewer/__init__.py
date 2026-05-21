import asyncio

from dataviewer.main import main, load_data

warehouses = asyncio.run(load_data())
main(warehouses)
