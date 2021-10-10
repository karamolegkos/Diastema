from flask import Flask, request, jsonify, Response
import requests
import json
import random   # for dummy results
import io
from minio import Minio
from pymongo import MongoClient

# from minio.error import S3Error

# Example of how the analysis is getting saved
#---------------------------------------------
# Metis -- Analysis-1 -- Raw-Files-1
#       |             |- Data-Load-1
#       |             |- Raw-Files-2
#       |             |- Data-Load-2
#       |             |- Analysis-1-1
#       |             |- Analysis-1-2
#       |             |- Analysis-2-1
#       |
#       |- Analysis-2 -- Raw-Files-1
#                     |- Data-Load-1
#                     |- Analysis-1-1
#                     |- Analysis-1-2
#
# BIO   -- Analysis-1 -- Raw-Files-1
#                     |- Data-Load-1
#                     |- Raw-Files-2
#                     |- Data-Load-2
#                     |- Analysis-1-1
#                     |- Analysis-1-2
#                     |- Analysis-1-2-1
#                     |- Analysis-1-2-2
#                     |- Analysis-1-3
#                     |- Analysis-2-1

""" Global variables """
# The name of the flask app
app = Flask(__name__)

# Diastema Token
diastema_token = "diastema-key"

# Kubernetes API HOST to call spark jobs
kubernetes_api_host = "http://10.20.20.205:443/api"

# Spark API HOST to call spark jobs
spark_api_host = "http://localhost:5000"

# MongoDB HOST
mongo_host = "localhost:27017"
mongo_client = MongoClient("mongodb://"+mongo_host+"/")

# MinIO HOST and Client
minio_host = "localhost:9000"
minio_client = Minio(
        minio_host,
        access_key="diastema",
        secret_key="diastema",
        secure=False
    )

# Diastema Front End host
diastema_front_end_host = "http://localhost:5000"

# Diastema Data Clean and Data Load Servcices
diastema_data_loading_api_host = "http://localhost:5000/data-loading-cleaning-api"
diastema_data_cleaning_api_host = "http://localhost:5000/data-loading-cleaning-api"

""" Frequently used code """
# Make a good MinIO String
def minioString(obj):
    """
    A Function to cast an object to str and then lowercase it.
    This Function is helping to name paths, needed for the analysis in the right way.

    Args:
        - obj (Python Object): An object to turn it into a lowercase String.

    Returns:
        - Lower cased String (String): The lowecased String of the given object.
    """
    return str(obj).lower()

# Insert one record in mongo
def insertMongoRecord(mongo_db_client, mongo_db_analysis_collection, record):
    """
    A Function used to insert records into the Diastema MongoDB Server.

    Args:
        - mongo_db_client (String): A MongoDB Database as the user who wants to make an analysis.
        - mongo_db_analysis_collection (String): A MongoDB Collection as an Analysis of a User.
        - record (JSON): The record to insert in the given collection.

    Returns:
        - Nothing
    """
    mongo_db = mongo_client[mongo_db_client]
    analysis_collection = mongo_db[mongo_db_analysis_collection]
    analysis_collection.insert_one(record)
    return

# Contact Diastema Front-End for the ending of a job
def diastema_call(db_id, analysis_id, job_name):
    """
    This function is making an API request to the Diastema central API Server. 
    It will inform it for the end of a job, or the end of the whole analysis.

    Args:
        - db_id (String): The user who needs to be informed.
        - analysis_id (String): The analysis ID of the user.
        - job_name (String): A job name, or the "analysis" value.

    Returns:
        - Nothing
    """
    url = diastema_front_end_host+"/modelling"
    payload = {"database-id":db_id, "analysis-id":analysis_id, "job-name":job_name}
    requests.post(url, json=payload)
    print("Contacted Diastema Front  End")
    return

