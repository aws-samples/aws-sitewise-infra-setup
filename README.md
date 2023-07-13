
# Sitewise Infrastructure Setup

Introducing a powerful Python script designed to simplify resource creation in AWS IoT Sitewise. This flexible solution accepts configurable files, which can be generated manually or automatically using a script. 

With this script, effortlessly generate assets, models, and hierarchies to streamline your AWS IoT Sitewise implementation. The script leverages the boto3 SDK to make API calls and offers modular code that can be split into separate parts for independent execution. 

Empower your AWS IoT Sitewise workflows with this versatile and customizable solution!

**Note: The project serves as a *proof of concept* and is not intended for production use; detailed deployment considerations are provided below for those interested in utilizing it in a production environment.**

## Deployment considerations

1.  If deploying 500+ tags/asset model, please make sure the limit for \"Number
    of properties per asset model\" has been increased accordingly. The
    default limit is 500.

2. The default API Limits for CreateAssetModel and CreateAsset according to the [limits page](https://docs.aws.amazon.com/general/latest/gr/iot-sitewise.html#limits_iot_sitewise) are as follows:
    - Default Request rate for CreateAsset =  50
    - Default Request rate for CreateAssetModel = 10

    to accomodate the above limits the multiprocessing limits in the code are set as follows L
    - Worker limit for CreateAsset at line 767
        ```
        pool = multiprocessing.Pool(processes=45)
        ```
    - Worker limit for CreateAssetModel at line 740
        ```
        pool = multiprocessing.Pool(processes=8)
        ```

3.  When running the script please setup AWS credentials for
    your AWS Account in the system, and please make sure
    the **credentials do not expire before the time it takes to deploy
    all resources** using the script.\
    *For example*, if it takes 20 minutes to deploy resources, and the
    temporary credentials were only valid till 10, the script will fail,
    and you will have to DELETE all resources before deploying again.

4.  If in any case the script **fails** during creation, **do not try to
    run the CREATE flow again**, please run the DELETE flow to make sure
    all resources have been deleted and issues fixed before deploying
    again.

5. Deploying lots of assets (500+) can take time with this script. If you wish to perform a batch deployment, please feel free to split the script into multiple smaller section. Sections of the code can be identified in the MAIN section after line 677 into the following sections:

    - Create Asset Models
    - Create Assets
    - Configure Asset Model Hierarchy
    - Configure Asset Hierarchy

You can split the code into smaller sections, and also use **batch deployment** to split the `assets.json` file in to smaller array json files, and process in batch with the `create_asset()` function

## Script deployement process

### 1. Initiate a venv and install requirements.

```
python3 -m venv .venv && \
    source .venv/bin/activate && \
    pip install -r requirements.txt
```

### 2. Copy Config Files into the sitewise_config folder :

- asset_hierarchy.json
- assets.json
- model_hierarchy.json
- models.json

More information on config files can be found below .. 

### 3. Run the script to create Resources

```
python3 sw_infra.py CREATE
```

### 4. Run the script to delete Resources

```
python3 sw_infra.py DELETE
```

## How to add resources to sitewise_config files?

Sample config files can be found in the `sitewise_config` folder

### 1. Add new model to `models.json` config file

```
{
    "model_name": "ModelName",
    "model_description": "Model Description",
    "attributes": [{
        "name": "AttributeName",
        "data_type": "STRING",
        "default_value": "DEFAULT"
    }],
    "measurements": [{
        "name": "Temperature (Celsius)",
        "data_type": "DOUBLE",
        "unit": "Celsius",
        "forward_config_state": "ENABLED"
    }],
    "transforms": [{
        "name": "Temperature (Fahrenheit)",
        "data_type": "DOUBLE",
        "unit": "Fahrenheit",
        "expression": "(temperature*1.8)+32",
        "variables": [{
            "name": "temperature",
            "property_logical_id": "Temperature (Celsius)",
            "hierarchy_logical_id": null
        }],
        "forward_config_state": "ENABLED",
        "compute_location": "EDGE"
    }],
    "metrics": [{
        "name": "Average Temperature (Fahrenheit)",
        "data_type": "DOUBLE",
        "unit": "Fahrenheit",
        "expression": "avg(temperature)",
        "variables": [{
            "name": "temperature",
            "property_logical_id": "Temperature (Fahrenheit)",
            "hierarchy_logical_id": null
        }],
        "interval": "5m",
        "offset": null,
        "compute_location": "CLOUD"
    }]

}
```

### 2. Add new model hierarchy `model_hierarchy.json` to config file

```
{
    "parent_asset_model_name": "ParentModelName",
    "child_models": [{
        "child_asset_model_name": "ChildModelName",
        "logical_id": "ParentChildAssetModelHierarchy",
        "name": "ParentChild"
    }]
}
```

### 3. Add new asset to `assets.json` config file

```
{
    "model_name": "ModelName",
    "asset_name": "AssetName",
    "asset_description": "Creating a Parent Test SW Asset",
    "attributes": [{
        "name": "AttributeName",
        "value": "asset attribute value"
    }],
    "measurements": [{
        "name": "Temperature (Celsius)",
        "logical_id": "ModelNameTemperatureMesurement",
        "alias": "asset/alias",
        "notification_state": "ENABLED"
    }]
}
```

### 4. Add new asset hierarchy to `asset_hierarchy.json` config file

```
{
    "parent_asset_name": "ParentAsset",
    "child_assets": [{
        "child_asset_name": "ChildAsset",
        "logical_id": "ParentChildAssetModelHierarchy"
    }]
}
```

## Contributing and Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

