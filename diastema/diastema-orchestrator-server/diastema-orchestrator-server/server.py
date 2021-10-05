from flask import Flask, request, jsonify, Response
import requests
import json

""" Global variables """
# The name of the flask app
app = Flask(__name__)

# Diastema Token
diastema_token = "diastema-key"

# Kubernetes API URL to call spark jobs
kubernetes_api_url = "http://10.20.20.205:443/api"

""" Functions to call a spark job """
# A call for a data load job
def data_load(data_set_name, client_name, all_files, data_set_files):
    """
    Makes the API call to the data load service.
    
    Args: 
        - data_set_name (String) : The name of the dataset for the data load operation.
        - client_name (String) : The name of the client for the data load operation.
        - all_files (Dictionary) : All the files given to the diastema playbook.
        - data_set_files (List) : The files to send to the data load service.
    
    Returns:
        - The MongoDB ID for the next job, given by the Data Load job
    """
    # data-load query parameters.
    query_parameters = "?data-set="+data_set_name+"&"+"client-name="+client_name
    
    # Find the files to send to the data-load service.
    listOfFiles = []
    for file in data_set_files:
        lines = all_files[file].readlines()
        # Make a file in memory from the given file to send it for the data-load
        myFile = (all_files[file].name, (all_files[file].filename, b''.join(lines), all_files[file].mimetype))
        # Hold the file untill you send it.
        listOfFiles.append(myFile)
    
    # Make the API call
    # Due to spark calls not being ready, this is a dummy call.
    dummy_host = "http://localhost:5000/dummy-data-load"
    api_call = dummy_host+query_parameters
    response = requests.post(api_call, files=listOfFiles)
    #print(response.content)
    
    return bytes.decode(response.content ) 

# A call for a data cleaning job
def cleaning(mongodb_dataset_id, max_shrink="false", json_schema="false"):
    """
    Makes the API call to the data cleaning service.
    
    Args: 
        - mongodb_dataset_id (String) : The MongoDB ID of the last job's output
        - max_shrink (Float) : The pressentage of shrinking to be done on the dataset.
        - json_schema (JSON) : A JSON schema for the cleaning service.
    
    Returns:
        - The MongoDB ID for the next job, given by the Data Cleaning job
    """
    # data-cleaning query parameters.
    query_parameters = ""
    if max_shrink == "false":
        query_parameters = "?mongodb-id="+mongodb_dataset_id+"&"+"max-shrink="+max_shrink
    else:
        query_parameters = "?mongodb-id="+mongodb_dataset_id+"&"+"max-shrink="+str(max_shrink)
    
    # Make the API call
    # Due to spark calls not being ready, this is a dummy call.
    dummy_host = "http://localhost:5000/dummy-cleaning"
    api_call = dummy_host+query_parameters
    
    response = ""
    
    if json_schema == "false":
        response = requests.post(api_call)
    else:
        response = requests.post(api_call, json={'json-schema': json_schema})
    
    return bytes.decode(response.content ) 
    
# A call for a data classification job
def classification(mongodb_dataset_id, column, algorithm="false", tensorfow_algorithm="false"):
    """
    Makes the API call to the data classification service.
    
    Args: 
        - mongodb_dataset_id (String) : The MongoDB ID of the last job's output
        - algorithm (String) : The classification algorithm to use in the Service.
        - column (String) : The column to do the classification on, with the called job.
        - tensorfow_algorithm (Not Specified) : Jupiter Notebook Custom Algorithm or Neural Network Architecture.
    
    Returns:
        - The MongoDB ID for the next job, given by the Data Classification job
    """
    # data-classification query parameters.
    query_parameters = "?mongodb-id="+mongodb_dataset_id+"&"+"algorithm="+algorithm+"&"+"column="+column
    
    # Make the API call
    # Due to spark calls not being ready, this is a dummy call.
    dummy_host = "http://localhost:5000/dummy-classification"
    api_call = dummy_host+query_parameters
    
    response = ""
    
    if tensorfow_algorithm == "false":
        response = requests.post(api_call)
    else:
        response = requests.post(api_call, json={'tensorfow-algorithm': tensorfow_algorithm})
    
    return bytes.decode(response.content ) 
    
