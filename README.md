vpcgenerate
----
Simple CLI tool to generate configurations for VPCs via CLI.

### Summary
This is a rather simple script that can be used to create configurations for VPC connections on edge routers. We do this by utilizing a CSV file that contains the information that is needed for this. This will eventually be extended to a bigger application but this was a quick way to get something running that has the beginning steps of building that larger portion of an application. 

This is a simple script thats used to create configs for VPC connections on AWS edge routers. The application does this by utilizing a CSV file that contains the information that is needed for this. This should eventually be extended to a bigger application but this was a quick way to get something running that has the beginning steps of building that larger portion of an application.

## Getting Started
The script has a few requirements that are listed within the requirements file. You can install these by utilizing `pip` to install. Once these are installed you are good to begin using the application.

You will need all the information for the VPC outlined in a csv file. Please look at the `template_input.csv` to see what format the tool is expecting. 

You can run `python vpcgenerate.py --help` for a list of things the tool needs and can do.

```
(delme) ❯ ./vpcgenerate.py --help                                                                                                                                                                                                                    vpcgenerate/git/master !+
Usage: vpcgenerate.py [OPTIONS]

Options:
  --json TEXT           URL of JSON to be used
  --csvfile TEXT        File that will be used to generate the configurations.
  --batch / --no-batch  Default is False. If specified this means that all the
                        configs are placed per router instead of a config for
                        each VPC.
  --help                Show this message and exit.


```
**json** = The URL of the JSON output to build the configs from. 

**csvfile** = This is the file that contains all the information. This is pretty explanatory.

**batch** = This may be a little confusing. If you do not place `--batch` within the cli it will create a configuration for **every** VPC file. This will be in the format of `<router>_<name>_<vlan>.cfg`. 

```
├── generated_configs
│   ├── br01.sea01-coin-aws_0001.cfg
│   ├── br01.sea01-coin-aws_0002.cfg
│   ├── br02.sea01-coin-aws_0003.cfg
│   ├── br02.sea01-coin-aws_0004.cfg
│   └── empty.txt
```


This may or may not be want you want to do. By specifying `--batch` within the cli it will only create a config file for each router. All the connections pertaining to that router will be placed in that configuration file. 

```
├── generated_configs
│   ├── br01.sea01.cfg
│   ├── br02.sea01.cfg
│   └── empty.txt
```


For the most part `--batch` should be set or you will have many files.

# JSON
Using JSON is simple. We are able to pull from JSON format by running the following command:

```
python vpcgenerate.py --json "https://url" --batch  
```

The above command will pull all the information from the URL and create those templates.

# API Server

Feel free to spin up the included demo server.

`python3 server.py`

Once the server is up you can use a tool like postman and perform a `PUT` to the URL that  was started. 

Push the following as a test in JSON format:

```json
{"name":"TESTVPC",
"account":1213123,
"ref":"dxlag-strc34",
"vlan":101,
"ipv4_network":"1.1.1.1/24",
"bgp_auth_key":"asdfghhjkljf",
"bgp_community":"65000",
"region_id":"ap-southeast-3"
}
```