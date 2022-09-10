from uuid import uuid4
import json
import os
import urllib.request

class Vehicle_data:
    def __init__(self, vehicle_id):
        self.__vehicle_id = vehicle_id
        self.__UUID = str(uuid4())
        self.__data = {
            "href" : None,
            "title" : None,
            "subtitle" : None,
            "price" : None,
            "location" : None,
            "mileage" : None,
            "description" : None,
            "img" : []
        }

    def add_data(self, **kwargs):
        for key, value in kwargs.items():
            if key == "img":
                if not isinstance(value, list):
                    raise TypeError("img type must be a list.")
                for v in value:
                    if v not in self.__data[key]:
                        self.__data[key].append(v)
            elif key in self.__data:
                if self.__data[key]:
                    print(f"Overwriting vehicle data ID {self.__vehicle_id}: {key} : {self.__data[key]} -> {value}")
                self.__data[key] = value
            else:
                raise KeyError("Invalid key in vehicle data entry")

    def get_data(self):
        return {
            "id" : self.__vehicle_id,
            "uuid" : self.__UUID,
            "data" : self.__data
        }
    def get_url(self):
        return self.__data["href"]
    def get_id(self):
        return self.__vehicle_id
    def download_images(self):
        if not os.path.exists(f"raw_data/{self.__vehicle_id}/images"):
            os.mkdir(f"raw_data/{self.__vehicle_id}/images")
        img_index = 0
        for img_url in self.__data['img']:
            img_path = f"raw_data/{self.__vehicle_id}/images/{self.__vehicle_id}_{img_index}.jpg"
            urllib.request.urlretrieve(img_url, img_path)
            img_index += 1
    def save_JSON(self):
        if not os.path.exists(f"raw_data/{self.__vehicle_id}"):
            os.mkdir(f"raw_data/{self.__vehicle_id}")
        else:
            print(f"Veh id {self.__vehicle_id} already exists!")
            
        json_object = json.dumps(self.get_data(), indent=4)
        with open(f"raw_data/{self.__vehicle_id}/data.json", 'w') as of:
            of.write(json_object)
