# %% -----------------------------------------------------------------------------------------------------------
# import packages

# python modules
import xarray as xr
import s3fs
import boto3
import time
import io
import pickle

# %% -------------------------------------------------------------------------
# Setup S3 bucket

s3 = boto3.client('s3')
bucket_name = 'aws-project-3'  # Replace with your bucket name

# %% -------------------------------------------------------------------------
# get S3 URLs for each site

sites = ['PH100']

URLS_AGG_S3 = {}

for s in sites:
    # print(s)
    if 'NRS' not in s:
        URLS_AGG_S3[s] = "imos-data/IMOS/ANMN/NSW/" + s + "/aggregated_timeseries/"
    else:
        URLS_AGG_S3[s] = "imos-data/IMOS/ANMN/NRS/" + s + "/aggregated_timeseries/"
# %% -----------------------------------------------------------------------------------------------------------
# Functions to load LTSP data

def getLTSPsS3(sites,URLS_AGG_S3):
    files = []
    data_links = []
    site_info = []
    s3 = s3fs.S3FileSystem(anon=True)
    for s in sites:
        files_site = s3.ls(URLS_AGG_S3[s])
        data_links.append(files_site)
        # get file names
        for n in range(len(files_site)):
            f = files_site[n].find('IMOS_ANMN')
            files.append(files_site[n][f::])
        site_info.append(s)
        
    # flatten data_links list
    data_links = [item for sublist in data_links for item in sublist]
        
    return files, data_links

def loadLTSPsS3(data_links, exclude_vars=None):
    """
    Load datasets from the provided data links, excluding specific variables if they exist.

    Parameters:
    - data_links (list): List of dataset links to load.
    - exclude_vars (list): List of variables to exclude from the datasets.

    Returns:
    - data (dict): Dictionary of loaded datasets with keys formatted as 'site_code_variable'.
    """
    
    data = {}
    s3 = s3fs.S3FileSystem(anon=False)  # Use `anon=False` for authenticated access

    for dls in data_links:
        print(dls)
        start_time = time.time() 
        # Open the dataset using s3fs
        if exclude_vars:
            ds = xr.open_dataset(s3.open(dls), drop_variables=exclude_vars)
        else:
            ds = xr.open_dataset(s3.open(dls))
        
        # Assuming 'site_code' is an attribute of the dataset
        key = ds.attrs['site_code'] + '_' + list(ds.variables)[0]
        data[key] = ds
        
        end_time = time.time()  # Record the end time
        iteration_time = end_time - start_time  # Calculate the time taken for the iteration

        print(f"Iteration took {iteration_time:.6f} seconds")
        
    return data    

def PickleSave(bucket_name, object_key, data2save):
    """
    Save data as a pickle file in an S3 bucket.
    
    :param bucket_name: Name of the S3 bucket
    :param object_key: The key (path) for the object in the S3 bucket
    :param data2save: The data to be pickled and saved
    """
    print('Saving data as a pickle to S3')

    # Create a bytes buffer to hold the pickle data
    pickle_buffer = io.BytesIO()

    # Pickle the data and write it to the bytes buffer
    pickle.dump(data2save, pickle_buffer)

    # Reset the buffer position to the beginning
    pickle_buffer.seek(0)

    # Initialize the S3 client
    s3_client = boto3.client('s3')

    # Upload the pickle file to S3
    s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=pickle_buffer)

    print('Data successfully saved to S3')


# %% -----------------------------------------------------------------------------------------------------------
# load aggregated files
# as dictionary

files, data_links = getLTSPsS3(sites,URLS_AGG_S3)
data = loadLTSPsS3(data_links)

# %% -----------------------------------------------------------------------------------------------------------
# Split LTSPs into OBSERVATION and INSTRUMENT datasets

dataOBS = {}
dataINS = {}

for k in list(data.keys()):
    # Create subsets for 'OBSERVATION' and 'INSTRUMENT'
    dataOBS[k] = data[k].drop_dims('INSTRUMENT')
    dataINS[k] = data[k].drop_dims('OBSERVATION')

# %% -----------------------------------------------------------------------------------------------------------
# Save LTSPs to pickle file stored on S3

PickleSave(bucket_name, 'Data/AGG_LTSPs.pkl', data)
PickleSave(bucket_name, 'Data/AGG_LTSPs_OBS.pkl', dataOBS)
PickleSave(bucket_name, 'Data/AGG_LTSPs_INS.pkl', dataINS)
