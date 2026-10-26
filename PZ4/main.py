import asyncio #Event Loop, Семафоры и функцию gather
import json
from datetime import datetime
import aiohttp #запросы, не блокируя программу

API_URL_BRANDS = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"
API_URL_SPECS = "https://vpic.nhtsa.dot.gov/api/vehicles/GetMakeForManufacturer/Tesla?format=json"

semaphore = asyncio.Semaphore(3)

async def fetch_data(url, session): #корутина
    async with semaphore:  
        print(f"[ЗАПРОС] Отправка к {url[:10]}...")
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"[УСПЕХ] Данные получены от {url[:40]}...")
                    return data
                else:
                    print(f"[ОШИБКА] Статус {response.status} от {url}")
                    return None
        except asyncio.TimeoutError:
            print(f"[ТАЙМАУТ] Сервер не ответил за 5 сек: {url}")
            return None
        except Exception as e:
            print(f"[ОШИБКА] {e} при запросе {url}")
            return None

async def get_car_data():
    async with aiohttp.ClientSession() as session:
        task1 = fetch_data(API_URL_BRANDS, session)
        task2 = fetch_data(API_URL_SPECS, session)
        
        brands_data, specs_data = await asyncio.gather(task1, task2)
        
        return {
            "car_brands": brands_data,
            "car_specs": specs_data,
            "timestamp": datetime.now().isoformat()
        }

def save_data(data, filename="auto_data.json"):
    with open(filename, "a", encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False) + "\n")
    print(f"[СОХРАНЕНО] Запись добавлена в {filename}")

async def main():
    print("ПРОГРАММА СБОРА ДАННЫХ ОБ АВТОМОБИЛЯХ ЗАПУЩЕНА")
    while True:
        data = await get_car_data()
        
        if data["car_brands"] or data["car_specs"]:
            save_data(data)
        else:
            print("[ПРОПУСК] Нет данных для сохранения")
        
        print("Ожидание 10 минут до следующего запроса...\n")
        await asyncio.sleep(600)  

if __name__ == "__main__":
    asyncio.run(main()) #Event Loop