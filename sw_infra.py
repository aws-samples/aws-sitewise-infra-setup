# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0


import json
import boto3
import botocore
import sys
import time as t
import traceback
import multiprocessing
import itertools
import string
import random
client = boto3.client('iotsitewise')

#################################
# DEFINE TAGS
#################################

tags= {
    "Application": "FOF",
    "CostCenter": "62644"
}

#################################
# DEFINE PATH VARIABLES
#################################

# Define path variables for sitewise config files
models_path= "sitewise_config/models.json"
assets_path= "sitewise_config/assets.json"
model_hierarchy_path= "sitewise_config/model_hierarchy.json"
asset_hierarchy_path= "sitewise_config/asset_hierarchy.json"

# Define path variables for local files
parent_models_path= "created/parent_models.json"
resources_path= "created/resources.json"
asset_hierarchy_mapping_path= "created/asset_hierarchy_mapping.json"
script_assets_path= "created/assets.json"
script_asset_models_path= "created/asset_models.json"
hierarchy_id_mapping_path= "created/hierarchy_id_mapping.json"

#################################
# ADD ELEMENT TO RESOURCES FILE
#################################

def add_resources_element(key, element):
    
    # Read latest version of the file
    with open(resources_path, 'r') as file:
        resources_file = json.load(file)
    
    # Add the element in key
    resources_file[key].append(element)
    
    # Write the updated version back to the file
    with open(resources_path, "w") as outfile:
        outfile.write(json.dumps(resources_file, indent=4))

#################################
# DELETE ELEMENT FROM RESOURCES FILE
#################################

def delete_resources_element(key, element):
    
    # Read latest version of the file
    with open(resources_path, 'r') as file:
        resources_file = json.load(file)
    
    # Delete the element from key
    resources_file[key].remove(element)
    
    # Write the updated version back to the file
    with open(resources_path, "w") as outfile:
        outfile.write(json.dumps(resources_file, indent=4))

#################################
# ADD ELEMENT TO PARENT MODEL FILE
#################################

def add_parent_model_element(element):
    
    # Read latest version of the file
    with open(parent_models_path, 'r') as file:
        parent_models = json.load(file)
    
    # Add the element in key
    parent_models.append(element)
    
    # Write the updated version back to the file
    with open(parent_models_path, "w") as outfile:
        outfile.write(json.dumps(parent_models, indent=4))

#################################
# DELETE ELEMENT FROM PARENT MODEL FILE
#################################

def delete_parent_model_element(element):
    
    # Read latest version of the file
    with open(parent_models_path, 'r') as file:
        parent_models = json.load(file)
    
    # Delete the element from key
    parent_models.remove(element)
    
    # Write the updated version back to the file
    with open(parent_models_path, "w") as outfile:
        outfile.write(json.dumps(parent_models, indent=4))
        
#################################
# ADD ELEMENT TO ASSET HIERARCHY FILE
#################################

def add_asset_hierarchy_mapping_element(element):
    
    # Read latest version of the file
    with open(asset_hierarchy_mapping_path, 'r') as file:
        asset_hierarchy_list = json.load(file)
    
    # Add the element in key
    asset_hierarchy_list.append(element)
    
    with open(asset_hierarchy_mapping_path, "w") as outfile:
        outfile.write(json.dumps(asset_hierarchy_list, indent=4))

#################################
# DELETE ELEMENT FROM ASSET HIERARCHY FILE
#################################

def delete_asset_hierarchy_mapping_element(element):
    
    # Read latest version of the file
    with open(asset_hierarchy_mapping_path, 'r') as file:
        asset_hierarchy_list = json.load(file)
    
    # Add the element in key
    asset_hierarchy_list.remove(element)
    
    with open(asset_hierarchy_mapping_path, "w") as outfile:
        outfile.write(json.dumps(asset_hierarchy_list, indent=4))

#################################
# CREATE MODELS
#################################

