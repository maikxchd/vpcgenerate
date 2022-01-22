#!/usr/bin/env python

import csv
import netaddr
from tinydb.storages import MemoryStorage
from tinydb import TinyDB, Query
import jinja2
import os
import click
import requests
from logzero import logger
from requests.auth import HTTPBasicAuth
from getpass import getpass

# Quick And Easy Using tinydb. This can be modified for a real DB.

db = TinyDB(storage=MemoryStorage)

# Place all the sites with the exact structured data so that this can be used for jinja2 templating.
sites = [{'name': 'dxcon-fgsezsn1', 'router': 'br01.sea01', 'port': '8/7', 'vendor': 'brocade', 'primary': True},
         {'name': 'dxcon-fg43vylb', 'router': 'br01.sea01', 'port': '7/7', 'vendor': 'brocade', 'primary': False},
         {'name': 'dxcon-ffma5u4b', 'router': 'br02.sea01', 'port': '8/7', 'vendor': 'brocade', 'primary': True},
         {'name': 'dxcon-fgz90x4d', 'router': 'br02.sea01', 'port': '7/7', 'vendor': 'brocade', 'primary': False},
         {'name': 'dxlag-ffmi354y', 'router': 'br01.pdx01', 'port': 'Bundle-Ether190', 'vendor': 'cisco', 'primary': True},
         {'name': 'dxlag-fgub0exd', 'router': 'br02.pdx01', 'port': 'Bundle-Ether190', 'vendor': 'cisco', 'primary': True},
         {'name': 'dxlag-fhbaaj9l', 'router': 'br01.iad03', 'port': 'Bundle-Ether190', 'vendor': 'cisco', 'primary': True},
         {'name': 'dxlag-fgtp2wyi', 'router': 'br02.iad03', 'port': 'Bundle-Ether190', 'vendor': 'cisco', 'primary': True},
         {'name': 'dxlag-fgamlxc3', 'router': 'br01.lhr03', 'port': 'Bundle-Ether190', 'vendor': 'cisco', 'primary': True},
         {'name': 'dxlag-fgakpk3m', 'router': 'br02.lhr03', 'port': 'Bundle-Ether190', 'vendor': 'cisco', 'primary': True},
         {'name': 'dxlag-ffrkq299', 'router': 'br01.sin01', 'port': 'Bundle-Ether190', 'vendor': 'cisco', 'primary': True},
         {'name': 'dxlag-ffl4n4hg', 'router': 'br02.sin01', 'port': 'Bundle-Ether190', 'vendor': 'cisco', 'primary': True}
         ]
for site in sites:  # Inserting all the sites listed above into the pseudo db.
    db.insert(site)


def render(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)


class VpcConnection:
    def __init__(self, name, account, connection, vlan, ipblock, bgp_auth, bgp_community, region_id, batch=False,
                 serve=False, cli=False):
        self.name = name
        self.cli = cli
        self.account = account
        self.connection = connection
        self.region_id = region_id
        self.vlan = vlan
        self.ipblock = ipblock
        self.ip = None
        self.amzn_ip = None
        self.netmask = None
        self.serve = serve
        self.bgp_auth = bgp_auth
        self.bgp_community = bgp_community
        self.vpc_router = None
        self.vpc_port = None
        self.vpc_vendor = None
        self.vpc_primary = None
        self.__pull_site_info()
        self.__break_ip()
        if not batch:
            self.filename = "{0}_{1}_{2}.cfg".format(self.vpc_router, self.name, self.vlan)
        else:
            self.filename = "{0}.cfg".format(self.vpc_router)
        self.__render_route_map()
        self.__render_vpc_config()

    def __render_vpc_config(self):
        render_config = (render('./templates/vpc.peer.jinja2', self.__dict__))
        if self.serve:
            self.vpc_config = render_config
        else:
            with open('./generated_configs/' + self.filename, "a") as conf:
                conf.write(render_config)
                conf.write("\n")

    def __render_route_map(self):
        route_query = Query()
        if db.search(route_query.route_map == "{}_{}".format(self.vpc_router, self.name)) and self.cli:
            # The route map has already been created and lets not put it there again.
            pass
        else:
            # Lets create the routemap
            db.insert({'route_map': "{}_{}".format(self.vpc_router, self.name)})
            route_map = render('./templates/vpc.routemap.jinja2', self.__dict__)
            if self.serve:
                self.vpc_route_map = route_map
            else:
                with open('./generated_configs/' + self.filename, "a") as conf:
                    conf.write(route_map)
                    conf.write("\n")

    def __pull_site_info(self):
        vpc_site = Query()
        site = db.search(vpc_site.name == self.connection)[0]
        self.vpc_router = site['router']
        self.vpc_port = site['port']
        self.vpc_vendor = site['vendor']
        self.vpc_primary = site['primary']

    def __break_ip(self):
        net_obj = netaddr.IPNetwork(self.ipblock)
        # assert str(net_obj.netmask) == '255.255.255.252', "The IP Network {} is not a /30!!".format(net_obj)
        ip_addresses_avail = [x for x in net_obj.iter_hosts()]
        self.ip = ip_addresses_avail[1]
        self.amzn_ip = ip_addresses_avail[0]
        self.netmask = net_obj.netmask
        if str(self.netmask) not in ['255.255.255.252', '255.255.255.254']:
            logger.warn("The IP Network {} has a netmask of {}".format(net_obj, self.netmask))


@click.command()
@click.option('--json', help="URL of JSON to be used")
@click.option('--csvfile', help='File that will be used to generate the configurations.')
@click.option('--batch/--no-batch', default=False,
              help='Default is False. If specified this means that all the configs are placed per router instead of a config for each VPC.')
def cli(csvfile, batch, json=None):
    if json:
        # todo: Change this to directly pass the JSON as dict as **kwargs on VpcConnection
        try:
            username = input("Please enter your username: ")
            password = getpass("Please enter the password: ")
            jq = requests.get(json, auth=HTTPBasicAuth(username=username, password=password)).json()
            for vpc in jq:
                vpc_object = VpcConnection(vpc['name'], vpc['account'], vpc['ref'], vpc['vlan'], vpc['ip4_network'],
                                           vpc['bgp_auth_key'], vpc['bgp_community'], vpc['region_id'], batch=batch, cli=True)

        except:
            logger.error(
                "Something went wrong with the JSON import. Ensure that the url is proper and is in proper json format.")
    else:
        try:
            with open(csvfile, 'r', encoding='utf-8-sig') as f:
                csvreader = csv.DictReader(f)
                for line in csvreader:
                    vpc_object = VpcConnection(line['name'], line['account'], line['connection'], line['vlan'],
                                               line['ipblock'],
                                               line['bgp_auth'], line['bgp_community'], line['region_id'], batch=batch, cli=True)



        except TypeError:
            logger.warn("program did not receive a file input.")


if __name__ == '__main__':
    cli()
