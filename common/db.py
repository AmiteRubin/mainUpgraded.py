import asyncio
import logging
from pathlib import Path

from beanie import init_beanie
from motor.core import AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient


async def _get_mongo_client():
    """
    separate so it could be decorated, the reason were not also initiating in this function
    """
    logging.info('attempting to connect to mongodb')
    SSL_CA_CERTS = True
    # if SSL_CA_CERTS:
    client = AsyncIOMotorClient(
        'mongodb+srv://rubs:niyI7rni6CCuWAlc@5353.yvp6d4q.mongodb.net/?retryWrites=true&w=majority',
        # tlsCertificateKeyFile=str(Path(__file__).parent / 'X509-cert-6661849979066861196.pem'),
        uuidRepresentation="standard"
    )
    # else:
    #     client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_FULL_URL, uuidRepresentation="standard",
    #                                                     tlsAllowInvalidCertificates=True)

    await client.admin.command({'ping': 1})
    return client


async def init_db(
       documents, allow_index_dropping: bool = False
) -> tuple[list['Document'], 'AgnosticDatabase']:
    client = await _get_mongo_client()
    db: AgnosticDatabase = client['5353']
    db.get_io_loop = asyncio.get_event_loop
    await init_beanie(database=db, document_models=documents, allow_index_dropping=allow_index_dropping)
    logging.info('successfully connected to mongo')
    return documents, db
