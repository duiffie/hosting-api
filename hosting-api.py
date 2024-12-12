#!/usr/bin/python3
# pylint: disable=invalid-name,line-too-long

"""
File: hosting-api.py
Author: Marco van Duijvenbode
Date: 06/12/2024

Description: Wrapper around the hosting.nl api
"""

# Built-in/Generic Imports
import argparse
import configparser
import json
import os
import requests
import secrets
import sys

# Libs
import logging as log

# Futures
from argparse import Namespace
from tld import get_fld

def parse_args():  # pylint: disable=too-many-locals,too-many-statements
    """Function parsing arguments"""
    DESCRIPTION = 'Wrapper around the hosting.nl api'
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    subparsers = parser.add_subparsers(required=True)

    # create the parser for the "domain" command
    DESCRIPTION = 'Create/delete/get/update domain objects'
    parser_domain = subparsers.add_parser('domain', description=DESCRIPTION, help=DESCRIPTION)
    domain_subparsers = parser_domain.add_subparsers(required=True)

    # create the parser for the "domain" -> "get" command
    DESCRIPTION = 'Get domain objects'
    parser_domain_get = domain_subparsers.add_parser('get', description=DESCRIPTION, help=DESCRIPTION)
    parser_domain_get.add_argument('-d', '--domain', type=str, help='Domain name')
    parser_domain_get.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser_domain_get.set_defaults(func=domain_get)

    # create the parser for the "record" command
    DESCRIPTION = 'Create/delete/get/update dns records'
    parser_record = subparsers.add_parser('record', description=DESCRIPTION, help=DESCRIPTION)
    record_subparsers = parser_record.add_subparsers(required=True)

    # create the parser for the "record" -> "get" command
    DESCRIPTION = 'Get (a) dns record(s)'
    parser_record_get = record_subparsers.add_parser('get', description=DESCRIPTION, help=DESCRIPTION)
    parser_record_get.add_argument('-d', '--domain', type=str, help='Domain (returns all record(s) in this domain)')
    parser_record_get.add_argument('-i', '--id', type=int, help='Id')
    parser_record_get.add_argument('-n', '--name', type=str, help='Name (returns record(s) matching this name)')
    parser_record_get.add_argument('-t', '--type', type=str, choices=["A", "AAAA", "CAA", "CNAME", "MX", "NAPTR", "NS", "PTR", "SRV", "TLSA", "TXT"], help='Type (returns record(s) matching this type)')
    parser_record_get.add_argument('-c', '--content', type=str, help='Content (returns record(s) matching this content)')
    parser_record_get.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser_record_get.set_defaults(func=record_get)

    # create the parser for the "record" -> "add" command
    DESCRIPTION = 'Add dns records'
    parser_record_add = record_subparsers.add_parser('add', description=DESCRIPTION, help=DESCRIPTION)
    parser_record_add.add_argument('-n', '--name', type=str, help='Name', required=True)
    parser_record_add.add_argument('-t', '--type', type=str, choices=["A", "AAAA", "CAA", "CNAME", "MX", "NAPTR", "NS", "PTR", "SRV", "TLSA", "TXT"], help='Type', required=True)
    parser_record_add.add_argument('-c', '--content', type=str, help='Content', required=True)
    parser_record_add.add_argument('--ttl', type=int, choices=[60, 300, 3600, 86400], default=3600, help='TTL (default: 3600)')
    parser_record_add.add_argument('--prio', type=int, default=0, help='Prio (default: 0)')
    parser_record_add.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser_record_add.set_defaults(func=record_add)

    # create the parser for the "record" -> "upd" command
    DESCRIPTION = 'Update dns records'
    parser_record_upd = record_subparsers.add_parser('upd', description=DESCRIPTION, help=DESCRIPTION)
    parser_record_upd.add_argument('-i', '--id', type=int, help='Id', required=True)
    parser_record_upd.add_argument('-n', '--name', type=str, help='Name', required=True)
    parser_record_upd.add_argument('-t', '--type', type=str, choices=["A", "AAAA", "CAA", "CNAME", "MX", "NAPTR", "NS", "PTR", "SRV", "TLSA", "TXT"], help='New type')
    parser_record_upd.add_argument('-c', '--content', type=str, help='New content')
    parser_record_upd.add_argument('--ttl', type=int, choices=[60, 300, 3600, 86400], default=3600, help='New TTL')
    parser_record_upd.add_argument('--prio', type=int, default=0, help='New prio')
    parser_record_upd.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser_record_upd.set_defaults(func=record_upd)

    # create the parser for the "record" -> "del" command
    DESCRIPTION = 'Delete dns records'
    parser_record_del = record_subparsers.add_parser('del', description=DESCRIPTION, help=DESCRIPTION)
    parser_record_del.add_argument('-n', '--name', type=str, help='Name', required=True)
    parser_record_del.add_argument('-t', '--type', type=str, choices=["A", "AAAA", "CAA", "CNAME", "MX", "NAPTR", "NS", "PTR", "SRV", "TLSA", "TXT"], help='Type')
    parser_record_del.add_argument('-c', '--content', type=str, help='Content')
    parser_record_del.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser_record_del.set_defaults(func=record_del)

    # etc

    # parse the args
    arguments = parser.parse_args()

    return arguments


