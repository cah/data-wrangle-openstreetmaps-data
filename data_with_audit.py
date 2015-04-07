#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

lower          = re.compile(r'^([a-z]|_)*$')
lower_colon    = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars   = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

mapping = { "St" : "Street",
            "St.": "Street",
            "Rd." : "Road",
            "Ave": "Avenue"
            }


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]


def shape_element(element):
    node = {}
    
    if element.tag != "node" and element.tag != "way" :
        return None
    else:
        node['type']    = element.tag        
        node['pos']     = [None,None]

        for key in element.keys():
            if key in CREATED:
                node.setdefault('created', {})
                node['created'][key] = element.get(key)
            elif key == "lat":
                node['pos'][0] = float(element.get(key))
            elif key == "lon":
                node['pos'][1] = float(element.get(key))
            else:
                node[key] = element.get(key)

        for child_element in iter(element):
            if child_element.tag == "nd":
                node.setdefault('node_refs', []).append(child_element.attrib["ref"])
            elif child_element.tag == "tag":
                key = child_element.attrib["k"]
                if (problemchars.search(key)):
                    continue
                elif(key.startswith('addr:')):
                    node.setdefault('address', {})
                    addr = key.split(':')
                    
                    if(len(addr)==2):
                        key = addr[1]
                        if key == 'street':
                       	   street = update_name(child_element.attrib["v"], mapping) 
                           print street
		        else:
			   street = child_element.attrib["v"]
			node['address'][key] = street
                else:
                    node[key] = child_element.attrib["v"]
        return node


def update_name(name, mapping):
    st_type = street_type_re.search(name).group()
    if st_type in mapping:
    	name = street_type_re.sub(mapping[st_type],name)
    return name


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    data = process_map('example.osm', True)

if __name__ == "__main__":
    test()
