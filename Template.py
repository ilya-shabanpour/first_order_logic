import sys
import tkinter
import tkinter.messagebox
from tkintermapview import TkinterMapView
from pyswip import Prolog
import pandas as pd


class App(tkinter.Tk):
    APP_NAME = "map_view_demo.py"
    WIDTH = 800
    HEIGHT = 1100  # This is now the initial size, not fixed. 750

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Text area and submit button combined row
        self.grid_rowconfigure(1, weight=4)  # Map row

        # Upper part: Text Area and Submit Button
        self.text_area = tkinter.Text(self, height=5)  # Reduced height for text area
        self.text_area.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="nsew")

        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        self.submit_button.grid(row=0, column=0, pady=(0, 10), padx=10,
                                sticky="se")  # Placed within the same cell as text area

        # Lower part: Map Widget
        self.map_widget = TkinterMapView(self)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        self.marker_list = []  # Keeping track of markers
        self.marker_path = None

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Text area can expand/contract.
        self.grid_rowconfigure(1, weight=0)  # Submit button row; doesn't need to expand.
        self.grid_rowconfigure(2, weight=3)  # Map gets the most space.

        # Upper part: Text Area and Submit Button
        self.text_area = tkinter.Text(self)
        self.text_area.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")

        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        self.submit_button.grid(row=1, column=0, pady=10, sticky="ew")

        # Lower part: Map Widget
        self.map_widget = TkinterMapView(self)
        self.map_widget.grid(row=2, column=0, sticky="nsew")

        self.marker_list = []  # Keeping track of markers

    def graph(self, prolog, result):

        for index, row in adj_matrix.iterrows():
            dest = row["Destinations"].lower()
            if dest == result:
                columns = list(adj_matrix.columns[row == 1])
                for column in columns:
                    column = column.lower()
                    prolog.assertz(f"directly_connected('{dest}', '{column}')")

                    for i, r in adj_matrix.iterrows():  # second level neighbors
                        dest2 = r["Destinations"].lower()
                        if dest2 == column:
                            cols = list(adj_matrix.columns[r == 1])
                            for col in cols:
                                col = col.lower()
                                prolog.assertz(f"directly_connected('{dest2}', '{col}')")
                            break
                break

        prolog.assertz("connected(X, Y) :- directly_connected(X, Y)")
        prolog.assertz("connected(X, Y) :- directly_connected(Y, X)")

    def check_connections(self, results):
        prolog.retractall("directly_connected(_,_)")
        prolog.retractall("connected(_,_)")

        for location in results:
            self.graph(prolog, location)

        paths = []
        for location in results:
            city_to_check = location
            curr_path = [location]
            cities_left = results.copy()
            cities_left.remove(location)
            paths.append([location])
            while len(cities_left) != 0:
                cities_connected_to_first = list(prolog.query(f"connected({city_to_check}, X)"))

                condition = False
                for c in cities_connected_to_first:
                    if c["X"] in cities_left:
                        condition = True
                        curr_path.append(c["X"])
                        cities_left.remove(c["X"])
                        city_to_check = c["X"]
                        paths.append(curr_path.copy())
                        break

                if condition:
                    continue

                for c in cities_connected_to_first:
                    city_to_check = c["X"]
                    cities_connected = list(prolog.query(f"connected({city_to_check}, X)"))
                    for c2 in cities_connected:
                        if c2["X"] in cities_left:
                            condition = True
                            curr_path.append(c["X"])
                            curr_path.append(c2["X"])
                            cities_left.remove(c2["X"])
                            city_to_check = c2["X"]
                            paths.append(curr_path.copy())
                            break
                    if condition:
                        break

                if not condition:
                    break

        best_path = self.find_best_path(paths, results)

        return best_path

    def find_best_path(self, paths, results):
        max_matches = 0
        best_path = []

        for path in paths:
            current_matches = sum(element in results for element in path)
            if current_matches == max_matches:
                best_path.append(path)
            elif current_matches > max_matches:
                best_path = [path]
                max_matches = current_matches

        min_len = 1000
        short_path = None
        for path in best_path:
            if len(path) < min_len:
                min_len = len(path)
                short_path = path

        return short_path

    def process_text(self):
        """Extract locations from the text area and mark them on the map."""
        text = self.text_area.get("1.0", "end-1c")  # Get text from text area
        extracted_features = self.extract_locations(text)  # Extract locations (you may use a more complex method here)

        # 4: create the query based on the extracted features of user description

        if len(extracted_features) == 0:
            tkinter.Tk().withdraw()
            tkinter.messagebox.showerror("Error", "We didn't find any specific tour!\n"
                                                  "Please describe your destination more detailed.")
            return

        result_list = []
        for key, value in extracted_features.items():
            query = f"{key}(City, '{value}')"
            result = list(prolog.query(query))
            temp_list = []
            for val in result:
                temp_list.append(val["City"])
            result_list.append(temp_list)
        if len(result_list) > 1:
            locations = set(result_list[0]).intersection(*result_list[1:])
        else:
            locations = result_list[0]
        print(locations)

        if len(locations) == 0:
            tkinter.Tk().withdraw()
            tkinter.messagebox.showerror("Error", "We didn't find any specific tour with your description!")
            return
        locations = list(locations)

        locations = self.check_connections(locations)
        print(locations)

        # 6: if the number of destinations is less than 6 mark and connect them

        if len(locations) > 5:
            tkinter.Tk().withdraw()
            tkinter.messagebox.showerror("Error", "We didn't find any specific tour!\n"
                                                  "Please describe your destination more detailed.")
        else:
            self.mark_locations(locations)

    def mark_locations(self, locations):
        """Mark extracted locations on the map."""
        for address in locations:
            marker = self.map_widget.set_address(address, marker=True)
            if marker:
                self.marker_list.append(marker)
        self.connect_marker()
        self.map_widget.set_zoom(1)  # Adjust as necessary, 1 is usually the most zoomed out

    def connect_marker(self):
        # print(self.marker_list)
        position_list = []

        for marker in self.marker_list:
            position_list.append(marker.position)

        if hasattr(self, 'marker_path') and self.marker_path is not None:
            self.map_widget.delete(self.marker_path)

        if len(position_list) > 0:
            self.marker_path = self.map_widget.set_path(position_list)

    def extract_locations(self, text):
        # 3: extract key features from user's description of destinations

        text = text.lower()
        text = text.replace(".", " ")
        text = text.replace(",", " ")
        text = text.replace("/", " ")
        words = text.split()
        key_features = {}
        for word in words:
            for key, value in unique_features.items():
                for feature in value:
                    if word == feature.lower():
                        key_features[key] = word

        return key_features


    def start(self):
        self.mainloop()


