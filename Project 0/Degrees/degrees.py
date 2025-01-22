import csv
import sys
from util import Node, StackFrontier, QueueFrontier

# Dictionaries for data storage
names = {}  # Maps names to sets of corresponding person_ids
people = {}  # Maps person_ids to dictionaries with details like name, birth year, and movies
movies = {}  # Maps movie_ids to dictionaries with details like title, year, and stars


def load_data(directory):
    """
    Load people, movies, and stars data from CSV files into memory.
    """
    import os
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"Current directory: {current_directory}")

    # Load people data
    with open(f"{directory}/people.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            person_id = row["id"]
            name = row["name"].lower()
            people[person_id] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set(),
            }
            if name not in names:
                names[name] = {person_id}
            else:
                names[name].add(person_id)

    # Load movies data
    with open(f"{directory}/movies.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set(),
            }

    # Load stars data
    with open(f"{directory}/stars.csv", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                person_id = row["person_id"]
                movie_id = row["movie_id"]
                people[person_id]["movies"].add(movie_id)
                movies[movie_id]["stars"].add(person_id)
            except KeyError:
                continue


def main():
    """
    Main program to determine the shortest path between two actors.
    """
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    # Find the shortest path
    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Finds the shortest path of (movie_id, person_id) pairs connecting source to target.

    Returns:
        List of tuples (movie_id, person_id) if a path exists, otherwise None.
    """
    if source == target:
        return []

    frontier = QueueFrontier()
    frontier.add(Node(state=source, parent=None, action=None))
    visited = set()

    while not frontier.empty():
        current_node = frontier.remove()
        visited.add(current_node.state)

        for movie_id, person_id in neighbors_for_person(current_node.state):
            if person_id in visited or frontier.contains_state(person_id):
                continue
            child_node = Node(state=person_id, parent=current_node, action=movie_id)

            if child_node.state == target:
                path = []
                while child_node.parent is not None:
                    path.append((child_node.action, child_node.state))
                    child_node = child_node.parent
                path.reverse()
                return path

            frontier.add(child_node)

    return None


def person_id_for_name(name):
    """
    Resolves the IMDB id for a person's name.

    Handles ambiguous names by prompting the user.
    """
    person_ids = list(names.get(name.lower(), set()))
    if not person_ids:
        return None
    if len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            print(f"ID: {person_id}, Name: {person['name']}, Birth: {person['birth']}")
        try:
            chosen_id = input("Intended Person ID: ")
            if chosen_id in person_ids:
                return chosen_id
        except ValueError:
            pass
        return None
    return person_ids[0]


def neighbors_for_person(person_id):
    """
    Gets all (movie_id, person_id) pairs for co-stars of a given person.
    """
    neighbors = set()
    for movie_id in people[person_id]["movies"]:
        for co_star in movies[movie_id]["stars"]:
            neighbors.add((movie_id, co_star))
    return neighbors


if __name__ == "__main__":
    main()
