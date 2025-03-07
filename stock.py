import requests
import time
import collections
from bs4 import BeautifulSoup
import argparse

# 기본 실행 횟수 (고정값)
DEFAULT_NUM_RUNS = 1 

def task_stock_analysis():
    start_time = time.time()
    url = "https://finance.naver.com/sise/sise_market_sum.naver"
    headers = {"User-Agent": "Mozilla/5.0"}  # User-Agent 설정 추가

    # 주식 데이터 크롤링
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f" [Error] Failed to fetch stock data (Status Code: {response.status_code})")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    stocks = [s.get_text(strip=True) for s in soup.select(".tah.p11")]
    
    if not stocks:
        print(" [Warning] No stock data found.")
        return None

    # 주식 이름 분석
    stopwords = {"종목", "현재", "시가", "종가", "등"}
    stock_count = collections.Counter()
    for stock in stocks:
        words = [word for word in stock.split() if word not in stopwords and len(word) > 1]
        stock_count.update(words)

    # 가장 많이 등장한 주식 항목 5개 출력
    most_common_stocks = stock_count.most_common(5)

    elapsed_time = (time.time() - start_time) * 1000  # 실행 시간 (ms)
    print(f"-----------------------------------------------")
    print(f"Execution Time : {elapsed_time:.3f} ms")
    print(f"ㄴ Most common stocks: {most_common_stocks}")
    print(f"-----------------------------------------------")

    return elapsed_time

def calculate_average_time(num_runs):
    total_time = 0
    valid_runs = 0

    for _ in range(num_runs):
        elapsed_time = task_stock_analysis()
        if elapsed_time is not None:
            total_time += elapsed_time
            valid_runs += 1

    if valid_runs == 0:
        print(" [Error] No valid runs completed.")
        return

    average_time = total_time / valid_runs
    # print(f"Average execution time over {valid_runs} runs: {average_time:.3f} ms")

if __name__ == "__main__":
    # argparse를 통해 num_runs 값을 가져오되, 기본값으로 1 사용
    parser = argparse.ArgumentParser(description="Run the stock analysis task multiple times and calculate the average time.")
    parser.add_argument('--num_runs', type=int, default=DEFAULT_NUM_RUNS, help="Number of times to run the stock analysis task. Default is 5.")
    
    args = parser.parse_args()

    # 평균 실행 시간 계산
    calculate_average_time(args.num_runs)