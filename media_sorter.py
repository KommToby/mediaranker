import random
import sys

def star_rating_to_elo(star_rating):
    # Converts letterboxd star ratings to an ELO
    # Im using 2000 -> 1000 because those are more likely to work with an ELO system
    mapping = {
        "★★★★★": 2000,
        "★★★★½": 1900,
        "★★★★": 1800,
        "★★★½": 1700,
        "★★★": 1600,
        "★★½": 1500,
        "★★": 1400,
        "★½": 1300,
        "★": 1200,
        "½": 1100,
        "": 1000,
    }
    return mapping.get(star_rating.strip(), 1000)

# imagine the film is in a list where first is most preferred and last is least preferred
# We now also pass in what the function is now we use a GUI
def insert_film(film_list, film_title, comparison_func):
    # If the list doesnt exist, we can create a list of just the film by itself
    if not film_list:
        return [film_title]
    
    # Initialise both low and high values
    low, high = 0, len(film_list) - 1

    while low <= high:
        mid = (low + high) // 2
        res = comparison_func(film_title, film_list[mid])

        # New film is better
        if res == 1:
            high = mid - 1
        # Other film is better
        elif res == 2:
            low = mid + 1
        # Films are qual
        else:
            low = mid
            break
        
    # Logic for duplicates
    if film_title not in film_list:
        return film_list[:low] + [film_title] + film_list[low:]
    return film_list

# Initial ELO ratings for each film
def elo_rating(rating1, rating2, result):
    K = 32
    expected1 = 1 / (1 + 10 ** ((rating2 - rating1) / 400))
    expected2 = 1 / (1 + 10 ** ((rating1 - rating2) / 400))
    
    new_rating1 = rating1 + K * (result - expected1)
    new_rating2 = rating2 + K * ((1 - result) - expected2)
    
    return new_rating1, new_rating2

# Updating the ELO depending on chosen comparison
def update_ratings(films, film1, film2, result):
    # ELO initialisation in case they are missing
    # Assuming 2.5 stars because middle of the road
    if film1 not in films:
        films[film1] = 1500
    if film2 not in films:
        films[film2] = 1500
    
    rating1 = films[film1]
    rating2 = films[film2]
    
    if result == 1:
        new_rating1, new_rating2 = elo_rating(rating1, rating2, 1)
    elif result == 2:
        new_rating1, new_rating2 = elo_rating(rating1, rating2, 0)
    else:
        new_rating1, new_rating2 = elo_rating(rating1, rating2, 0.5)
    
    films[film1] = new_rating1
    films[film2] = new_rating2

def load_films_with_ratings(films_filename):
    films = {}
    with open(films_filename, "r", encoding="utf8") as f:
        for line in f:
            title, rating = line.strip().rsplit(" - ", 1)
            films[title] = star_rating_to_elo(rating)
    return films

def load_sorted_films(sorted_films_filename):
    try:
        with open(sorted_films_filename, "r", encoding="utf8") as f:
            films = {}
            for line in f:
                title, rating = line.strip().rsplit(" - ", 1)
                films[title] = float(rating)
            return films
    except FileNotFoundError:
        return {}
    
def save_sorted_films(films, sorted_films_filename):
    with open(sorted_films_filename, "w", encoding="utf8") as f:
        for film, rating in sorted(films.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{film} - {rating}\n")

def compare_films(f1, f2):
    print(f"Prefer:\n1. {f1}\n2. {f2}\n3. Equal")
    res = int(input())
    return res

def load_films(films_filmname):
    films = open(films_filmname, "r", encoding="utf8").readlines()
    films = [film.split(" - ")[0] for film in films]
    random.shuffle(films)
    return films

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python media-sorter.py <username>")
        sys.exit(1)

    target_user = sys.argv[1]

    films_filename = f"{target_user}_films.txt"
    sorted_films_filename = f"sorted_{target_user}_films.txt"

    films = load_films(films_filename)
    sorted_films = load_sorted_films(sorted_films_filename)
    
    for film1 in films:
        for film2 in films:
            if film1 != film2:
                result = compare_films(film1, film2)
                update_ratings(sorted_films, film1, film2, result)
                save_sorted_films(sorted_films, sorted_films_filename)