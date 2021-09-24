from flask import Flask, request, jsonify, Response
import requests
import json

app = Flask(__name__)

### Functions used for the json handling ###
# A call for a data load job
def data_load(data_set_name, client_name, data_set_files):
    """
    Args: 
        - data_set_name (String) : The name of the dataset for the data load operation.
        - client_name (String) : The name of the client for the data load operation.
        - data_set_files (Dictionary) : The files to send to the data load service.
    
    Returns:
        - The MongoDB ID for the next job, given by the Data Load job
    """
    print("Data Loaded")
    # Print files from dictionary
    for filename, file in data_set_files.items():
        print(filename, "-", file, ":")
        lines = file.readlines()
        for line in lines:
            print(line)
    
    
    # REMEMBER THAT THERE CAN BE MORE THAN ONE DATA LOAD JOBS
    # AND YOU MUST USE SEND THE NEEDED FILE FOR EACH ONE
    
    return "A TEST MONGO DB ID 1"

# A call for a data cleaning job
def cleaning(mongodb_dataset_id, max_shrink="false", json_schema="false"):
    """
    Args: 
        - mongodb_dataset_id (String) : The MongoDB ID of the last job's output
        - max_shrink (Float) : The pressentage of shrinking to be done on the dataset.
        - json_schema (JSON) : A JSON schema for the cleaning service.
    
    Returns:
        - The MongoDB ID for the next job, given by the Data Cleaning job
    """
    print("Data Cleaned")
    return "A TEST MONGO DB ID 2"
    
# A call for a data classification job
def classification(mongodb_dataset_id, column, algorithm="false", tensorfow_algorithm="false"):
    """
    Args: 
        - mongodb_dataset_id (String) : The MongoDB ID of the last job's output
        - algorithm (String) : The classification algorithm to use in the Service.
        - column (String) : The column to do the classification on, with the called job.
        - tensorfow_algorithm (Not Specified) : Jupiter Notebook Custom Algorithm or Neural Network Architecture.
    
    Returns:
        - The MongoDB ID for the next job, given by the Data Classification job
    """
    print("Data Classified")
    return "A TEST MONGO DB ID 3"
    
# A call for a data regression job
def regression(mongodb_dataset_id, column, algorithm="false", tensorfow_algorithm="false"):
    """
    Args: 
        - mongodb_dataset_id (String) : The MongoDB ID of the last job's output
        - algorithm (String) : The classification algorithm to use in the Service.
        - column (String) : The column to do the classification on, with the called job.
        - tensorfow_algorithm (Not Specified) : Jupiter Notebook Custom Algorithm or Neural Network Architecture.
    
    Returns:
        - The MongoDB ID for the next job, given by the Data Regression job
    """
    print("Data Regressed")
    return "A TEST MONGO DB ID 4"
    
# A call for a data visualize job
def visualize(mongodb_dataset_id):
    """
    Args: 
        - mongodb_dataset_id (String) : The MongoDB ID of the last job's output
    
    Returns:
        - Nothing
    
    Description:
        Sends a call to the Front-End, informing it that a visualization is ready.
    """
    print("Data Visualized")
    return "A TEST MONGO DB ID 5"

def job_requestor(job_json, files_dict, jobs_anwers_dict, collection):
    """
    Args: 
        - job_json (JSON) : The job to be requested.
        - files_dict (Dictionary) : Possible files to be used in the job request.
        - jobs_anwers_dict ("Dictionary") : All the answers of the jobs getting handled.
    
    Returns:
        - Nothing
    
    Description:
        Makes the request of a job (the json given is the job).
    """
    title = job_json["title"]
    step = job_json["step"]
    from_step = job_json["from"]
    
    if(title == "data-load"):
        jobs_anwers_dict[step] = data_load(job_json["dataset-name"], collection, files_dict)
    
    if(title == "cleaning"):
        jobs_anwers_dict[step] = cleaning(jobs_anwers_dict[from_step], max_shrink = job_json["max-shrink"])
    
    if(title == "classification"):
        jobs_anwers_dict[step] = classification(jobs_anwers_dict[from_step], job_json["column"], algorithm = job_json["algorithm"])
    
    if(title == "regression"):
        jobs_anwers_dict[step] = regression(jobs_anwers_dict[from_step], job_json["column"], algorithm = job_json["algorithm"])
    
    if(title == "visualize"):
        jobs_anwers_dict[step] = visualize(jobs_anwers_dict[from_step])
    
    return

