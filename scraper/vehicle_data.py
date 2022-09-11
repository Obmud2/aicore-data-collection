from uuid import uuid4
import json
import os
import urllib.request

class Vehicle_data:
    """
    Template class for storing vehicle data for each vehicle.
    """
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

    def __download_images(self, path):
        """
        Downloads image data from the given img src addresses stored within Vehicle_data.
        File are output in the following location:
            path/vehicle_id/images/vehicle_id_index.jpg
        """
        if not os.path.exists(f"{path}/{self.__vehicle_id}/images"):
            os.makedirs(f"{path}/{self.__vehicle_id}/images")
        img_index = 0
        for img_url in self.__data['img']:
            img_path = f"{path}/{self.__vehicle_id}/images/{self.__vehicle_id}_{img_index}.jpg"
            urllib.request.urlretrieve(img_url, img_path)
            img_index += 1
    def __save_JSON(self, path):
        """
        Saves Vehicle_data to JSON format in the following location:
            path/vehicle_id/data.json
        """
        if not os.path.exists(f"{path}/{self.__vehicle_id}"):
            os.makedirs(f"{path}/{self.__vehicle_id}")
        else:
            print(f"Veh id {self.__vehicle_id} already exists!")
            
        json_object = json.dumps(self.get_data(), indent=4)
        with open(f"{path}/{self.__vehicle_id}/data.json", 'w') as of:
            of.write(json_object)

    def add_data(self, **kwargs):
        """
        Adds data to the existing Vehicle_data object.
        Args:
            **kwargs (key = value): Input key/value pairs which are present in the Vehicle_data class template.
        """
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
    def get_data(self) -> dict:
        """
        Returns Vehicle_data in dictionary format.
        Returns:
            dict: Vehicle_data in {id:, uuid:, data:{}} format.
        """
        return {
            "id" : self.__vehicle_id,
            "uuid" : self.__UUID,
            "data" : self.__data
        }
    def get_url(self) -> str:
        """
        Returns:
            str: URL for Vehicle_data
        """
        return self.__data["href"]
    def get_id(self) -> str:
        """
        Returns:
            str: Autotrader unique ID for Vehicle_data
        """
        return self.__vehicle_id
    def save_data(self, path="raw_data"):
        """
        Downloads images and saves JSON data for Vehicle_data in file structure:
            path/vehicle_id/
        """
        self.__save_JSON(path)
        self.__download_images(path)