# A call for a data regression job
def regression(mongodb_dataset_id, column, algorithm="false", tensorfow_algorithm="false"):
    """
    Makes the API call to the data regression service.
    
    Args: 
        - mongodb_dataset_id (String) : The MongoDB ID of the last job's output.
        - algorithm (String) : The Regression algorithm to use in the Service.
        - column (String) : The column to do the regression on, with the called job.
        - tensorfow_algorithm (Not Specified) : Jupiter Notebook Custom Algorithm or Neural Network Architecture.
    
    Returns:
        - The MongoDB ID for the next job, given by the Data Regression job
    """
    # data-regression query parameters.
    query_parameters = "?mongodb-id="+mongodb_dataset_id+"&"+"algorithm="+algorithm+"&"+"column="+column
    
    # Make the API call
    # Due to spark calls not being ready, this is a dummy call.
    dummy_host = "http://localhost:5000/dummy-regression"
    api_call = dummy_host+query_parameters
    
    response = ""
    
    if tensorfow_algorithm == "false":
        response = requests.post(api_call)
    else:
        response = requests.post(api_call, json={'tensorfow-algorithm': tensorfow_algorithm})
    
    return bytes.decode(response.content ) 
    
# A call for a data visualize job
def visualize(mongodb_dataset_id):
    """
    Sends a call to the Front-End, informing it that a visualization is ready.
    
    Args: 
        - mongodb_dataset_id (String) : The MongoDB ID of the last job's output
    
    Returns:
        - Nothing
    """
    print("There has not been any confirmation of what to give to the front-end yet!")
    return "DATA-VISUALIZATION-MONGO-ID"

""" Functions used for the json handling """
# Request a job
def job_requestor(job_json, files_dict, jobs_anwers_dict, collection):
    """
    Makes the request of a job (the json given is the job), using the above functions.
    
    Args: 
        - job_json (JSON) : The job to be requested.
        - files_dict (Dictionary) : Possible files to be used in the job request.
        - jobs_anwers_dict (Dictionary) : All the answers of the jobs getting handled.
        - collection (String): The name of the collection to use for a data-load job.
    
    Returns:
        - Nothing.
    """
    title = job_json["title"]
    step = job_json["step"]
    from_step = job_json["from"]
    
    if(title == "data-load"):
        jobs_anwers_dict[step] = data_load(job_json["dataset-name"], collection, files_dict, job_json["files"])
    
    if(title == "cleaning"):
        jobs_anwers_dict[step] = cleaning(jobs_anwers_dict[from_step], max_shrink = job_json["max-shrink"])
    
    if(title == "classification"):
        jobs_anwers_dict[step] = classification(jobs_anwers_dict[from_step], job_json["column"], algorithm = job_json["algorithm"])
    
    if(title == "regression"):
        jobs_anwers_dict[step] = regression(jobs_anwers_dict[from_step], job_json["column"], algorithm = job_json["algorithm"])
    
    if(title == "visualize"):
        jobs_anwers_dict[step] = visualize(jobs_anwers_dict[from_step])
    
    return

# Access jobs by viewing them Depth-first O(N)
def jobs(job_step, jobs_dict, files, jobs_anwers_dict, collection):
    """
    A recursive function to access in a depth-first way all the jobs of a json analysis object.
    
    Args:
        - job_step (Int): The job that called this function.
        - jobs_dict (Dictionary): All the jobs of the given analysis.
        - files (Dictionary): All the files for the data-loading jobs.
        - jobs_anwers_dict (Dictionary): A dictionary containing all the answers of each job request.
        - collection (String): The name of the collection to use for the data-load jobs.
    
    Returns:
        - Nothing.
    """
    # Make the job request
    job_requestor(jobs_dict[job_step], files, jobs_anwers_dict, collection)
    
    # Depth-first approach
    next_steps = jobs_dict[job_step]["next"]
    for step in next_steps:
        if(step != 0):  # If ther is no next job then do not try to go deeper
            jobs(step, jobs_dict, files, jobs_anwers_dict, collection)
    return