def create_asset_model(model):
    
    obj = {}
    
    # Create asset property value array
    asset_property_values = []
    
    # Attributes
    # Iterate through all attributes and add to array
    if  model['attributes'] != []:
        for attribute in model['attributes']:
            asset_property_values.append({
                'name': attribute['name'],
                'dataType': attribute['data_type'],
                'type': {
                    'attribute': {
                        'defaultValue': attribute['default_value']
                    }
                }
            })
    
    # Measurements
    # Iterate through all measurements and add to array
    if  model['measurements'] != []:
        for measurement in model["measurements"]:
            if measurement["unit"]==None:
                measurement["unit"]="None"
            asset_property_values.append({
                'name': measurement['name'],
                'dataType': measurement['data_type'],
                'unit': measurement["unit"],
                'type': {
                    'measurement': {
                        'processingConfig': {
                            'forwardingConfig': {
                                'state': measurement['forward_config_state']
                            }
                        }
                    }
                }
            })
    
    # Transforms 
    # Iterate through all transformations and add to array
    if  model['transforms'] != []:
        for transform in model['transforms']:
            
            variables = []
            for variable in transform['variables']:
                variables.append({
                    'name': variable['name'],
                    'value': {
                        'propertyId': variable['property_logical_id']
                    }
                })
            if measurement["unit"]==None:
                measurement["unit"]="None"
            asset_property_values.append({
                'name': transform['name'],
                'dataType': transform['data_type'],
                'unit': transform['unit'],
                'type': {
                    'transform': {
                        'expression': transform['expression'],
                        'variables': variables,
                        'processingConfig': {
                            'computeLocation': transform['compute_location'],
                            'forwardingConfig': {
                                'state': transform['forward_config_state'],
                            }
                        }
                    }
                }
            })
    
    # Metrics
    if  model['metrics'] != []:
        for metric in model['metrics']:
            
            # Define array of variables
            variables = []
            for variable in metric['variables']:
                variables.append({
                    'name': variable['name'],
                    'value': {
                        'propertyId': variable['property_logical_id']
                    }
                })
            
            # Append metric
            if metric['offset']!= None:
                asset_property_values.append({
                    'name': metric['name'],
                    'dataType': metric['data_type'],
                    'unit': metric['unit'],
                    'type': {
                        'metric': {
                            'expression': metric['expression'],
                            'variables': variables,
                            'window': {
                                'tumbling': {
                                    'interval': metric['interval'],
                                    'offset': metric['offset']
                                }
                            },
                            'processingConfig': {
                                'computeLocation': metric['compute_location']
                            }
                        }
                    }
                })
            else:
                asset_property_values.append({
                    'name': metric['name'],
                    'dataType': metric['data_type'],
                    'unit': metric['unit'],
                    'type': {
                        'metric': {
                            'expression': metric['expression'],
                            'variables': variables,
                            'window': {
                                'tumbling': {
                                    'interval': metric['interval']
                                }
                            },
                            'processingConfig': {
                                'computeLocation': metric['compute_location']
                            }
                        }
                    }
                })
    
    # Error handling of the create model API Call
    try:
        # Create Model
        create_asset_model_response = client.create_asset_model(
            assetModelName= model['model_name'],
            assetModelDescription= model['model_description'],
            assetModelProperties= asset_property_values,
            tags=tags
        )
        
        # Add asset model to list of assets
        add_resources_element("asset_models", create_asset_model_response["assetModelId"])
        
        # Add asset model to return dictionary
        obj[model['model_name']]= create_asset_model_response
    
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'InternalError': # Generic error
            # We grab the message, request ID, and HTTP code to give to customer support
            print('Error Message: {}'.format(err.response['Error']['Message']))
            print('Request ID: {}'.format(err.response['ResponseMetadata']['RequestId']))
            print('Http code: {}'.format(err.response['ResponseMetadata']['HTTPStatusCode']))
        
        elif err.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            # print('Error Message: {}'.format(err.response['Error']['Message']))
            print("\tResource already exists!")
        else:
            print(str(err) + "\n")
    
    t.sleep(1)
    
    return obj


#################################
# DELETE MODELS
#################################

def delete_asset_models(resources_file):  
    
    for asset_model in resources_file["asset_models"]:
       
        print("\tNow deleting asset model: "+ asset_model)
        
        # Error handling of the delete model API Call
        try:
            # Remove model from cloud
            delete_asset_model_response = client.delete_asset_model(
                assetModelId= asset_model
            )
            
            # Remove model id from resources file
            delete_resources_element("asset_models", asset_model)
            
        except botocore.exceptions.ClientError as err:
            print(str(err) + "\n")
        
        t.sleep(0.5)
    