# Access jobs by viewing them Depth-first
def jobs(job_step, jobs_dict, files, jobs_anwers_dict, collection):
    # Print that this function did this job step 
    # print(job_step)
    
    # make the job request
    job_requestor(jobs_dict[job_step], files, jobs_anwers_dict, collection)
    
    # Depth-first approach
    next_steps = jobs_dict[job_step]["next"]
    for step in next_steps:
        if(step != 0):  # if ther is no next job then stop recursive
            jobs(step, jobs_dict, files, jobs_anwers_dict, collection)
    return
    

# Function to handle all the jobs of one analysis
# Gets the the jobs list from the form-data of the call
# Gets the files needed for the data loading jobs
def handler(json_jobs, collection, raw_files):
    # Handle files as a dictionary - O(N)
    files = {}
    for file in raw_files:
        files[file] = raw_files[file]
    
    # Print files from dictionary
    #for filename, file in files.items():
    #    print(filename, "-", file, ":")
    #    lines = file.readlines()
    #    for line in lines:
    #        print(line)
    
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
    
    # Use a dictionary as a storage for the each job answer
    jobs_anwers_dict = {}
    
    # for each starting job, start the analysis
    for starting_job_step in starting_jobs:
        job = jobs_dict[starting_job_step]
        # navigate through all the jobs and execute them in the right order
        jobs(starting_job_step, jobs_dict, files, jobs_anwers_dict, collection)
    
    # Print jobs_anwers_dict for testing purposes
    for job_step, answer in jobs_anwers_dict.items():
        print(job_step, '->', answer)
    
    return "handled"

### FLASK ENDPOINTS ###
@app.route("/test1", methods=["POST"])
def test1():
    print("DEBUGGING ##########################")
    
    # Get and print valuable stuff about the files in a give form-data body
    # of a POST request
    
    # Get all the given files
    files = request.files
    # For each file
    for file in files:
        # Print file's key name : File's real name
        print(file,":",files[file])
        # Print file's content
        # YOU CAN PRINT THE FILES ONLY ONCE
        # lines = files[file].readlines()
        # print(lines)
        # print(b''.join(lines))
        # for line in lines:
        #     print(line)
    
    # Get and print valuable stuff about the keys in a give form-data body
    # of a POST request
    
    # Get the form-data
    form = request.form
    # For each key in the form-data
    for key in form.keys():
        # Print the value of this key
        for value in form.getlist(key):
            print (key,":",value)
    
    # test request to an other API endpoint
    # response = requests.get("http://localhost:5000/test2")
    
    # test request to an endpoint that will get the passed files
    url = "http://localhost:5000/test3"
    # Send one file after making its content
    # files = {'file': ('report.csv', 'some,data,to,send\nanother,row,to,send\n')}
    
    # Send multiple files after making their content
    # files = [('file1', ('report1.csv', 'some,data,to,send\nanother,row,to,send\n')),
    #         ('file2', ('report2.csv', 'some,data,to,send\nanother,row,to,send\n'))]
    
    # Send all the files got by THIS endpoint
    # List for all the files to send
    listOfFiles = []
    for file in files:
        # Put the files in the memory
        lines = files[file].readlines()
        # Make a temp file with all the right attributes and byte data as content and append it in the list
        myFile = (files[file].name, (files[file].filename, b''.join(lines), files[file].mimetype))
        listOfFiles.append(myFile)
    
    # Make the API call
    response = requests.post(url, files=listOfFiles)
    
    print("DEBUGGING END ##########################")
    return response.content

@app.route("/test2", methods=["GET"])
def test2():
    return "hello from test2"
    
@app.route("/test3", methods=["POST"])
def test3():
    print("You gave at the test3 endpoint")
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
    return "good job"

# An endpoint to use the JSON playbook
@app.route("/analysis", methods=["POST"])
def analysis():
    # Get the JSON from the form data
    playbook = json.loads(request.form["json-playbook"])
    
    # print given diastema-token
    #print(playbook["diastema-token"])
    
    # print given analysis-id
    #print(playbook["analysis-id"])
    
    # print given analysis-datetime
    #print(playbook["analysis-datetime"])
    
    # print given jobs
    # print(playbook["jobs"])
    
    # print the first given job
    # print(playbook["jobs"][0])
    
    # Get all the given files
    files = request.files
    
    # Send the playbook for handling
    jobs_handler = handler(playbook["jobs"], playbook["collection-id"], files)
    #print(jobs_handler)
    
    
    # Response('{"Got analysis": true}', status=202, mimetype='application/json')
    return Response(status=202)

if __name__ == "__main__":
    app.run(debug=True)
