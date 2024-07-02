import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup as bs
import json
import random
import sys
import io
import queue
import threading
from media_sorter import load_films_with_ratings, load_sorted_films, save_sorted_films, update_ratings

class MediaSorterGUI:
    def __init__(self, root, films, sorted_films, sorted_films_filename):
        self.root = root
        self.root.title("Media Sorter")
        self.films = films
        self.sorted_films = sorted_films
        self.sorted_films_filename = sorted_films_filename
        self.current_films = list(films.keys())
        random.shuffle(self.current_films)
        self.film1 = None
        self.film2 = None
        self.left_image = None
        self.right_image = None
        self.comparison_queue = queue.Queue()  # Initialize the comparison queue
        self.create_widgets()
        self.ensure_sorted_films_initialized()
        self.preload_comparisons(3)  # Preload 3 comparisons initially
        self.load_initial_films()
        
    def load_initial_films(self):
        while self.comparison_queue.qsize() < 3:
            pass  # Wait until we have preloaded comparisons
        self.load_next_films()

    def ensure_sorted_films_initialized(self):
        for film in self.films:
            if film not in self.sorted_films:
                self.sorted_films[film] = self.films[film]

    def preload_comparisons(self, num_comparisons):
        def preload():
            for _ in range(num_comparisons):
                if len(self.current_films) < 2:
                    self.current_films = list(self.films.keys())
                    random.shuffle(self.current_films)
                film1 = self.current_films.pop()
                film2 = self.current_films.pop()
                left_image_data = self.fetch_image_data(film1)
                right_image_data = self.fetch_image_data(film2)
                self.comparison_queue.put((film1, film2, left_image_data, right_image_data))
        threading.Thread(target=preload).start()

    def fetch_image_data(self, film_title):
        url = f'https://letterboxd.com/film/{film_title.replace(" ", "-").lower()}/'
        print(f"Fetching image for {film_title} from {url}")
        r = requests.get(url)
        soup = bs(r.text, 'html.parser')
        script_w_data = soup.select_one('script[type="application/ld+json"]')
        json_obj = json.loads(script_w_data.text.split(' */')[1].split('/* ]]>')[0])
        image_url = json_obj['image']
        print(f"Image URL: {image_url}")
        response = requests.get(image_url)
        img_data = response.content
        return img_data

    def create_widgets(self):
        self.left_poster_label = tk.Label(self.root)
        self.left_poster_label.grid(row=0, column=0, padx=20, pady=20)

        self.vs_label = tk.Label(self.root, text="VS", font=("Helvetica", 24))
        self.vs_label.grid(row=0, column=1, padx=20, pady=20)

        self.right_poster_label = tk.Label(self.root)
        self.right_poster_label.grid(row=0, column=2, padx=20, pady=20)

        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=1, column=0, columnspan=3, pady=20)

        self.left_button = ttk.Button(self.button_frame, text="1", command=self.left_button_click)
        self.left_button.grid(row=0, column=0, padx=10)

        self.equal_button = ttk.Button(self.button_frame, text="Equal", command=self.equal_button_click)
        self.equal_button.grid(row=0, column=1, padx=10)

        self.right_button = ttk.Button(self.button_frame, text="2", command=self.right_button_click)
        self.right_button.grid(row=0, column=2, padx=10)

    def load_next_films(self):
        if not self.comparison_queue.empty():
            film1, film2, left_image_data, right_image_data = self.comparison_queue.get()
            left_image = Image.open(io.BytesIO(left_image_data))
            left_image = left_image.resize((200, 300), Image.LANCZOS)
            self.left_image = ImageTk.PhotoImage(left_image)
            
            right_image = Image.open(io.BytesIO(right_image_data))
            right_image = right_image.resize((200, 300), Image.LANCZOS)
            self.right_image = ImageTk.PhotoImage(right_image)

            self.film1, self.film2 = film1, film2
            self.left_poster_label.config(image=self.left_image)
            self.left_poster_label.image = self.left_image  # Keep a reference to avoid garbage collection
            self.right_poster_label.config(image=self.right_image)
            self.right_poster_label.image = self.right_image  # Keep a reference to avoid garbage collection
        
        self.preload_comparisons(1)  # Preload one more comparison

    def get_poster_image(self, film_title):
        url = f'https://letterboxd.com/film/{film_title.replace(" ", "-").lower()}/'
        # print(f"Fetching image for {film_title} from {url}")
        r = requests.get(url)
        soup = bs(r.text, 'html.parser')
        script_w_data = soup.select_one('script[type="application/ld+json"]')
        json_obj = json.loads(script_w_data.text.split(' */')[1].split('/* ]]>')[0])
        image_url = json_obj['image']
        # print(f"Image URL: {image_url}")
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((200, 300), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def left_button_click(self):
        update_ratings(self.sorted_films, self.film1, self.film2, 1)
        save_sorted_films(self.sorted_films, self.sorted_films_filename)
        self.load_next_films()

    def right_button_click(self):
        update_ratings(self.sorted_films, self.film1, self.film2, 0)
        save_sorted_films(self.sorted_films, self.sorted_films_filename)
        self.load_next_films()

    def equal_button_click(self):
        update_ratings(self.sorted_films, self.film1, self.film2, 0.5)
        save_sorted_films(self.sorted_films, self.sorted_films_filename)
        self.load_next_films()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python media_sorter_gui.py <username>")
        sys.exit(1)

    target_user = sys.argv[1]

    films_filename = f"{target_user}_films.txt"
    sorted_films_filename = f"sorted_{target_user}_films.txt"

    films = load_films_with_ratings(films_filename)
    sorted_films = load_sorted_films(sorted_films_filename)

    root = tk.Tk()
    app = MediaSorterGUI(root, films, sorted_films, sorted_films_filename)
    root.mainloop()