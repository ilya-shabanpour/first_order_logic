import sys
import tkinter
import tkinter.messagebox
from tkintermapview import TkinterMapView
from pyswip import Prolog
import pandas as pd
import spacy


class App(tkinter.Tk):

    APP_NAME = "map_view_demo.py"
    WIDTH = 800
    HEIGHT = 750  # This is now the initial size, not fixed.

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
        self.submit_button.grid(row=0, column=0, pady=(0, 10), padx=10, sticky="se")  # Placed within the same cell as text area

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

    def check_connections(self, results):
        print('result2 ', results)
        locations = []
        for result in results:
            city  = result["City"]
            locations.append(city)
            # TODO 5: create the knowledgebase of the city and its connected destinations using Adjacency_matrix.csv


        return locations

    def process_text(self):
        """Extract locations from the text area and mark them on the map."""
        text = self.text_area.get("1.0", "end-1c")  # Get text from text area
        locations = self.extract_locations(text)  # Extract locations (you may use a more complex method here)


        # TODO 4: create the query based on the extracted features of user desciption 
        ################################################################################################
        query = "destination(City,_, _, _, low, _, _, _, _, _, _, _, _)"
        results = list(prolog.query(query))
        print(results)
        locations = self.check_connections(results)
        # TODO 6: if the number of destinations is less than 6 mark and connect them 
        ################################################################################################
        print(locations)
        locations = ['mexico_city','rome' ,'brasilia']
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
        print(self.marker_list)
        position_list = []

        for marker in self.marker_list:
            position_list.append(marker.position)

        if hasattr(self, 'marker_path') and self.marker_path is not None:
            self.map_widget.delete(self.marker_path)

        if len(position_list) > 0:
            self.marker_path = self.map_widget.set_path(position_list)

    def extract_locations(self, text):
        """Extract locations from text. A placeholder for more complex logic."""
        # Placeholder: Assuming each line in the text contains a single location name
        # TODO 3: extract key features from user's description of destinations

        words = text.split()
        key_features = {}
        for word in words:
            for key, value in unique_features.items():
                for feature in value:
                    if word == feature.lower():
                        key_features[key] = word


        print(key_features)



        ################################################################################################

        return [line.strip() for line in text.split('\n') if line.strip()]

    def start(self):
        self.mainloop()

# 1: read destinations' descriptions from Destinations.csv and add them to the prolog knowledge base
################################################################################################
# STEP1: Define the knowledge base of illnesses and their symptoms

prolog = Prolog()
destinations = pd.read_csv("Destinations.csv")

# for row_num in range(103):
#     if " " in destinations.iloc[row_num]['Destinations']:

destinations.replace(' ', '_', regex=True, inplace=True)


destinations.at[37, "Destinations"] = "Washington DC"
destinations.at[73, "Destinations"] = "Xi_an"

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

# query = "cuisine(City, asian)"
# results = list(prolog.query(query))
# for result in results:
#     current_city = result["City"]
#     if len(list(prolog.query(f"budget('{current_city}', low)"))) != 0:
#         print(current_city)



# TODO 2: extract unique features from the Destinations.csv and save them in a dictionary
################################################################################################

cities = destinations["Destinations"].unique()
countries = destinations["country"].unique()
regions = destinations["region"].unique()
climates = destinations["Climate"].unique()
budgets = destinations["Budget"].unique()
activities = destinations["Activity"].unique()
demographics = destinations["Demographics"].unique()
cuisines = destinations["Cuisine"].unique()
histories = destinations["History"].unique()
natural_wonder = destinations["Natural Wonder"].unique()
accommodation = destinations["Accommodation"].unique()
language = destinations["Language"].unique()

unique_features = {"cities": cities, "countries": countries, "regions": regions, "climates": climates,
                 "budgets": budgets, "activities": activities, "demographics": demographics,
                 "cuisines": cuisines, "histories": histories, "natural_wonder": natural_wonder,
                 "accommodation": accommodation, "language": language}

print(unique_features)


if __name__ == "__main__":
    app = App()
    app.start()
