from asyncio import current_task

import datetime

import asyncio
import aiohttp
from typing import List, Dict, Any

from itertools import batched

from db import DbSession, SwapiPeople, open_orm, close_orm

MAX_REQUESTS = 10

async def get_people(person_id: int, http_session: aiohttp.ClientSession):
    response = await http_session.get(f'https://www.swapi.tech/api/people/{person_id}')
    json_data = await response.json()
    return json_data

def extract_character_data(api_response: Dict[str, Any]) -> Dict[str,Any]:
    props = api_response['result']['properties']
    return {
        'id': int(api_response['result']['uid']),
        'birth_year': props.get('birth_year'),
        'eye_color': props.get('eye_color'),
        'gender': props.get('gender'),
        'hair_color': props.get('hair_color'),
        'homeworld': props.get('homeworld'),
        'mass': props.get('mass'),
        'name': props.get('name'),
        'skin_color': props.get('skin_color'),
    }

async def insert_results(results: List[Dict[str, Any]]):
    async with DbSession() as session:
        for people_dict in results:
            if people_dict:
                people_obj = SwapiPeople(
                    id=people_dict['id'],
                    name=people_dict['name'],
                    birth_year=people_dict['birth_year'],
                    eye_color=people_dict['eye_color'],
                    gender=people_dict['gender'],
                    hair_color=people_dict['hair_color'],
                    homeworld=people_dict['homeworld'],
                    mass=people_dict['mass'],
                    skin_color=people_dict['skin_color'],
                )
                session.add(people_obj)
        await session.commit()


async def get_total_people() -> int:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://www.swapi.tech/api/people/?page=1&limit=1') as response:
            if response.status == 200:
                data = await response.json()
                return data['total_records']
            return 0

async def main():
    await open_orm()
    total_people = await get_total_people()
    async with aiohttp.ClientSession() as http_session:
        insert_tasks = []
        for batch in batched(range (1, total_people + 1), MAX_REQUESTS):
            coros = [get_people(i, http_session) for i in batch]
            results = await asyncio.gather(*coros)

            extracted_data = [extract_character_data(r) for r in results if r]
            if extracted_data:
                task = asyncio.create_task(insert_results(extracted_data))
                insert_tasks.append(task)
        if insert_tasks:
            await asyncio.gather(*insert_tasks)
    await close_orm()



start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)


asyncio.run(main())






