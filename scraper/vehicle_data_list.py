import pandas as pd
from scraper.vehicle_data import Vehicle_data
from scraper.aws_handler import AWS_handler

class Vehicle_data_list():
    
    def __init__(self) -> None:
        COLUMNS = ['id',
            'uuid',
            'date_scraped',
            'last_updated',
            'date_removed',
            'href',
            'title',
            'subtitle',
            'price',
            "location",
            "mileage",
            "description",
            "img"]
        self.vdl = pd.DataFrame(columns=COLUMNS)

    def append_vehicle(self, vehicle):
        if type(vehicle = Vehicle_data):
            self.vdl.append(vehicle)
        else:
            raise TypeError