# 1: read destinations' descriptions from Destinations.csv and add them to the prolog knowledge base

prolog = Prolog()

adj_matrix = pd.read_csv("Adjacency_matrix.csv")

adj_matrix.at[37, "Destinations"] = "Washington_DC"
adj_matrix.at[73, "Destinations"] = "Xi_an"
adj_matrix.rename(columns={"Washington D.C.": "Washington_DC"}, inplace=True)
adj_matrix.rename(columns={"Xi'an": "Xi_an"}, inplace=True)

adj_matrix.replace(' ', '_', regex=True, inplace=True)
adj_matrix.columns = adj_matrix.columns.str.replace(' ', '_')

destinations = pd.read_csv("Destinations.csv")

destinations.at[37, "Destinations"] = "Washington DC"
destinations.at[73, "Destinations"] = "Xi_an"

destinations.replace(' ', '_', regex=True, inplace=True)
destinations.replace("Budget", "low-range", regex=True, inplace=True)

prolog.retractall("climate(_,_)")
prolog.retractall("budget(_,_)")
prolog.retractall("activity(_,_)")
prolog.retractall("demographic(_,_)")
prolog.retractall("duration(_,_)")
prolog.retractall("cuisine(_,_)")
prolog.retractall("history(_,_)")
prolog.retractall("natural_wonder(_,_)")
prolog.retractall("accommodation(_,_)")
prolog.retractall("language(_,_)")
prolog.retractall("region(_,_)")
prolog.retractall("my_destination(_)")
prolog.retractall("country(_,_)")

for row in destinations.iterrows():
    city = row[1]["Destinations"].lower()
    country = row[1]["country"].lower()
    region = row[1]["region"].lower()
    climate = row[1]["Climate"].lower()
    budget = row[1]["Budget"].lower()
    activity = row[1]["Activity"].lower()
    demographic = row[1]["Demographics"].lower()
    duration = row[1]["Duration"].lower()
    cuisine = row[1]["Cuisine"].lower()
    history = row[1]["History"].lower()
    natural_wonder = row[1]["Natural Wonder"].lower()
    accommodation = row[1]["Accommodation"].lower()
    language = row[1]["Language"].lower()

    prolog.assertz(f"my_destination('{city}')")
    prolog.assertz(f"country('{city}', '{country}')")
    prolog.assertz(f"region('{city}', '{region}')")
    prolog.assertz(f"climate('{city}', '{climate}')")
    prolog.assertz(f"budget('{city}', '{budget}')")
    prolog.assertz(f"activity('{city}', '{activity}')")
    prolog.assertz(f"demographic('{city}', '{demographic}')")
    prolog.assertz(f"duration('{city}', '{duration}')")
    prolog.assertz(f"cuisine('{city}', '{cuisine}')")
    prolog.assertz(f"history('{city}', '{history}')")
    prolog.assertz(f"natural_wonder('{city}', '{natural_wonder}')")
    prolog.assertz(f"accommodation('{city}', '{accommodation}')")
    prolog.assertz(f"language('{city}', '{language}')")


# 2: extract unique features from the Destinations.csv and save them in a dictionary

cities = destinations["Destinations"].unique()
countries = destinations["country"].unique()
regions = destinations["region"].unique()
climates = destinations["Climate"].unique()
budgets = destinations["Budget"].unique()
activities = destinations["Activity"].unique()
demographics = destinations["Demographics"].unique()
durations = destinations["Duration"].unique()
cuisines = destinations["Cuisine"].unique()
histories = destinations["History"].unique()
natural_wonder = destinations["Natural Wonder"].unique()
accommodation = destinations["Accommodation"].unique()
language = destinations["Language"].unique()

unique_features = {"my_destination": cities, "country": countries, "region": regions,
                   "climate": climates,"budget": budgets, "activity": activities,
                   "demographic": demographics, "duration": durations,
                   "cuisine": cuisines, "history": histories, "natural_wonder": natural_wonder,
                   "accommodation": accommodation, "language": language}

if __name__ == '__main__':
    app = App()
    app.start()