""" Functions to call a spark job """
# Spark job Handler
def spark_caller(call_args):
    """
    A function to handle the spark calling procedure.
    It will contact the cluster to make jobs and after every job it will
    waut untill the job is FINISHED to continue.

    Args:
        - call_args (List): The arguments of the app to run 
            (The arguments contain the spark job in the 0 possition)

    Returns:
        - Nothing
    """
    # Submit the job
    job_call_responce = job_caller(call_args)
    job_call_json_responce = job_call_responce.json()
    driver = job_call_json_responce["submissionId"]

    # get job state until the job is finished
    job_test_responce = job_tester(driver)
    job_test_json_responce = job_test_responce.json()
    state = job_test_json_responce["driverState"]
    while state != "FINISHED":
        job_test_responce = job_tester(driver)
        job_test_json_responce = job_test_responce.json()
        state = job_test_json_responce["driverState"]

    return

# API call to submit a spark job
def job_caller(call_args):
    """
    A function to make the API call to a Spark Cluster.

    Args:
        - call_args (List): The arguments of the app to run 
            (The arguments contain the spark job in the 0 possition)

    Returns:
        - responce (Responce): The Responce of the API request.
    """
    call = spark_api_host+"/v1/submissions/create"
    headers = {'Content-Type': 'application/json;charset=UTF-8'}
    appResource = "file:"+call_args[0]
    json = {
        "appResource": appResource,
        "sparkProperties": {
            "spark.master": "local[*]",
            "spark.eventLog.enabled": "false",
            "spark.app.name": "Spark REST API - PI"
        },
        "clientSparkVersion": "3.1.2",
        "mainClass": "org.apache.spark.deploy.SparkSubmit",
        "environmentVariables": {
            "SPARK_ENV_LOADED": "1"
        },
        "action": "CreateSubmissionRequest",
        "appArgs": call_args
    }
    return requests.post(call, json=json, headers=headers)
    
# API call to check a Spark job
def job_tester(driver):
    """
    An API call to test if a job is FINISHED or RUNNING.

    Args:
        - driver (String): The Spark driver's ID handling the executors of the job.

    Returns:
        - responce (Responce): The Responce of the API request.
    """
    call = spark_api_host+"/v1/submissions/status/"+driver
    return requests.get(call)