#################################
# CREATE ASSETS
#################################
def return_elements(list_asset_properties_response, assetId):
    arr=[]
    # Get property id and then find out the name of the property
    for assetPropertySummary in list_asset_properties_response["assetPropertySummaries"]:
        describe_asset_property_response = client.describe_asset_property(
            assetId= assetId,
            propertyId= assetPropertySummary['id']
        )
        arr_input= {}
        arr_input["assetName"]= describe_asset_property_response["assetName"]
        arr_input["assetId"]= describe_asset_property_response["assetId"]
        arr_input["propertyId"]= describe_asset_property_response["assetProperty"]["id"]
        arr_input["assetPropertyName"]= describe_asset_property_response["assetProperty"]["name"]
        arr.append(arr_input)
    return arr

def create_asset(asset, asset_models):
    
    obj = {}
    
    print("\tCreating Asset: " + str(asset['asset_name']))
    # Error handling of the create asset API Call
    try:
        asset_model_id= asset_models[asset['model_name']]['assetModelId']
        
        create_asset_response = client.create_asset(
            assetName= asset['asset_name'],
            assetModelId= asset_model_id,
            tags=tags,
            assetDescription='Creating a SW Asset'
        )
        # Add asset to list of assets created
        add_resources_element("assets", create_asset_response["assetId"])
        
        # Add asset to return dictionary
        obj[asset['asset_name']]= create_asset_response
        
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            # print('Error Message: {}'.format(err.response['Error']['Message']))
            print("Resource already exists!")
        else:
            print(str(err) + "\n")
    
    t.sleep(2)
    
    # establish array to store all measurments property data
    json_arr=[]
    
    # First API call without nextToken
    list_asset_properties_response = client.list_asset_properties(
        assetId= create_asset_response["assetId"],
        maxResults= 250
    )
    # Add elements in resonse to array
    for element in return_elements(list_asset_properties_response, create_asset_response["assetId"]):
        json_arr.append(element)
        
    # Check if there was a next token
    while "nextToken" in list_asset_properties_response:
        # Make api call again with next token
        list_asset_properties_response = client.list_asset_properties(
            assetId= create_asset_response["assetId"],
            nextToken= list_asset_properties_response["nextToken"],
            maxResults= 250
        )
        # Add elements in resonse to array
        for element in return_elements(list_asset_properties_response, create_asset_response["assetId"]):
            json_arr.append(element)
    
    # print(len(json_arr))
    
    # Iterate through measurement, find property id of measurement, and update asset property with alias
    if  asset['measurements'] != []:
        for measurement in asset["measurements"]:
            for json_element in json_arr:
                if measurement["name"]==json_element["assetPropertyName"]:
                    # Make sure asset is done creating
                    t.sleep(5)
                    try:
                        update_asset_property_response = client.update_asset_property(
                            assetId= json_element["assetId"],
                            propertyId= json_element["propertyId"],
                            propertyAlias= measurement["alias"],
                            propertyNotificationState= measurement["notification_state"]
                        )
                    except botocore.exceptions.ClientError as err:
                        if err.response['Error']['Code'] == 'ConflictingOperationException':
                            print("\t\tTrying to add asset to alias data stream")
                            try:
                                # Run the update stream code
                                response = client.associate_time_series_to_asset_property(
                                    alias= measurement["alias"],
                                    assetId= json_element["assetId"],
                                    propertyId= json_element["propertyId"]
                                )
                                update_asset_property_response = client.update_asset_property(
                                    assetId= json_element["assetId"],
                                    propertyId= json_element["propertyId"],
                                    propertyAlias= measurement["alias"],
                                    propertyNotificationState= measurement["notification_state"]
                                )
                                print("\t\tAsset added to alias data stream")
                            except botocore.exceptions.ClientError as err:
                                print(str(err) + "\n")
                        else:
                            print(str(err) + "\n")
                    
                    # Break loop as we've found our match
                    break
    if  asset['attributes'] != []:
        for attribute in asset["attributes"]:
            for json_element in json_arr:
                if attribute["name"]==json_element["assetPropertyName"]:
                    try:
                        
                        # Check what type of entry is in the config file
                        if type(attribute["value"]) is str:
                            val={
                                "stringValue": attribute["value"]
                            }
                        elif type(attribute["value"]) is int:
                            val={
                                "integerValue": attribute["value"]
                            }
                        elif type(attribute["value"]) is float:
                            val={
                                "doubleValue": attribute["value"]
                            }
                        elif type(attribute["value"]) is bool:
                            val={
                                "booleanValue": attribute["value"]
                            }
                        
                        # Create entry json payload
                        entry={
                            "entryId": asset["asset_name"] + "-" + attribute["name"] + "-" + ''.join(random.choices(string.ascii_lowercase +
                                string.digits, k = 7)),
                            "assetId": json_element["assetId"],
                            "propertyId": json_element["propertyId"],
                            "propertyValues": [{
                                "value": val,
                                "timestamp": {
                                    "timeInSeconds": int(t.time())
                                }
                            }]
                        }
                        entries=[]; entries.append(entry)
                        
                        # Make the BatchPutAssetPropertyValue API call to add attribute value
                        batch_put_asset_property_value_response = client.batch_put_asset_property_value(
                            entries=entries
                        )
                        
                    except botocore.exceptions.ClientError as err:
                        print(str(err) + "\n")
                    # Break loop as we've found our match
                    break
    return obj

