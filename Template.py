import sys
import tkinter
import tkinter.messagebox
from tkintermapview import TkinterMapView
from pyswip import Prolog
import pandas as pd


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
        ################################################################################################

        return [line.strip() for line in text.split('\n') if line.strip()]

    def start(self):
        self.mainloop()

# TODO 1: read destinations' descriptions from Destinations.csv and add them to the prolog knowledge base
################################################################################################
# STEP1: Define the knowledge base of illnesses and their symptoms

prolog = Prolog()
destinations = pd.read_csv("Destinations.csv")

destinations.at[37, "Destinations"] = "Washington DC"


# prolog.retractall("destination(_, _, _, _, _, _, _, _, _, _, _, _, _)")
# prolog.assertz("destination('Tokyo', japan, 'East Asia', temperate, high, cultural, solo, long, asian, modern, mountains, luxury, japanese)")
# prolog.assertz("destination('Ottawa', canada, 'North America', cold, medium, adventure, family_friendly, medium, european, modern, forests, mid_range, english)")
# prolog.assertz("destination('Mexico City', mexico, 'North America', temperate, low, cultural, senior, short, latin_american, ancient, mountains, budget, spanish)")
# prolog.assertz("destination('Rome', italy, 'Southern Europe', temperate, high, cultural, solo, medium, european, ancient, beaches, luxury, italian)")
# prolog.assertz("destination('Brasilia', brazil, 'South America', tropical, low, adventure, family_friendly, long, latin_american, modern, beaches, budget, portuguese)")

query = "destination(City, _, _, _, low, _, _, _, _, _, _, _, _)"
results = list(prolog.query(query))
for result in results:
    print(result)


arg = "destination("

for dest in destinations.iterrows():
    arg = "destination("
    for prop in range(13):
        phrase = dest[1].iloc[prop]
        if " " in phrase:
            phrase = phrase.replace(" ", "_")
        elif "'" in phrase:
            phrase = phrase.replace("'", "_")

        if prop == 12:
            arg += phrase
            continue
        else:
            arg += phrase + ", "
    arg += ")"
    prolog.assertz(arg)
results = list(prolog.query("destination(City, _, _, _, low, _, _, _, _, _, _, _, _)"))
for result in results:
    print(result["City"])


# TODO 2: extract unique features from the Destinations.csv and save them in a dictionary
################################################################################################


if __name__ == "__main__":
    app = App()
    app.start()
