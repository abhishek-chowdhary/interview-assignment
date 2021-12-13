from service.ecs.common.session import get_session
from service.ecs.common.file_read import read_file
from multiprocessing import Process,Manager
import json

# Fetch cluster details and return json list

def ecs_cluster_opertaions(account_details,result_list):
    '''
        Inputs - Account details which contain aws creds and account name and Final result list 
        Loop over all aws account and then create 
    '''
    #Creating aws client session     
    session = get_session(account_details)
    account_dict = {}
    account_dict["account_name"] = account_details["aws_account_name"]
    
    #Boto3 ecs client 
    ecs_client = session.client('ecs')
    account_dict["clusters"] = []

    #Fetching the list of ecs cluster  
    list_clusters = ecs_client.list_clusters()["clusterArns"]

    #Looping over the ecs clusters
    for cluster_arn in list_clusters:

            #creating a dict to store ecs cluster service details
            cluster_dict = dict()
            cluster_dict["clusterArn"] = cluster_arn
            cluster_dict["services"] = []

            #Fetching list of services in a cluster
            serviceArns = ecs_client.list_services(cluster= cluster_arn, launchType= 'EC2')["serviceArns"]
            
            #if service exist then describing the service
            if serviceArns:
                svc_response = ecs_client.describe_services(services = serviceArns, cluster= cluster_arn)

                #Looping over different services in a ecs cluster
                for svc in svc_response["services"]:
                    
                    #if service is active then scaling down the task to 0
                    if svc["status"] == "ACTIVE":
                        ecs_client.update_service(service=svc["serviceArn"], cluster=cluster_arn, desiredCount=0)

                    #creating dict to store svc details of an ecs cluster
                    svc_dict = dict()
                    svc_dict[svc["serviceArn"]] = {}
                    svc_dict[svc["serviceArn"]]["status"] = svc["status"]
                    svc_dict[svc["serviceArn"]]["desiredCountBefore"] = svc["desiredCount"]
                    
                    #fetching desiredcount after update service call in ecs to scale down the task to 0
                    svc_response_after = ecs_client.describe_services(services=[svc["serviceArn"]],
                                                                     cluster=cluster_arn)                                                                   
                    desired_count_after = svc_response_after["services"][0]["desiredCount"]
                    svc_dict[svc["serviceArn"]]["desiredCountAfter"] = desired_count_after

                    #appending all collated data to cluster dict
                    cluster_dict["services"].append(svc_dict)

            else:
                print(f"No running services in {cluster_arn}")
            
            #appending all clusters data to account dict
            account_dict["clusters"].append(cluster_dict)

    #storing all account and svc data to final result list
    result_list.append(account_dict)


def final_result(path):

    #Creating process to run mulitple sessions and work in parallel
    processes = []
    manager = Manager()
    account_desc = manager.list()
    
    #For creating multiple process for creating multiple session to different account and fetch details
    for account_detail in read_file(path):
        process = Process(target=ecs_cluster_opertaions, args=(account_detail,account_desc))
        processes.append(process)
    
    #Starting the process
    for process in processes:
        process.start()

    #Joining the process to make them work together by waiting for other process to finish
    for process in processes:
        process.join()        
    
    #Writing all the data to account_service_status json file   
    with open("account_service_status.json", "w") as file:
        json.dump(list(account_desc),file,indent=2)