#################################
# DELETE ASSETS
#################################

def delete_assets(resources_file):
    
    for asset in resources_file['assets']:
        
        print("\tNow deleting asset: "+ asset)
        
        # Error handling of the delete asset API Call
        try:
            # Remove asset from cloud
            response = client.delete_asset(
                assetId= asset
            )
            
            # Remove model id from resources file
            delete_resources_element("assets", asset)
            
        except botocore.exceptions.ClientError as err:
            print(str(err) + "\n")
        
        t.sleep(0.5)
            
#################################
# Model Hierarchy
#################################

def create_model_hierarchy(model_hierarchy_path, asset_models, parent_models_path):
    
    # Load the json objects file into variable
    with open(model_hierarchy_path, 'r') as file:
        model_hierarchies= json.load(file)
        
    # Dictionary of model hierarchy name and hoerarchy if
    hierarchy_id_mapping= {}
        
    # Iterate through all the model hierarchy in the JSON
    for model_hierarchy in model_hierarchies: 
        
        # array of asset model hierarchy properties
        json_arr= []
        
        # Fetch model Id of parent model
        parent_asset_model_id= asset_models[model_hierarchy['parent_asset_model_name']]["assetModelId"]
        
        # Make describe call to get current config
        describe_asset_model_response = client.describe_asset_model(
            assetModelId= parent_asset_model_id,
            excludeProperties= False
        )
        parent_asset_model_name= describe_asset_model_response["assetModelName"]
        parent_asset_model_description= describe_asset_model_response["assetModelDescription"]
        parent_asset_model_properties= describe_asset_model_response["assetModelProperties"]
    
                    
        if model_hierarchy['child_models'] != []:
            for child_model in model_hierarchy['child_models']:
                
                # Fetch model Id of child model 
                child_asset_model_id= asset_models[child_model["child_asset_model_name"]]["assetModelId"]
                
                json_arr_input= {}
                json_arr_input["name"]= child_model["name"]
                json_arr_input["childAssetModelId"]= child_asset_model_id
                json_arr.append(json_arr_input)
            
            
            # print("Parent Model: "+ str(parent_asset_model_id) + "\nChild Models:\n"+ str(json_arr))
            # Update model with current + hierarchy setting
            
            # Error handling of the update asset modelAPI Call
            try:
                response = client.update_asset_model(
                    assetModelId= parent_asset_model_id,
                    assetModelName= parent_asset_model_name,
                    assetModelDescription= parent_asset_model_description,
                    assetModelProperties= parent_asset_model_properties,
                    assetModelHierarchies= json_arr
                )
                
                # Add parent model to parent models list
                add_parent_model_element(parent_asset_model_id)
                t.sleep(5)
                
                # Make describe call to get current config
                describe_asset_model_response = client.describe_asset_model(
                    assetModelId= parent_asset_model_id,
                    excludeProperties= True
                )
                
                parent_asset_model_hierarchies= describe_asset_model_response["assetModelHierarchies"]
                # Get all the assetModelHierarchies. Create a mapping of logical Id and hierarchy id 
                for child_model in model_hierarchy['child_models']:
                    for asset_model_hierarchy in parent_asset_model_hierarchies:
                        
                        # Map the logical id from config file with the hierarchy id of the model in SW
                        if child_model["name"]==asset_model_hierarchy["name"]:
                            hierarchy_id_mapping[child_model["logical_id"]]=asset_model_hierarchy["id"]
                            break
            except botocore.exceptions.ClientError as err:
                print(str(err) + "\n")  
                
    # Return this back to use for asset association
    return hierarchy_id_mapping    

