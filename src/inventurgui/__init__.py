import asyncio

from inventurgui.main import main, load_data

warehouses, wiki = asyncio.run(load_data())
main(warehouses, wiki)
