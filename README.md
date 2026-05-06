# KooCLI

Koo Command Line Interface (KooCLI) is a command line tool built based on HUAWEI CLOUD API. The owner of the software is the current user. You can use this tool to call HUAWEI CLOUD API to manage your HUAWEI CLOUD resources. The commands provided by this tool correspond to HUAWEI CLOUD API.

## Features

KooCLI is developed based on the Go language. It parses and executes commands using API as the metadata driver, and interacts with HUAWEI CLOUD API using HTTPS. KooCLI has the following features:
 * A single executable file is provided, which is green and free of installation. You can use KooCLI after decompressing the executable file.
 * Multiple OSs, including Linux, Windows, and macOS, are supported.
 * It is easy to expand. You can use this tool to encapsulate HUAWEI CLOUD API and expand functions as required.

## Use

Example for using KooCLI
 * Lists system-level help information.
    hcloud --help   
 * Lists help information about the configuration function.
    hcloud configure --help   
 * Initializes configurations.
    hcloud configure init   
 * Lists available APIs of a service.
    hcloud ECS --help  
 * Lists parameters of an API.
    hcloud ECS NovaListServers --help  
 * Calls an API after initializing configurations.
    hcloud ECS NovaListServers --cli-profile=default 
 * Calls an API when the configurations are not initialized.
    hcloud ECS NovaListServers --cli-region=region --cli-access-key=accessKey --cli-secret-key=secretKey  
    
For more information, see KooCLI [User Guide](https://support.huaweicloud.com/intl/en-us/productdesc-hcli/hcli_01.html).

## Set parameters

According to the HUAWEI CLOUD API usage specifications, the following personal data must be configured to ensure the normal use of KooCLI:
 * cli-profile: name of a profile. KooCLI supports multiple profiles, which are distinguished by the profile name.
 * cli-mode: supports AKSK|ecsAgency authentication. AKSK authentication is recommended.
 * [cli-project-id](https://support.huaweicloud.com/intl/en-us/usermanual-hcli/hcli_09_002.html): project ID.
 * [cli-region](https://support.huaweicloud.com/intl/en-us/usermanual-hcli/hcli_09_003.html): region.
 * [cli-domain-id](https://support.huaweicloud.com/intl/en-us/usermanual-hcli/hcli_09_002.html): ID of the account to which the IAM user belongs.
 * [cli-access-key](https://support.huaweicloud.com/intl/en-us/usermanual-hcli/hcli_09_001.html):
 An access key ID (AK) is your long-term identity credential on HUAWEI CLOUD. You can use an AK to sign requests for calling HUAWEI CLOUD APIs. An AK is used together with an SK to sign requests cryptographically, ensuring that the requests are secret, complete, and correct.
 * [cli-secret-key](https://support.huaweicloud.com/intl/en-us/usermanual-hcli/hcli_09_001.html):
 A secret access key (SK) is your long-term identity credential on HUAWEI CLOUD. An AK is used together with an SK to sign requests cryptographically, ensuring that the requests are secret, complete, and correct.
 * [cli-security-token](https://support.huaweicloud.com/intl/en-us/usermanual-hcli/hcli_09_005.html): temporary token obtained by a user, which must be used together with the temporary AK/SK.
 

The preceding information is required for API authentication and is transparently transmitted to HUAWEI CLOUD API Gateway when KooCLI calls APIs. You can run the configure command to encrypt the preceding information and save the encrypted information to the config.json file in the home directory of the current user. By default, the information is permanently stored unless you run the configure command to delete the information or directly delete the config.json file. You can also directly enter related configurations in the command to call an API without saving them locally.

The configuration information is stored in the following path:
 * Linux OS: /home/{Current username}/.hcloud/config.json
 * Windows OS: C:\Users\{Current username}\.hcloud\config.json
 * macOS: /Users/{Current username}/.hcloud/config.json

## Logs

Error information generated when KooCLI is used is logged. If none of the parameters are specified, the default log level is error, a single log file is 20 MB, and 3 files are retained.

You can modify log configurations by setting the following parameters:
 * level: log level, which can be info, warning, or error.
 * max-file-size: maximum size (MB) of a single log file. Range: 1 to 100. Default value: 20.
 * max-file-num: the number of retained log files. The value 0 indicates that all log files are retained. Default value: 3.
 * retention-period: the number of days for retaining log files. The value 0 indicates that log files are retained permanently.

Logs are stored in the following directory:
 * Linux OS: /home/{Current username}/.hcloud/log
 * Windows OS: C:\Users\{Current username}\.hcloud\log
 * macOS: /Users/{Current username}/.hcloud/log

## User Guide

 * [User Guide](https://support.huaweicloud.com/intl/en-us/productdesc-hcli/hcli_01.html)
