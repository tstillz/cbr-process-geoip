import requests
import json
try:
    import geoip2.database
except Exception as e:
    print(e)
    exit()

reader = geoip2.database.Reader('GeoLite2-City.mmdb')
import threading
import queue
import urllib.parse

def get_geo_info(ip):
    try:
        response = reader.city(ip)
        return {
            'country': response.country.name,
            'city': response.city.name,
            'ip': ip
        }
    except geoip2.errors.AddressNotFoundError as e:
        return {
            'country': '',
            'city': '',
            'ip': ip
        }

requests.packages.urllib3.disable_warnings()

with open('config.json', 'r') as fd:
    cfg = json.load(fd)

cb_api = cfg.get('cb_api')
url = cfg.get('cb_url')
queries = cfg.get('queries')
payload = {'X-Auth-Token': cb_api}

class processEvents():
    def getEvents(self):
        while True:
            if q._qsize() == 0:
                exit()
            taskItem = q.get()
            output_file_name = taskItem.get("filename")
            cb_query = taskItem.get("query")
            print("WORKING ON: {}".format(output_file_name))
            with open(output_file_name, "w+") as f:
                f.write("proc_id,hostname,sensor_id,username,ppid,pid,path,name,parent,process_md5,cmdline,conn_timestamp,local_port,remote_port,local_ip,country,city,proto,domain,direction,country,city,ip\n")
            try:
                offset = 0
                itemsProcessed = 0
                while True:
                    get_deets = requests.get("{}/api/v1/process?cb.urlver=1&q={}&rows=500&start={}".format(url, urllib.parse.quote(cb_query), offset), headers=payload, verify=False)
                    all_list_deets = get_deets.json()

                    total_results = all_list_deets["total_results"]
                    if total_results == 0:
                        break

                    for items in all_list_deets['results']:
                        print("{} | Total Results/Processed: {}/{}".format(output_file_name, total_results, itemsProcessed))

                        get_full_details = requests.get("{}/api/v4/process/{}/{}/event?cb.legacy_5x_mode=false".format(url, items.get("id"), items.get("segment_id"), offset), headers=payload, verify=False)
                        all_full_deets = get_full_details.json()

                        getNets = all_full_deets.get("process").get("netconn_complete")

                        if getNets:
                            for n in getNets:
                                remote_ip = n.get("remote_ip")
                                timestamp = n.get("timestamp")
                                local_port = n.get("local_port")
                                remote_port = n.get("remote_port")
                                proto = n.get("proto")
                                local_ip = n.get("local_ip")
                                direction = n.get("direction")
                                domain = n.get("domain")

                                conntype = None
                                if proto == "6":
                                    conntype = "TCP"
                                elif proto == "17":
                                    conntype = "TCP"

                                if direction == "true":
                                    direction = "outbound"
                                elif direction == "false":
                                    direction = "inbound"

                                with open(output_file_name, "a+") as wff:
                                    wff.write(','.join(map(str, [items.get("id"),
                                        all_full_deets.get("process").get("hostname"),
                                        all_full_deets.get("process").get("sensor_id"),
                                        all_full_deets.get("process").get("username"),
                                        all_full_deets.get("process").get("ppid"),
                                        all_full_deets.get("process").get("pid"),
                                        all_full_deets.get("process").get("path"),
                                        all_full_deets.get("process").get("process_name"),
                                        all_full_deets.get("process").get("parent_name"),
                                        all_full_deets.get("process").get("process_md5"),
                                        all_full_deets.get("process").get("cmdline"),
                                        timestamp,
                                        local_port,
                                        remote_port,
                                        local_ip,
                                        get_geo_info(local_ip).get("country"),
                                        get_geo_info(local_ip).get("city"),
                                        conntype,
                                        domain,
                                        direction,
                                        get_geo_info(remote_ip).get("country"),
                                        get_geo_info(remote_ip).get("city"),
                                        get_geo_info(remote_ip).get("ip")])) + "\n")

                        itemsProcessed = itemsProcessed + 1

                    offset = offset + 500

                    if total_results - offset <= 0:
                        break

            except Exception as e:
                print(e)

            q.task_done()

if __name__ == '__main__':
    q = queue.Queue()

    for qz in queries:
        q.put(qz)

    for i in range(5):
        stk = processEvents()
        worker = threading.Thread(target=stk.getEvents, daemon=True)
        worker.start()
    q.join()