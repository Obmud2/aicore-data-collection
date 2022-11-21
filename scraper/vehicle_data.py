import json
import os
import urllib.request
import pandas as pd
import datetime
from uuid import uuid4
from shutil import rmtree
from tqdm import tqdm

class Vehicle_data:
    """
    Template class for storing vehicle data for each vehicle.
    """
    def __init__(self, vehicle_id, uuid=None):
        self.__vehicle_id = vehicle_id
        self.__UUID = str(uuid4()) if not uuid else uuid
        self.__date_scraped = datetime.datetime.now()
        self.__last_updated = None
        self.__date_removed = None
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

    def __download_images(self, path) -> None:
        """
        Downloads image data from the given img src addresses stored within Vehicle_data.
        File are output in the following location:
            path/vehicle_id/images/vehicle_id_index.jpg
        Args:
            path (str): Path for saving image data
        """
        if not os.path.exists(f"{path}/{self.__vehicle_id}/images"):
            os.makedirs(f"{path}/{self.__vehicle_id}/images")
        img_index = 0
        for img_url in self.__data['img']:
            img_path = f"{path}/{self.__vehicle_id}/images/{self.__vehicle_id}_{img_index}.jpg"
            urllib.request.urlretrieve(img_url, img_path)
            img_index += 1
    
    def __save_JSON(self, path, verbose=False) -> None:
        """
        Saves Vehicle_data to JSON format in the following location:
            path/vehicle_id/data.json
        Args:
            Path for saved JSON data
        """
        if not os.path.exists(f"{path}/{self.__vehicle_id}"):
            os.makedirs(f"{path}/{self.__vehicle_id}")
        else:
            if verbose: print(f"Veh id {self.__vehicle_id} already exists!")
            
        json_object = json.dumps(self.get_data(), indent=4, default=str)
        with open(f"{path}/{self.__vehicle_id}/data.json", 'w') as of:
            of.write(json_object)

    def add_data(self, **kwargs) -> None:
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
    
    def set_date_removed(self) -> None:
        """
        Set __date_removed to current time
        """
        self.__date_removed = datetime.datetime.now()

    def get_data(self, flattened=False) -> dict:
        """
        Args:
            flattened (bool): Option to select dict output format
        Returns:
            dict: Vehicle_data in {id:, uuid:, data:{}} (flattened = False) or {id:, uuid:, data1:, data2:, ../} (flattened = True) formats.
        """
        data_dict = {
            "id" : self.__vehicle_id,
            "uuid" : self.__UUID,
            "date_scraped" : self.__date_scraped,
            "last_updated" : self.__last_updated,
            "date_removed" : self.__date_removed
        }
        if flattened:
            data_dict.update(self.__data)
        else:
            data_dict['data'] = self.__data
        return data_dict

    def get_data_pd(self) -> pd.DataFrame:
        """
        Returns:
            (DataFrame): Vehicle_data in single row pandas df
        """
        dt = self.get_data(flattened=True)
        img_temp = f"{{{dt['img'][0]}"
        for i in range(1,len(dt['img'])):
            img_temp += f", {dt['img'][i]}"
        img_temp += f"}}"
        dt['img'] = img_temp
        dt = {k:[v] for k,v in dt.items()}
        return pd.DataFrame(dt)
    
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
    
    def save_to_local(self, path="raw_data") -> None:
        """
        Downloads images and saves JSON data for Vehicle_data in file structure:
            path/vehicle_id/
        Args:
            path (str): Path to save data. Default = 'raw_data'
        """
        self.__save_JSON(path)
        self.__download_images(path)

    @staticmethod
    def select_storage_method() -> str:
        """

        Returns:
            (str): "local", "rds" or "localrds"
        """
        while(True):
            try:
                storage_method = int(input("Select storage method:" + 
                    "\n[1]\tLocal" +
                    "\n[2]\tRDS" +
                    "\n[3]\tLocal + RDS\n"))
            except:
                print("That's not an option! Try again.")
            if storage_method == 1:
                return "local"
            elif storage_method == 2:
                return "rds"
            elif storage_method == 3:
                return "localrds"
            else:
                print("Selection out of range. Try again.")

    @staticmethod
    def parse_json_vehicle_data_list(path) -> list:
        """
        Reads a JSON file containing a list of Vehicle_data objects
        Args:
            path (str): Path of JSON file
        Return:
            (list[Vehicle_data]): List of Vehicle_data objects
        """
        with open(path, 'r') as of:
            vehicle_data_list_from_json = json.load(of)
        vehicle_data_list = []
        for vehicle in vehicle_data_list_from_json:
            vehicle_data = Vehicle_data(vehicle['id'], vehicle['uuid'])
            vehicle_data.__date_scraped = datetime.datetime.strptime(vehicle['date_scraped'], '%Y-%m-%d %H:%M:%S.%f')
            try: vehicle_data.__last_updated = datetime.datetime.strptime(vehicle['last_updated'], '%Y-%m-%d %H:%M:%S.%f')
            except: pass
            vehicle_data.add_data(**vehicle['data'])
            vehicle_data_list.append(vehicle_data)
        return vehicle_data_list

    @staticmethod
    def get_pandas_vehicle_data_list(vehicle_data_list=None) -> pd.DataFrame:
        """
        Returns list of Vehicle_data objects as pandas df.
        Args:
            vehicle_data_list (list[Vehicle_data]): List of Vehicle_data objects
        Returns:
            (Dataframe): Vehicle data
        """
        data = []
        for vehicle in vehicle_data_list:
            vehicle_data = vehicle.get_data(flattened=True)
            data.append(vehicle_data)
        df = pd.DataFrame(data)
        return df

    @staticmethod
    def save_list_to_local(vehicle_data_list, path="raw_data") -> None:
        """
        Args:
            vehicle_data_list (list{Vehicle_data}): List from memory to store data
            path (str): Path to save data
        """
        for vehicle in tqdm(vehicle_data_list, desc="Saving data to local..."):
            vehicle.save_to_local(path)

    @staticmethod
    def rm_local_dir(dir='raw_data') -> None:
        rmtree(dir, ignore_errors=True)