def delete_model_hierarchy(parent_models):
    
    for model in parent_models:
        
        # Error handling of the update asset model API Call to remove hierarchy
        try:
            describe_asset_model_response = client.describe_asset_model(
                assetModelId= model
            )
            
            update_asset_model_response = client.update_asset_model(
                assetModelId= describe_asset_model_response["assetModelId"],
                assetModelName= describe_asset_model_response["assetModelName"],
                assetModelDescription= describe_asset_model_response['assetModelDescription'],
                assetModelProperties= describe_asset_model_response["assetModelProperties"],
                assetModelHierarchies= []
            )
            delete_parent_model_element(model)
        except botocore.exceptions.ClientError as err:
            print(str(err) + "\n")  
        
        t.sleep(0.5)
        
#################################
# Asset Hierarchy
#################################

def create_asset_hierarchy(asset_hierarchy_path, hierarchy_id_mapping, assets):

    # Load the json objects file into variable
    with open(asset_hierarchy_path, 'r') as file:
        asset_hierarchies= json.load(file)
    
    asset_hierarchy_list=[]
    
    for asset_hierarchy in asset_hierarchies:
        
        # Fetch asset Id of parent asset
        parent_asset_id= assets[asset_hierarchy['parent_asset_name']]["assetId"]
        
        if asset_hierarchy['child_assets'] != []:
            for child_asset in asset_hierarchy['child_assets']:
                
                json_element= {}
                
                # Get hierarchy id for given logical id
                hierarchy_id= hierarchy_id_mapping[child_asset['logical_id']]
                # Get asset id of child asset
                child_asset_id= assets[child_asset['child_asset_name']]["assetId"]
                
                # Error handling of the associate assets API Call to remove hierarchy
                try:
                    associate_assets_response = client.associate_assets(
                        assetId= parent_asset_id,
                        hierarchyId= hierarchy_id,
                        childAssetId= child_asset_id
                    )
                except botocore.exceptions.ClientError as err:
                    print(str(err) + "\n")      
                
                # Add associated asset info to array element
                json_element["assetId"]= parent_asset_id
                json_element["hierarchyId"]= hierarchy_id
                json_element["childAssetId"]= child_asset_id
                
                #  Add element to asset hierarchy mapping file
                add_asset_hierarchy_mapping_element(json_element)
                
                t.sleep(1)
                
    return asset_hierarchy_list

def delete_asset_hierarchy(asset_hierarchy_list):
    for asset_hierarchy in asset_hierarchy_list:
        try:
            disassociate_assets_response = client.disassociate_assets(
                assetId= asset_hierarchy["assetId"],
                hierarchyId= asset_hierarchy["hierarchyId"],
                childAssetId= asset_hierarchy["childAssetId"]
            )
            delete_asset_hierarchy_mapping_element(asset_hierarchy)
        except botocore.exceptions.ClientError as err:
            print(str(err) + "\n")      
            
        t.sleep(0.5)
        
#################################
# MAIN
#################################

