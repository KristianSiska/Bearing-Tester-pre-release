
import os
# for copying files
import shutil

# FTP comunication
from ftplib import FTP
import configparser

import csv

def addPlus(value):
    try:
        if int(value) > 0:
            return str(f'+{value}')
        elif int(value < 0):
            return str(f'{value}')
        else:
            return value
    except:
        return value
   


def get_config_list(configFile, section, item):
    values = []
    for i in range(1, len(configFile[f"{section}"]) + 1):
        value = configFile.get(f'{section}',f'{item}{i}',fallback=None)
        if value is not None:
            values.append(value)
    return values



def add_value_to_ini_file(file_path, section, key, value):
    """
    Add or update a key-value pair in a specific section of an INI file.

    Parameters:
    - file_path (str): The path to the INI file.
    - section (str): The section in which the key-value pair should be added or updated.
    - key (str): The key for the new or existing value.
    - value (str): The value to be added or updated.

    Returns:
    - None
    """
    config = configparser.ConfigParser()

    # Read the existing INI file
    config.read(file_path)

    # Check if the specified section exists, if not, create it
    if section not in config:
        config.add_section(section)

    # Add or update the key-value pair in the specified section
    config.set(section, key, value)

    # Write the changes back to the INI file
    with open(file_path, 'w') as config_file:
        config.write(config_file)

def find_highest_index(ini_path, section, variable_name):
    """
    Find the highest index for a specific variable within a given section in an INI file.

    Parameters:
    - ini_path (str): The path to the INI file.
    - section (str): The section where the variable is located.
    - variable_name (str): The name of the variable for which to find the highest index.

    Returns:
    - int: The highest index found for the specified variable in the given section.
    """
    config = configparser.ConfigParser()

    # Read the existing INI file
    config.read(ini_path)

    # Check if the specified section exists
    if section in config:
        # Filter keys in the specified section that start with the variable_name
        relevant_keys = [key for key in config[section] if key.startswith(variable_name)]

        if relevant_keys:
            # Extract indices from the relevant keys and find the maximum
            indices = [int(key[len(variable_name):]) for key in relevant_keys if key[len(variable_name):].isdigit()]
            if indices:
                highest_index = max(indices)
                return int(highest_index)

    # Return -1 if the specified section or variable does not exist or no relevant keys found
    return -1



def safe_save_to_csv(file_path, data, data_mode = "w"):
    """
    Safely save a big text variable to a CSV file.

    Parameters:
    - file_path (str): The path to the CSV file.
    - data (str): The big text variable to be saved.

    Returns:
    - bool: True if the data is successfully saved, False otherwise.
    """
    try:
        # Open the CSV file for writing
        with open(file_path, data_mode, newline='', encoding='utf-8') as csv_file:
            # Use csv.writer to write the data to the CSV file
            data.replace('"', '')
            #writer = csv.writer(csv_file)
            
            # Write the data to the CSV file
            #writer.writerow([data])
            csv_file.write(data)

        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False




def set_data_list_ini(data_list, ini_file_path, section_name, starting_word):
    config = configparser.ConfigParser()

    # Read the existing INI file, create if it doesn't exist
    config.read(ini_file_path)

    # Ensure the section exists
    if section_name not in config:
        config.add_section(section_name)
    else:
        # Clear existing IP keys in the specified section
        for key in config.options(section_name):
            if key.startswith(f'{starting_word}'):
                config.remove_option(section_name, key)

    # Set the IP addresses in the specified section
    for i, data in enumerate(data_list, start=1):
        config.set(section_name, f'{starting_word}{i}', data)

    # Write the updated INI file
    with open(ini_file_path, 'w') as config_file:
        config.write(config_file)


# this function will convert seconds to hours, minutes and seconds
def convert_seconds(seconds):
    # Calculate hours, minutes, and remaining seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    return int(round(hours,0)), int(round(minutes,0)), int(round(remaining_seconds,0))











# This function will create a new folder
def create_folder(folder_path, foldername):
    full_path = os.path.join(folder_path, foldername)
    if not os.path.exists(full_path):
        try:
            os.makedirs(full_path)
           
        except OSError as e:
            pass
    else:
        pass





# This function will copy a file
def copy_file(source_path, destination_path, new_filename=None):
    if new_filename is None:
        new_filename = os.path.basename(source_path)

    destination_file = os.path.join(destination_path, new_filename)

    try:
        shutil.copy2(source_path, destination_file)
        
        print(f"COPY     |File '{source_path}' copied to '{destination_file}' successfully.")
    except Exception as e:
        
        
        print(f"Error copying file '{source_path}': {e}")


# this function will create directories if they are not existing
def create_ftp_directory_structure(ftp, path):
    dirs = path.split('/')
    for d in dirs:
        if d:
            try:
                ftp.cwd(d)
            except:
                ftp.mkd(d)
                ftp.cwd(d)

# This function will upload a file to the FTP server
def upload_file_to_ftp(file_path, ftp_server, ftp_username, ftp_password, target_folder):
    try:
        # Connect to the FTP server
        ftp = FTP(ftp_server)
        ftp.login(user=ftp_username, passwd=ftp_password)

        # Create the necessary directory structure
        create_ftp_directory_structure(ftp, target_folder)

        # Change to the target folder
        ftp.cwd(target_folder)

        # Get the file name from the file path
        file_name = file_path.split('/')[-1]

        # Open the local file in binary mode for reading
        with open(file_path, 'rb') as local_file:
            # Upload the file to the FTP server
            ftp.storbinary('STOR ' + file_name, local_file)

        # Close the FTP connection
        ftp.quit()
        
    except Exception as e:
        pass

