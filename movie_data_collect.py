# -*- coding: utf-8 -*-
"""movie_data_collect

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1k0zi9tmzCOj8PJ1cuCDJ_jpcNja-5WRe
"""

import requests
import time
import csv

API_KEY = 'KOBIS_API_KEY'

def get_movie_list(year, cur_page=1):
    url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieList.json"
    params = {
        'key': API_KEY,
        'openStartDt': year,
        'openEndDt': year,
        'curPage': cur_page,
        'itemPerPage': 100,
        'movieType': '장편'       # 단편영화 제외 (일일 API호출횟수가 제한되어있다)
    }
    response = requests.get(url, params=params)
    return response.json()

def get_movie_info(movieCd):
    url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/movie/searchMovieInfo.json"
    params = {
        'key': API_KEY,
        'movieCd': movieCd
    }
    response = requests.get(url, params=params)
    return response.json()

def collect_movies_and_actors(start_year=2015, end_year=2024):
    results = []
    for year in range(start_year, end_year + 1):
        print(f"data collect")
        cur_page = 1
        while True:
            movie_list = get_movie_list(year, cur_page)
            movies = movie_list.get('movieListResult', {}).get('movieList', [])
            if not movies:
                break
            for movie in movies:
                if movie.get('nationAlt') and '한국' not in movie['nationAlt']:
                    continue
                movieCd = movie['movieCd']
                movieNm = movie['movieNm']
                try:
                    movie_info = get_movie_info(movieCd)
                    movie_data = movie_info.get('movieInfoResult', {}).get('movieInfo', {})
                    actors = movie_data.get('actors', [])
                    genres = movie_data.get('genres', [])
                    actor_names = [actor['peopleNm'] for actor in actors if actor['peopleNm']]
                    genre_names = [genre['genreNm'] for genre in genres if genre['genreNm']]
                    if actor_names:
                        results.append({
                            'movieCd': movieCd,
                            'movieNm': movieNm,
                            'openYear': year,
                            'genres': genre_names,
                            'actors': actor_names
                        })
                    time.sleep(0.2)
                except Exception as e:
                    print(f"movie Cd {movieCd} error: {e}")
            cur_page += 1
            total_pages = (movie_list['movieListResult']['totCnt'] // 100) + 1
            if cur_page > total_pages:
                break
    return results

def save_to_csv(data, filename='movie_data.csv'):
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['movieCd', 'movieNm', 'openYear', 'genres', 'actorList'])
        for row in data:
            writer.writerow([
                row['movieCd'],
                row['movieNm'],
                row['openYear'],
                ';'.join(row['genres']),
                ';'.join(row['actors'])
            ])

if __name__ == "__main__":
    data = collect_movies_and_actors(2015, 2024)        # recent 10 years
    save_to_csv(data)
    print("csv saved")
