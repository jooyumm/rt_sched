import requests
import json
import time
import argparse 

CITY = "Seoul"
API_KEY = "본인의 API 키" 

# 기본 실행 횟수 (고정값)
DEFAULT_NUM_RUNS = 1 

def task_weather_analysis():
    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    start_time = time.time()

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        city = data.get('name')
        main = data.get('main', {})
        temperature = main.get('temp')  # 섭씨로 변환된 온도
        humidity = main.get('humidity')
        weather = data.get('weather', [{}])[0].get('description')
        
        elapsed_time = (time.time() - start_time) * 1000  # 실행 시간 (ms)
        
        print(f"-----------------------------------------------")
        print(f"Execution Time : {elapsed_time:.3f} ms")

        print(f"ㄴ {city} Temperature: {temperature:.2f} °C")
        print(f"ㄴ {city} Humidity: {humidity}%")
        print(f"ㄴ {city} Weather: {weather.capitalize()}")
        
        print(f"-----------------------------------------------")
        
        return elapsed_time
    else:
        print(f"Error: Failed to fetch data (Status Code: {response.status_code})")
        return None

def calculate_average_time(num_runs):
    total_time = 0
    valid_runs = 0

    for i in range(num_runs):
        # Fetch and analyze data in one step
        elapsed_time = task_weather_analysis()
        if elapsed_time is not None:
            total_time += elapsed_time
            valid_runs += 1

    if valid_runs == 0:
        print(" [Error] No valid runs completed.")
        return

    average_time = total_time / valid_runs
    
    # print(f"Average execution time over {valid_runs} runs: {average_time:.3f} ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and analyze weather data multiple times, and calculate the average execution time.")
    parser.add_argument('--num_runs', type=int, default=DEFAULT_NUM_RUNS, help="Number of times to run the weather data fetching and analysis task. Default is 1.")

    args = parser.parse_args()

    # 평균 실행 시간 계산
    calculate_average_time(args.num_runs)
