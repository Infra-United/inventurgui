import asyncio

from inventurgui.io.load_data import load_data
from inventurgui.main import main

warehouses, pages, wiki = asyncio.run(load_data())
main(warehouses, pages, wiki)
