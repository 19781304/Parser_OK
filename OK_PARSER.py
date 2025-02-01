import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

class OKParser:
    def __init__(self, profile_url):
        self.profile_url = profile_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_page(self, url):
        """Загружает страницу по URL"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка загрузки страницы: {e}")

    def get_bookmarks_url(self):
        """Строит URL страницы закладок"""
        
        return f"{self.profile_url}/bookmarks"

    def parse_bookmarks(self, html):
        """Парсинг закладок"""
        if not html:
            print("Ошибка: html-код не передан")
            return {}

        soup = BeautifulSoup(html, "html.parser")
        data = {}

        try:
            bookmarks_section = soup.find("div", class_="tico")
            if bookmarks_section:
                bookmarks = bookmarks_section.find_all("a")
                data["bookmarks"] = [bookmark.text.strip() for bookmark in bookmarks]
            else:
                data["bookmarks"] = []
        except Exception as e:
            print(f"Ошибка парсинга закладок: {e}")
            data["bookmarks"] = []

        return data

    def parse_games(self, html):
        """Парсит список игр"""
        soup = BeautifulSoup(html, "html.parser")
        games = []

        try:
            games_section = soup.find_all("div", class_="games-card")  
            for game in games_section:
                try:
                    game_name = game.find("div", class_="games-title").text.strip()
                    play_frequency = game.find("div", class_="games-frequency").text.strip()
                    games.append({"name": game_name, "frequency": play_frequency})
                except AttributeError:
                    print("Некоторые данные об игре отсутствуют. Пропускаем.")
        except Exception as e:
            print(f"Ошибка парсинга игр: {e}")

        return games

    def save_data(self, data, output_format="json", filename="output"):
        """Сохраняет данные в указанный формат"""
        try:
            if output_format == "json":
                with open(f"{filename}.json", "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            elif output_format == "csv":
                df = pd.DataFrame(data["games"])
                df.to_csv(f"{filename}.csv", index=False)
            elif output_format == "excel":
                df = pd.DataFrame(data["games"])
                df.to_excel(f"{filename}.xlsx", index=False)
            else:
                raise ValueError("Неподдерживаемый формат сохранения!")
            print(f"Данные сохранены в файл {filename}.{output_format}")
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")


def main():
    profile_url = "https://ok.ru/profile/470895515911"
    parser = OKParser(profile_url)

    # пустой словарь
    profile_data = {}

    print(f"Загрузка профиля: {profile_url}...")
    try:
        html = parser.fetch_page(profile_url)
        print("HTML-код профиля успешно загружен.")
    except Exception as e:
        print(f"Ошибка загрузки профиля: {e}")
        return

    #  URL страницы закладок 
    bookmarks_url = parser.get_bookmarks_url()
    print(f"Страница закладок: {bookmarks_url}")

    try:
        bookmarks_html = parser.fetch_page("https://ok.ru/bookmarks")
        profile_data["bookmarks"] = parser.parse_bookmarks(bookmarks_html)
        print(json.dumps(profile_data["bookmarks"], indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка загрузки страницы закладок: {e}")

    print("Переход на страницу с играми...")
    try:
        games_html = parser.fetch_page("https://ok.ru/vitrine")
        print("HTML-код страницы игр успешно загружен.")
        profile_data["games"] = parser.parse_games(games_html)
        print(json.dumps(profile_data["games"], indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка работы со страницей игр: {e}")

    print("Сохранение данных...")
    if profile_data:  
        parser.save_data(profile_data, output_format="json", filename="user_data")
        print("Парсинг завершен.")
    else:
        print("Нет данных для сохранения.")


if __name__ == "__main__":
    main()