# Handle the playbook
def handler(json_jobs, collection, raw_files):
    """
    Handle all the jobs of one analysis.
    
    Args:
        - json_jobs (JSON): All the jobs of a diastema analysis.
        - collection (String): The collection name to use for the data-loading jobs.
        - raw_files (List): Files given by the front-end to use as data-load. 
        
    Returns:
        - Nothing.
    """
    # Handle files as a dictionary - O(N)
    files = {}
    for file in raw_files:
        files[file] = raw_files[file]
    
    # handle jobs as a dictionary - O(N)
    jobs_dict = {}
    for job in json_jobs:
        jobs_dict[job["step"]] = job
    
    # Find starting jobs - O(N)
    starting_jobs = []
    for job_step, job in jobs_dict.items():
        # print(job_step, '->', job)
        if job["from"] == 0:
            starting_jobs.append(job_step)
    #print(starting_jobs)
    
    # Use a dictionary as a storage for each job answer
    jobs_anwers_dict = {}
    
    # for each starting job, start the analysis
    for starting_job_step in starting_jobs:
        job = jobs_dict[starting_job_step]
        # navigate through all the jobs and execute them in the right order
        jobs(starting_job_step, jobs_dict, files, jobs_anwers_dict, collection)
    
    # Print jobs_anwers_dict for testing purposes
    for job_step, answer in jobs_anwers_dict.items():
        print(job_step, '->', answer)
    
    return

""" Flask endpoints """
# An endpoint for handling and using the JSON playbook
@app.route("/analysis", methods=["POST"])
def analysis():
    """
    This functions is used as the endpoint for the orchestration of each analysis is needed to be done
    form the Diastema users.
    
    It will give feedback to the sedner to specify if the analysis is done correctly.
    
    Args: 
        Even if the function itself is not getting any arguments, it is using the form-data given by the 
        API call sender. This form data is specified below:
        - json-playbook (JSON) : A JSON reprecentation of the jobs to run.
        - files (file): Keys that have file values to get handled by the orchestrator.
    
    Returns:
        - Information about the status of the jobs given for execution.
    """
    # Get the JSON from the form-data
    playbook = json.loads(request.form["json-playbook"])
    
    # Here there will probably be code to check the whole json
    # To return if there is a bad request
    
    # Check Diastema token
    if playbook["diastema-token"] != diastema_token:
        return Response('{"reason": "diastema token is wrong"}', status=401, mimetype='application/json')
    
    # Get all the given files from the form-data
    files = request.files
    
    # Send the playbook for handling
    handler(playbook["jobs"], playbook["collection-id"], files)
    
    # The analysis has been accepted
    return Response(status=202)

""" Flask endpoints - Dummy Endpoints """
# Dummy data-load endpoint for testing purposes
@app.route("/dummy-data-load", methods=["POST"])
def dummy_data_load():
    data_set = request.args.get('data-set')
    client_name = request.args.get('client-name')
    print("The below data got send to the DATA LOADING service:")
    print("Dataset:",data_set)
    print("Client:",client_name)
    
    # Get all the given files
    files = request.files
    # For each file
    for file in files:
        # Print file's key name : File's real name
        print(file,":",files[file])
        # Print file's content
        lines = files[file].readlines()
        for line in lines:
            print(line)
    print()
    
    return "DATA-LOAD-MONGO-ID"

# Dummy cleaning endpoint for testing purposes
@app.route("/dummy-cleaning", methods=["POST"])
def dummy_cleaning():
    mongodb_id = request.args.get('mongodb-id')
    max_shrink = request.args.get('max-shrink')
    data = request.json
    print("The below data got send to the DATA CLEANING service:")
    print("MongoDB ID:",mongodb_id)
    print("Max Shrink:",max_shrink)
    print("Raw Data:",data)
    print()
    
    return "DATA-CLEANING-MONGO-ID"

# Dummy classification endpoint for testing purposes
@app.route("/dummy-classification", methods=["POST"])
def dummy_classification():
    mongodb_id = request.args.get('mongodb-id')
    algorithm = request.args.get('algorithm')
    column = request.args.get('column')
    data = request.json
    print("The below data got send to the DATA CLASSIFICATION service:")
    print("MongoDB ID:",mongodb_id)
    print("Algorithm:",algorithm)
    print("Column:",column)
    print("Raw Data:",data)
    print()
    
    return "DATA-CLASSIFICATION-MONGO-ID"

# Dummy regression endpoint for testing purposes
@app.route("/dummy-regression", methods=["POST"])
def dummy_regression():
    mongodb_id = request.args.get('mongodb-id')
    algorithm = request.args.get('algorithm')
    column = request.args.get('column')
    data = request.json
    print("The below data got send to the DATA REGRESSION service:")
    print("MongoDB ID:",mongodb_id)
    print("Algorithm:",algorithm)
    print("Column:",column)
    print("Raw Data:",data)
    print()
    
    return "DATA-REGRESSION-MONGO-ID"

""" Main """
# Main code
if __name__ == "__main__":
    app.run(debug=True)