if str(sys.argv[1]).upper()=='CREATE':

    #################################
    # CREATE 
    #################################
    
    
    ##
    # Get confirmation that only new resources are being created
    ##
    answer = None 
    while answer not in ("yes", "no"): 
        answer = input("Have you made sure that resources that you are about to deploy do not already exist in this account?\nEnter yes or no: ") 
        if answer == "yes": 
            continue 
        elif answer == "no": 
            print("Exiting ... ")
            exit(0) 
        else: 
        	print("Please enter yes or no.") 
    
    ##
    # Initiate empty resources file
    ##
    print("Initiating Resources File")
    resources= {
        "asset_models": [],
        "assets": []
    }
    with open(resources_path, "w") as outfile:
        outfile.write(json.dumps(resources, indent=4))
    
    ##
    # Create Asset Models
    ##
    print("Creating Asset Models ... ")
     # Open models file from sitewise config files 
    with open(models_path, 'r') as file:
        models = json.load(file)
    begin = t.time()
    # Establish multiprocessing pool object
    pool = multiprocessing.Pool(processes=8)
    # Created all assets in parallel
    created_asset_models= pool.starmap(create_asset_model, zip(models))
    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()
    end = t.time()
    print(f"\nTotal runtime to Create all Asset Models is {end - begin}\n")
    # Convert list to object 
    script_asset_models= {k: v for item in created_asset_models for k, v in item.items() if v}
    # Update models file
    with open(script_asset_models_path, "w") as outfile:
        outfile.write(json.dumps(script_asset_models, indent=4))
    t.sleep(5)
    
    ##
    # Create Assets
    ##
    print("Creating Assets ... ")
    # Load existing models file
    with open(script_asset_models_path, 'r') as file:
        script_asset_models = json.load(file)
    # Load assets config file
    with open(assets_path, 'r') as file:
        assets= json.load(file)
    begin = t.time()
    # Establish multiprocessing pool object
    pool = multiprocessing.Pool(processes=45)
    # Created all assets in parallel
    created_assets= pool.starmap(create_asset, zip(assets, itertools.repeat(script_asset_models)))
    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()
    end = t.time()
    print(f"\nTotal runtime to Create all Assets is {end - begin}\n")
    # Convert list to object 
    script_assets= {k: v for item in created_assets for k, v in item.items()  if v}
    # Update assets file
    with open(script_assets_path, "w") as outfile:
        outfile.write(json.dumps(script_assets, indent=4))
    
    ##
    # Configure Asset Model Hierarchy
    ##
    # Initiate empty parent models file
    with open(parent_models_path, "w") as outfile:
        outfile.write(json.dumps([], indent=4))
    print("Adding Model Hierarchy ... ")
    with open(script_asset_models_path, 'r') as file:
        script_asset_models = json.load(file)
    hierarchy_id_mapping= create_model_hierarchy(model_hierarchy_path, script_asset_models, parent_models_path)
    # Writing to hierarchy_id_mapping.json
    with open(hierarchy_id_mapping_path, "w") as outfile:
        outfile.write(json.dumps(hierarchy_id_mapping, indent=4))
    t.sleep(5)
    
    ##
    # Configure Asset Hierarchy
    ##
    print("Adding Asset Hierarchy ... ")
    with open(script_assets_path, 'r') as file:
        script_assets = json.load(file)
    with open(hierarchy_id_mapping_path, 'r') as file:
        hierarchy_id_mapping = json.load(file)
    asset_hierarchy_list= create_asset_hierarchy(asset_hierarchy_path, hierarchy_id_mapping, script_assets)
    
    print("Done!")
    
    print("\n\n*********")
    print("\nNOTE: If this deployment has FAILED, make sure to run the DELETE flow, and make sure all resources from this deployment have been removed BEFORE trying again.")
    print("\n*********\n")

elif str(sys.argv[1]).upper()=='DELETE':
    #################################
    # DELETE 
    #################################
    
    
    ##   
    # Remove Asset Hierarchy
    ##
    # Fetch all the hierarchy from hierarchy file
    # Fetch all the parent models from parent model file
    with open(asset_hierarchy_mapping_path, 'r') as file:
        asset_hierarchy_list = json.load(file)
    print("Removing Asset Hierarchy ... ")
    delete_asset_hierarchy(asset_hierarchy_list)
    t.sleep(10)
    
    ##
    # Remove Model Hierarchy
    ##
    with open(parent_models_path, 'r') as file:
        parent_models = json.load(file)
    print("Removing Model Hierarchy ... ")
    delete_model_hierarchy(parent_models)
    # Writing empty hierarchy_id_mapping.json
    with open(hierarchy_id_mapping_path, "w") as outfile:
        outfile.write(json.dumps({}, indent=4))
    t.sleep(10)
    
    # Fetch list of all resources from resources file
    with open(resources_path, 'r') as file:
        resources_file = json.load(file)
        
    
    ##
    # Delete Assets
    ##
    print("Removing Assets ... ")
    delete_assets(resources_file)
    # Writing empty assets.json
    with open(script_assets_path, "w") as outfile:
        outfile.write(json.dumps({}, indent=4))
    t.sleep(10)
    
    ##
    # Delete Asset Models
    ##
    print("Removing Models ... ")
    delete_asset_models(resources_file)
    with open(script_asset_models_path, "w") as outfile:
        outfile.write(json.dumps({}, indent=4))
    
    print("Done!")