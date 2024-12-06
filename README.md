# hosting-api

Python wrapper around the hosting.nl api

It is in beta state and might work or it might not. I am still working on documentation and testing.

## Features
* View registered domain details
* Query DNS records
* Add DNS records
* Delete DNS records

## Requirements
* Python 3.x
* [python3-tld](https://github.com/barseghyanartur/tld) module

## Configuration
There are two steps in configuring the usage of this script:

1. Arranging an API key
2. Configuring the script

### Authentication

#### Howto create an API key
See [the official Hosting.nl documentation](https://hosting.nl/support/beheer-je-api-sleutels/)

### Configure the script
Create a hidden file in your home directory named .hosting-api.ini with the following contents. It should contain the following:

```
[Api]
Url = https://api.hosting.nl
Token = <the Hosting.nl API key retrieved earlier>
```

## Usage
