from aiokafka import AIOKafkaProducer

from app.database import Database
from starlette.requests import Request


def get_db_client(request: Request) -> Database:
    return request.app.state.db


def get_kafka_client(request: Request) -> AIOKafkaProducer:
    return request.app.state.event_producer