def domain_get(arguments):
    """Function to list domains"""

    if arguments.domain:
        request = '/domains/' + arguments.domain
    else:
        request = '/domains'

    try:
        response = requests.get(api_config['Api']['Url'] + request, headers = headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        log.error("Unable to get domain '%s' (%s)", arguments.domain, error)
        sys.exit(1)

    data = json.loads(json.dumps(response.json()['data']))
    print(json.dumps(data))


def record_get(arguments):
    """Function to get dns-records"""

    if not arguments.domain and not arguments.name:
        log.error("Either option -d (domain) or -n (name) is required")
        exit(1)

    if arguments.domain:
        domain = arguments.domain
    else:
        domain = get_fld(arguments.name, fix_protocol=True)

    request = '/domains/' + domain + '/dns'

    try:
        response = requests.get(api_config['Api']['Url'] + request, headers = headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        log.error("Unable to get record(s) from '%s' (%s)", arguments.domain, error)
        sys.exit(1)

    data = json.loads(json.dumps(response.json()['data']))

    if not data:
        log.error("No record(s) found for domain '%s'", domain)
        exit(1)

    if arguments.domain and arguments.name:
        data = [record for record in data if arguments.name in record["name"]]
    elif arguments.name:
        data = [record for record in data if record["name"] == arguments.name]

        if not data:
            log.error("No record(s) found for '%s' in domain '%s'", arguments.name, domain)
            exit(1)

    if arguments.type:
        data = [record for record in data if record["type"] == arguments.type]

    if arguments.content:
        data = [record for record in data if arguments.content in record["content"]]

    if arguments.id:
        data = [record for record in data if record["id"] == arguments.id]

    if not data:
        log.warning("Record(s) were found for '%s' in domain '%s', but not matching your criteria", arguments.name, domain)
        exit(0)

    if arguments.func is record_get:
        print(json.dumps(data))
    else:
        return json.dumps(data)


def record_add(arguments):
    """Function to add dns records"""
    domain = get_fld(arguments.name, fix_protocol=True)

    request = '/domains/' + domain + '/dns'

    headers['Content-Type'] = 'application/json'

    if arguments.type == "TXT":
        payload = '[{"name": "' + arguments.name + '", "type": "' + arguments.type + '", "content": "\\"' + arguments.content + '\\"", "ttl": ' + str(arguments.ttl) + ', "prio": ' + str(arguments.prio) + '}]'
    else:
        payload = '[{"name": "' + arguments.name + '", "type": "' + arguments.type + '", "content": "' + arguments.content + '", "ttl": ' + str(arguments.ttl) + ', "prio": ' + str(arguments.prio) + '}]'

    try:
        response = requests.post(api_config['Api']['Url'] + request, headers = headers, data = payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        log.error("Unable to add record '%s' (%s)", arguments.name, error)
        sys.exit(1)

    log.info("DNS record '%s' successfully added", arguments.name)

    data = json.loads(json.dumps(response.json()['data']))
    print(json.dumps(data))


def record_upd(arguments):
    """Function to update dns records"""
    domain = get_fld(arguments.name, fix_protocol=True)

    request = '/domains/' + domain + '/dns'

    headers['Content-Type'] = 'application/json'

    # get matching record(s):
    #recorddata = json.loads(record_get(Namespace(func=arguments.func,domain='',name=arguments.name,id=arguments.id,type='',content='')))
    recorddata = record_get(Namespace(func=arguments.func,domain='',name=arguments.name,id=arguments.id,type='',content=''))

    if not recorddata:
        log.error("Record '%s' cannot be found in domain '%s'", arguments.name, domain)
        sys.exit(1)

    payload = json.loads(recorddata)

    if arguments.type:
        payload[0]['type'] = arguments.type

    if arguments.content:
        payload[0]['content'] = arguments.content

    if arguments.ttl:
        payload[0]['ttl'] = arguments.ttl

    if arguments.prio:
        payload[0]['prio'] = arguments.prio

    payload = json.dumps(payload)

    if payload != recorddata:
        try:
            response = requests.put(api_config['Api']['Url'] + request, headers = headers, data = payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            log.error("Unable to update record '%s' (%s)", arguments.name, error)
            sys.exit(1)

        log.info("DNS record '%s' successfully updated", arguments.name)

        data = json.loads(json.dumps(response.json()['data']))
        return(json.dumps(data))
    log.info("No changes found, not updating record")

def record_del(arguments):
    """Function to delete dns records"""
    domain = get_fld(arguments.name, fix_protocol=True)

    request = '/domains/' + domain + '/dns'

    headers['Content-Type'] = 'application/json'

    # get matching record(s):
    recorddata = json.loads(record_get(Namespace(func=arguments.func,domain='',name=arguments.name,type=arguments.type,content=arguments.content)))

    if not recorddata:
        log.error("Record '%s' cannot be found in domain '%s'", arguments.name, domain)
        sys.exit(1)

    payload=[]
    for record in recorddata:
        payload.append({"id": record['id']},)

    try:
        response = requests.delete(api_config['Api']['Url'] + request, headers = headers, data = json.dumps(payload))
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        log.error("Unable to delete record '%s' (%s)", arguments.name, error)
        sys.exit(1)

    log.info("DNS record(s) for '%s' successfully deleted", arguments.name)


# Check if config file exists
api_config = configparser.ConfigParser()

try:
    api_config.read_file(open(os.path.expanduser('~/.hosting-api.ini'), encoding="utf-8"))  # pylint: disable=consider-using-with
except FileNotFoundError:
    log.critical("Config file '~/.hosting-api.ini' does not exist")
    sys.exit(1)

# Load configuration file
api_config.read(os.path.expanduser('~/.hosting-api.ini'))

# Check required options
if not api_config['Api']['Url']:
    log.critical("Api URL not found in ~/.hosting-api.ini")
    sys.exit(1)

if 'Token' not in api_config['Api'] and ('User' not in api_config['Api'] or 'Password' not in api_config['Api']):
    log.critical("No Api credentials (token or username/password) found in ~/.hosting-api.ini")
    sys.exit(1)

# Parse arguments and start required function
args = parse_args()

# check if debug mode is needed
if args.debug:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    log.info("Debug mode enabled")
else:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)

headers = {'X-CSRF-TOKEN': '', 'accept': '*/*', 'API-TOKEN': api_config['Api']['Token']}

args.func(args)
