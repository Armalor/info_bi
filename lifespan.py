from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiopg.sa import create_engine, Engine, SAConnection
import logging
from typing import Dict
from sshtunnel import SSHTunnelForwarder
from pprint import pprint

# Локальный импорт:
import sys
from os import path
__path__ = path.dirname(path.abspath(__file__))
sys.path.append(__path__)
from config import Config
# ~Локальный импорт


class Lifespan:
    """Не можем тащить engine в config: при попытке передачи такого конфига в процесс изготовления отчета,
    идет крах fastAPI, т.к. (скорее всего!) engine — асинхронный, а процесс-Reporter — нет
    """
    engines: Dict[str, Engine] = {}
    tunnels: Dict[str, SSHTunnelForwarder] = {}

    def __init__(self):
        self.logger = logging.getLogger("uvicorn.default")
        self.config = Config(__path__).config

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):

        for key, item in self.config.db.items():
            # continue

            db = self.config.db[key]["database"]
            host = self.config.db[key]["host"]
            ssh = self.config.db[key].get('ssh', None)

            if ssh and key not in Lifespan.tunnels:
                Lifespan.tunnels[key] = SSHTunnelForwarder((ssh['host'], ssh['port']),
                    ssh_username=ssh['user'],
                    ssh_password=ssh['password'],
                    remote_bind_address=(ssh['remote_bind_host'], ssh['remote_bind_port']),
                    local_bind_address=(ssh['local_bind_host'], ssh['local_bind_port'])
                )
                Lifespan.tunnels[key].start()

            async def on_connect(conn: SAConnection):
                self.logger.info(f'New connection to {db}@{host} established...')

            dsn = 'host={host} port={port} dbname={database} user={user} password={password}'.format(**item)
            Lifespan.engines[key]: Engine = await create_engine(dsn, minsize=1, maxsize=30, on_connect=on_connect)
            self.logger.info(f'Connection pool to key "{key}" - {db}@{host} - created!')

        yield

        for key, engine in Lifespan.engines.items():
            engine.close()
            db = self.config.db[key]["database"]
            host = self.config.db[key]["host"]
            self.logger.info(f'Connection pool to "{key}" - {db}@{host} - closed.')
            await engine.wait_closed()

    @classmethod
    def get_engine(cls, title='db_147_portal'):
        return cls.engines.get(title, None)