""" Spark Jobs And Diastema API Jobs """
# Data load job
def data_load(playbook, job, all_files, data_set_files):
    """
    A function to handle a Data Loading Job from the Diastema JSON playbook.
    It will setup the folders needed for the spark jobs in the MinIO Database.
    Then it will call the Spark Job after configuring the way that the job must be called.
    After the above, it will use the MongoDB to save the path and the whole job in the needed analysis collection.

    Args:
        - playbook (JSON): The Diastema playbook.
        - job (JSON): The Data Loading Job from the Diastema playbook.
        - all_files (Dictionary): All the files of the Data Loading jobs in the Diastema playbook.
        - data_set_files (List): The files of the given Job to Data Load.

    Returns:
        - MinIO path (String): The path that the loaded data are saved.
    """
    # Raw bucket = User/analysis-id/job-id
    raw_bucket = minioString(playbook["database-id"])+"/analysis-"+minioString(playbook["analysis-id"])+"/raw-"+minioString(job["id"])

    # Bucket to Load Data = User/analysis-id/job-step
    load_bucket = minioString(playbook["database-id"])+"/analysis-"+minioString(playbook["analysis-id"])+"/loaded-"+minioString(job["step"])

    # Jobs arguments
    #job_args = ["/root/spark-job/load-job.py", raw_bucket, load_bucket]

    # Make the Databse Bucket
    if minio_client.bucket_exists(minioString(playbook["database-id"])) == False:
        minio_client.make_bucket(minioString(playbook["database-id"]))
    
    # Make the Raw Bucket directory
    minio_client.put_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/raw-"+minioString(job["id"])+"/", io.BytesIO(b""), 0,)

    #Make the load Bucket directory
    minio_client.put_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/loaded-"+minioString(job["step"])+"/", io.BytesIO(b""), 0,)

    # insert the raw files in the raw bucket
    for file in data_set_files:
        minio_client.put_object(
            minioString(playbook["database-id"]), 
            "analysis-"+minioString(playbook["analysis-id"])+"/raw-"+minioString(job["id"])+"/"+all_files[file].filename, 
            all_files[file], 
            length=-1, 
            part_size=10*1024*1024
        )
    
    # Make the API call for the Data Loading Service
    url = diastema_data_loading_api_host
    form_data = {"minio-input": raw_bucket, "minio-output": load_bucket}
    requests.post(url, form_data)

    # Insert the raw and loaded data in MongoDB
    raw_job_record = {"minio-path":raw_bucket, "directory-kind":"raw-data", "for-job-step":minioString(job["step"])}
    data_load_job_record = {"minio-path":load_bucket, "directory-kind":"loaded-data", "job-json":job}
    insertMongoRecord(minioString(playbook["database-id"]), "analysis_"+minioString(playbook["analysis-id"]), raw_job_record)
    insertMongoRecord(minioString(playbook["database-id"]), "analysis_"+minioString(playbook["analysis-id"]), data_load_job_record)

    # Contact front end for the ending of the job
    diastema_call(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"]), "data-load")

    # Return the bucket that this job made output to
    return load_bucket

# Cleaning job
def cleaning(playbook, job, last_bucket, max_shrink=False, json_schema=False):
    """
    A function to handle a Data Cleaning Job from the Diastema JSON playbook.
    It will setup the folders needed for the spark jobs in the MinIO Database.
    Then it will call the Spark Job after configuring the way that the job must be called.
    After the above, it will use the MongoDB to save the path and the whole job in the needed analysis collection.

    Args:
        - playbook (JSON): The Diastema playbook.
        - job (JSON): The Data Loading Job from the Diastema playbook.
        - last_bucket (String): The path that the raw data are saved.
        - max_shrink (float): The maximm shrinking of the data set to be cleaned.
        - json_schema (JSON): A JSON schema for the data cleaning job.

    Returns:
        - MinIO path (String): The path that the cleaned data are saved.
    """
    # Data Bucket = last jobs output bucket
    data_bucket = last_bucket

    # Analysis Bucket = User/analysis-id/job-step
    analysis_bucket = minioString(playbook["database-id"])+"/analysis-"+minioString(playbook["analysis-id"])+"/cleaned-"+minioString(job["step"])

    # Jobs arguments
    #job_args = ["/root/spark-job/cleaning-job.py", data_bucket, analysis_bucket]

    # Optional args
    #if max_shrink != False:
    #    job_args.append('"'+str(max_shrink)+'"')
    #if json_schema != False:
    #    job_args.append('"'+str(json_schema)+'"')

    # Make the MinIO Analysis buckers
    minio_client.put_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/cleaned-"+minioString(job["step"])+"/", io.BytesIO(b""), 0,)


    # Make the API call for the Data Cleaning Service
    url = diastema_data_cleaning_api_host

    # Optional args
    if max_shrink != False:
        url = url+"?max-shrink="+str(max_shrink)
    if json_schema != False:
        if max_shrink != False:
            url = url+"&json-schema="+'"'+str(json_schema)+'"'
        else:
            url = url+"?json-schema="+'"'+str(json_schema)+'"'

    form_data = {"minio-input": data_bucket, "minio-output": analysis_bucket}
    requests.post(url, form_data)

    # Insert the cleaned data in MongoDB
    cleaning_job_record = {"minio-path":analysis_bucket, "directory-kind":"cleaned-data", "job-json":job}
    insertMongoRecord(minioString(playbook["database-id"]), "analysis_"+minioString(playbook["analysis-id"]), cleaning_job_record)

    # Contact front end for the ending of the job
    diastema_call(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"]), "cleaning")

    # Return the bucket that this job made output to 
    return analysis_bucket

# Classification job
def classification(playbook, job, last_bucket, algorithm=False, tensorfow_algorithm=False):
    """
    A function to handle a Classification Analysis Job from the Diastema JSON playbook.
    It will setup the folders needed for the spark jobs in the MinIO Database.
    Then it will call the Spark Job after configuring the way that the job must be called.
    After the above, it will use the MongoDB to save the path and the whole job in the needed analysis collection.

    Args:
        - playbook (JSON): The Diastema playbook.
        - job (JSON): The Data Loading Job from the Diastema playbook.
        - last_bucket (String): The path that the non analyzed data are saved.
        - algorithm (String): The algorithm to run.
        - tensorfow_algorithm (String): A tensorflow algorithm to run.

    Returns:
        - MinIO path (String): The path that the analyzed data are saved.
    """
    # All the available spark classfication jobs 
    spark_files = {
        "logistic regression" : "/root/diastema-jobs/classification/logistic_regression.py",
        "decision tree classifier" : "/root/diastema-jobs/classification/decision_tree.py",
        "random forest classifier" : "/root/diastema-jobs/classification/random_forest.py",
        "gradient-boosted tree classifier" : "/root/spark-job/classification-job-4.py", # Not imported yet
        "multilayer perceptron classifier" : "/root/spark-job/classification-job-5.py", # Not imported yet
        "linear support vector machine" : "/root/spark-job/classification-job-6.py",    # Not imported yet
        "support vector machine" : "/root/spark-job/classification-job-7.py"            # Not imported yet
    }

    # Gget the spark algorithm to run
    job_to_run = ""
    if algorithm==False:
        job_to_run = list(spark_files.values())[0]
    else:
        job_to_run = spark_files[algorithm]
    print(job_to_run)

     # Data Bucket = last jobs output bucket
    data_bucket = last_bucket

    # Analysis Bucket = User/analysis-id/job-step
    analysis_bucket = minioString(playbook["database-id"])+"/analysis-"+minioString(playbook["analysis-id"])+"/classified-"+minioString(job["step"])

    # Jobs arguments
    job_args = [job_to_run, data_bucket, analysis_bucket, job["column"]]

    # Make the MinIO Analysis buckers
    minio_client.put_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/classified-"+minioString(job["step"])+"/", io.BytesIO(b""), 0,)

    # Make the Spark call
    spark_caller(job_args)

    # Remove the _SUCCESS file from the  spark job results
    minio_client.remove_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/classified-"+minioString(job["step"])+"/_SUCCESS")

    # Insert the classified data in MongoDB
    classification_job_record = {"minio-path":analysis_bucket, "directory-kind":"classified-data", "job-json":job}
    insertMongoRecord(minioString(playbook["database-id"]), "analysis_"+minioString(playbook["analysis-id"]), classification_job_record)

    # Contact front end for the ending of the job
    diastema_call(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"]), "classification")

    # Return the bucket that this job made output to 
    return analysis_bucket

# Regression job
def regression(playbook, job, last_bucket, algorithm=False, tensorfow_algorithm=False):
    """
    A function to handle a Regression Analysis Job from the Diastema JSON playbook.
    It will setup the folders needed for the spark jobs in the MinIO Database.
    Then it will call the Spark Job after configuring the way that the job must be called.
    After the above, it will use the MongoDB to save the path and the whole job in the needed analysis collection.

    Args:
        - playbook (JSON): The Diastema playbook.
        - job (JSON): The Data Loading Job from the Diastema playbook.
        - last_bucket (String): The path that the non analyzed data are saved.
        - algorithm (String): The algorithm to run.
        - tensorfow_algorithm (String): A tensorflow algorithm to run.

    Returns:
        - MinIO path (String): The path that the analyzed data are saved.
    """
    # All the available spark regression jobs 
    spark_files = {
        "linear regression" : "/root/diastema-jobs/regression/linear_regression.py",
        "generalized linear regression" : "/root/spark-job/regression-job-2.py",        # Not imported yet
        "decision tree regression" : "/root/diastema-jobs/regression/decision_tree.py",
        "random forest regression" : "/root/diastema-jobs/regression/random_forest.py",
        "gradient-boosted tree regression" : "/root/spark-job/regression-job-5.py"      # Not imported yet
    }

    # Get the spark algorithm to run
    job_to_run = ""
    if algorithm==False:
        job_to_run = list(spark_files.values())[0]
    else:
        job_to_run = spark_files[algorithm]

    # Data Bucket = last jobs output bucket
    data_bucket = last_bucket

    # Analysis Bucket = User/analysis-id/job-step
    analysis_bucket = minioString(playbook["database-id"])+"/analysis-"+minioString(playbook["analysis-id"])+"/regressed-"+minioString(job["step"])

    # Jobs arguments
    job_args = [job_to_run, data_bucket, analysis_bucket, job["column"]]

    # Make the MinIO Analysis buckers
    minio_client.put_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/regressed-"+minioString(job["step"])+"/", io.BytesIO(b""), 0,)

    # Make the Spark call
    spark_caller(job_args)

    # Remove the _SUCCESS file from the  spark job results
    minio_client.remove_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/regressed-"+minioString(job["step"])+"/_SUCCESS")

    # Insert the regressed data in MongoDB
    regression_job_record = {"minio-path":analysis_bucket, "directory-kind":"regressed-data", "job-json":job}
    insertMongoRecord(minioString(playbook["database-id"]), "analysis_"+minioString(playbook["analysis-id"]), regression_job_record)

    # Contact front end for the ending of the job
    diastema_call(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"]), "regression")

    # Return the bucket that this job made output to 
    return analysis_bucket

# Clustering Job
def clustering(playbook, job, last_bucket, algorithm=False, tensorfow_algorithm=False):
    """
    A function to handle a Clustering Analysis Job from the Diastema JSON playbook.
    It will setup the folders needed for the spark jobs in the MinIO Database.
    Then it will call the Spark Job after configuring the way that the job must be called.
    After the above, it will use the MongoDB to save the path and the whole job in the needed analysis collection.

    Args:
        - playbook (JSON): The Diastema playbook.
        - job (JSON): The Data Loading Job from the Diastema playbook.
        - last_bucket (String): The path that the non analyzed data are saved.
        - algorithm (String): The algorithm to run.
        - tensorfow_algorithm (String): A tensorflow algorithm to run.

    Returns:
        - MinIO path (String): The path that the analyzed data are saved.
    """
    # All the available spark clustering jobs 
    spark_files = {
        "k-means clustering" : "/root/diastema-jobs/clustering/kmeans.py",
        "generalized linear regression" : "/root/spark-job/clustering-job-2.py",   # Not imported yet
        "decision tree regression" : "/root/spark-job/clustering-job-3.py",        # Not imported yet
        "random forest regression" : "/root/spark-job/clustering-job-4.py",        # Not imported yet
        "gradient-boosted tree regression" : "/root/spark-job/clustering-job-5.py" # Not imported yet
    }

    # Get the spark algorithm to run
    job_to_run = ""
    if algorithm==False:
        job_to_run = list(spark_files.values())[0]
    else:
        job_to_run = spark_files[algorithm]

    # Data Bucket = last jobs output bucket
    data_bucket = last_bucket

    # Analysis Bucket = User/analysis-id/job-step
    analysis_bucket = minioString(playbook["database-id"])+"/analysis-"+minioString(playbook["analysis-id"])+"/clustered-"+minioString(job["step"])

    # Jobs arguments
    job_args = [job_to_run, data_bucket, analysis_bucket, job["column"]]

    # Make the MinIO Analysis buckets
    minio_client.put_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/clustered-"+minioString(job["step"])+"/", io.BytesIO(b""), 0,)

    # Make the Spark call
    spark_caller(job_args)

    # Remove the _SUCCESS file from the  spark job results
    minio_client.remove_object(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"])+"/clustered-"+minioString(job["step"])+"/_SUCCESS")

    # Insert the clustered data in MongoDB
    clustering_job_record = {"minio-path":analysis_bucket, "directory-kind":"clustered-data", "job-json":job}
    insertMongoRecord(minioString(playbook["database-id"]), "analysis_"+minioString(playbook["analysis-id"]), clustering_job_record)

    # Contact front end for the ending of the job
    diastema_call(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"]), "clustering")

    # Return the bucket that this job made output to 
    return analysis_bucket

# Visualization job
def visualize(playbook, job, last_bucket):
    """
    A function to handle a Vizualization Job from the Diastema JSON playbook.

    Args:
        - playbook (JSON): The Diastema playbook.
        - job (JSON): The Data Loading Job from the Diastema playbook.
        - last_bucket (String): The path that the non analyzed data are saved.

    Returns:
        - testing-value (String): A value that will have a perpose after the Diastema visualization framework is ready.
    """
    print("There has not been any confirmation of what to give to the front-end yet!")

    # Contact front end for the ending of the job
    diastema_call(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"]), "visualization")

    return "visualization-from: "+last_bucket

""" Functions used for the json handling """
# Request a job
def job_requestor(job_json, files_dict, jobs_anwers_dict, playbook):
    """
    A function to handle a Vizualization Job from the Diastema JSON playbook.

    Args:
        - job_json (JSON): The job to request to be done.
        - files_dict (Dictionary): A Dictionary with every file, given by the front-end request.
        - jobs_anwers_dict (Dictionary): A dictionary holding all the return values of every 
            Diastema job done in the given analysis so far.
        - playbook (JSON): The Diastema playbook.

    Returns:
        - Nothing.
    """
    title = job_json["title"]
    step = job_json["step"]
    from_step = job_json["from"]
    
    if(title == "data-load"):
        jobs_anwers_dict[step] = data_load(playbook, job_json, files_dict, job_json["files"])
    
    if(title == "cleaning"):
        jobs_anwers_dict[step] = cleaning(playbook, job_json, jobs_anwers_dict[from_step], max_shrink = job_json["max-shrink"])
    
    if(title == "classification"):
        jobs_anwers_dict[step] = classification(playbook, job_json, jobs_anwers_dict[from_step], algorithm = job_json["algorithm"])
    
    if(title == "regression"):
        jobs_anwers_dict[step] = regression(playbook, job_json, jobs_anwers_dict[from_step], algorithm = job_json["algorithm"])
    
    if(title == "clustering"):
        jobs_anwers_dict[step] = clustering(playbook, job_json, jobs_anwers_dict[from_step], algorithm = job_json["algorithm"])
    
    if(title == "visualize"):
        jobs_anwers_dict[step] = visualize(playbook, job_json, jobs_anwers_dict[from_step])
    
    return

# Access jobs by viewing them Depth-first O(N)
def jobs(job_step, jobs_dict, files, jobs_anwers_dict, playbook):
    """
    A Depth first recursive function, running every job of the Diastema analysis.

    Args:
        - job_step (Integer): The step of the job to parse.
        - jobs_dict (Dictionary): A Dictionary with every job from the requests.
        - files (Dictionary): A Dictionary with every file, given by the front-end request
        - jobs_anwers_dict (Dictionary): A dictionary holding all the return values of every 
            Diastema job done in the given analysis so far.
        - playbook (JSON): The Diastema playbook.

    Returns:
        - Nothing.
    """
    # Make the job request
    job_requestor(jobs_dict[job_step], files, jobs_anwers_dict, playbook)
    
    # Depth-first approach
    next_steps = jobs_dict[job_step]["next"]
    for step in next_steps:
        if(step != 0):  # If ther is no next job then do not try to go deeper
            jobs(step, jobs_dict, files, jobs_anwers_dict, playbook)
    return

# Handle the playbook
def handler(json_jobs, playbook, raw_files):
    """
    A function to handle and run the Diastema playbook.

    Args:
        - json_jobs (JSON): The jobs of the playbook.
        - playbook (JSON): The Diastema playbook.
        - raw_files (List): A list of the given files in the Diastema playbook form data.

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
        jobs(starting_job_step, jobs_dict, files, jobs_anwers_dict, playbook)
    
    # Print jobs_anwers_dict for testing purposes
    for job_step, answer in jobs_anwers_dict.items():
        print(job_step, '->', answer)
    
    return

""" Flask endpoints """
# An endpoint for handling and using the JSON playbook
@app.route("/analysis", methods=["POST"])
def analysis():
    """
    An endpoint to handle a Diastema Analysis playbook from start to finish.

    Args:
        - json_jobs (JSON): The jobs of the playbook.
        - playbook (JSON): The Diastema playbook.
        - raw_files (List): A list of the given files in the Diastema playbook form data.

    Returns:
        - responce (Responce): A responce to the central Diastema API Server containing information
            based on the analysis that has been requested.
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
    handler(playbook["jobs"], playbook, files)
    
    """ Dummy Test
    dummy_call = spark_api_host+"/v1/submissions/create"
    dummy_headers = {'Content-Type': 'application/json;charset=UTF-8'}
    dummy_job = "/root/spark-job/load-job.py"
    dummy_appResource = "file:"+dummy_job
    dummy_json = {
        "appResource": dummy_appResource,
        "sparkProperties": {
            "spark.master": "local[*]",
            "spark.eventLog.enabled": "false",
            "spark.app.name": "Spark REST API - PI"
        },
        "clientSparkVersion": "3.1.2",
        "mainClass": "org.apache.spark.deploy.SparkSubmit",
        "environmentVariables": {
            "SPARK_ENV_LOADED": "1"
        },
        "action": "CreateSubmissionRequest",
        "appArgs": [ dummy_job ]
    }
    response = requests.post(dummy_call, json=dummy_json, headers=dummy_headers)
    responce_json = response.json()
    #print("JSON Responce")
    #print(responce_json)
    #print("The driver got was")
    #print(responce_json["submissionId"])

    dummy_call = spark_api_host+"/v1/submissions/status/"+responce_json["submissionId"]

    response = requests.get(dummy_call)
    responce_json = response.json()
    #print("JSON Responce")
    #print(responce_json)
    Dummy Test """

    # Contact front end for the ending of the analysis
    diastema_call(minioString(playbook["database-id"]), "analysis-"+minioString(playbook["analysis-id"]), "analysis")

    # The analysis has been accepted
    return Response(status=202)

""" Flask endpoints - Dummy Spark Endpoints """
# Dummy Spark endpoint for starting a job
@app.route("/v1/submissions/create", methods=["POST"])
def submissions_create():
    headers = request.headers
    #print("Below are the headers")
    #print("Headers: ", headers)
    data = request.json
    #print("Below are your Data")
    #print("JSON Data:",data)
    #print("Below are some important data")
    #print("App resource:",data["appResource"])
    #print("App arguments:",data["appArgs"])
    #print()

    result_json = '{'+\
            '"action" : "CreateSubmissionResponse",'+\
            '"message" : "Driver successfully submitted as driver-20200923223841-0001",'+\
            '"serverSparkVersion" : "2.4.0",'+\
            '"submissionId" : "driver-20200923223841-0001",'+\
            '"success" : true'+\
        '}'
    
    if(data["appArgs"][0].endswith('load-job.py')):
        print("This is a loading job!")
        #print("Data got from:",data["appArgs"][1])
        #print("Data loaded to:",data["appArgs"][2])
    else:
        print("This is not a loading job!")
        #print("Data got from:",data["appArgs"][1])
        #print("Data analyzed to:",data["appArgs"][2])

    # Spark jobs are outputting a _SUCCESS file after their jobs
    minio_path  = data["appArgs"][2].split("/")
    minio_bucket = minio_path[0]
    del minio_path[0]
    minio_object = '/'.join([str(elem) for elem in minio_path])
    minio_success_object = minio_object + "/_SUCCESS"
    minio_results_object = minio_object + "/results.txt"
    minio_client.put_object(minio_bucket, minio_success_object, io.BytesIO(b""), 0)
    minio_client.put_object(minio_bucket, minio_results_object, io.BytesIO(b"results"), 7)

    return Response(result_json, status=200, mimetype='application/json')

# Dummy Spark endpoint checking if a spark job is ready
@app.route("/v1/submissions/status/<driver>", methods=["GET"])
def submissions_status(driver):
    rand = random.random()
    state = ""
    if rand < 0.2:
        state = "FINISHED"
    else:
        state = "RUNNING"
    print(state)

    result_json = '{'+\
            '"action" : "SubmissionStatusResponse",'+\
            '"driverState" : "'+state+'",'+\
            '"serverSparkVersion" : "2.4.0",'+\
            '"submissionId" : "'+driver+'",'+\
            '"success" : true,'+\
            '"workerHostPort" : "192.168.1.1:38451",'+\
            '"workerId" : "worker-20200923223841-192.168.1.2-34469"'+\
        '}'

    return Response(result_json, status=200, mimetype='application/json')

""" Flask endpoints - Dummy Front End Endpoints """
# A dummy endpoint to represent the answer of the front end services
@app.route("/modelling", methods=["POST"])
def modelling():
    return Response(status=200, mimetype='application/json')

""" Flask endpoints - Dummy Diastema API Services Endpoint """
# A dummy endpoint to represent the answer of the data loading and cleaning API Services
@app.route("/data-loading-cleaning-api", methods=["POST"])
def data_loading_cleaning_api():
    print("Cleaning or loading is done")
    #formdata = request.form["minio-input"]
    #print(formdata)
    return Response(status=200, mimetype='application/json')

""" Main """
# Main code
if __name__ == "__main__":
    app.run(debug=True)