import json
# import logging
import socket
# import threading
# import time
# from multiprocessing.pool import ThreadPool
from prettytable import PrettyTable
from termcolor import colored
import yaml


def print_error(message):
    """
    Prints a message to the console with red color, to indicate an error

    :param message: The message to print
    """
    print(colored(message, "red"))


def test_connection(host, port, protocol, timeout):
    """
    Tests a connection to a host and port using a specific protocol and timeout.

    :param host: The hostname or IP address to test the connection to
    :param port: The port number to test the connection on
    :param protocol: The protocol to use for the connection (either "tcp" or "udp")
    :param timeout: The number of seconds to wait for the connection to succeed
    :return: True if the connection succeeds, False otherwise
    """
    sock_type = socket.SOCK_STREAM  # default socket type is TCP

    if protocol == "udp":
        sock_type = socket.SOCK_DGRAM

    result = False

    try:
        sock = socket.socket(socket.AF_INET, sock_type)
        sock.settimeout(timeout)

        result = sock.connect_ex((host, port)) == 0
    except Exception as e:
        print_error(f"Error: {e}")
    finally:
        sock.close()

    return result


def main():
    """
    Main function that reads host configuration from a YAML file, tests connectivity
    for each host and service, and prints a status table.

    Reads the 'hosts.yaml' file to extract host details and service configurations.
    For each host, it determines the IP address, either directly or by resolving the FQDN.
    For each service, it tests connectivity using the specified protocol and port, and
    updates a PrettyTable with the results, showing the status as 'OK' or 'KO'.

    Utilizes the 'test_connection' function to check connectivity and 'print_error' to
    display error messages in case of issues.

    The table displays the following fields: Name, FQDN, IP, Service, Port, Protocol, and Status.
    """
    with open(r"hosts.yaml", "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        json_data = json.loads(json.dumps(data, sort_keys=False))
        timeout = json_data["config"]["timeout"]

        table = PrettyTable()
        table.field_names = [
            "Name",
            "FQDN",
            "IP",
            "Service",
            "Port",
            "Protocol",
            "Status",
        ]
        table.align["Name"] = "l"
        table.align["FQDN"] = "l"
        table.align["IP"] = "r"
        table.align["Service"] = "l"
        table.align["Port"] = "r"

        for host_data in json_data["hosts"]:
            name = host_data.get("host")
            ip = host_data.get("ip")
            fqdn = host_data.get("fqdn")
            services = host_data.get("services")

            if (ip is None) and (fqdn is None):
                print_error(f'Error: No IP and/or FQDN for host "{name}"')

            if (ip is None) and (fqdn is not None):
                try:
                    ip = socket.gethostbyname(fqdn)
                except Exception as e:
                    print_error(f"Error: {e}")

            for service, service_data in services.items():
                port = service_data.get("port")
                protocol = service_data.get("protocol")

                if protocol not in ("tcp", "udp"):
                    print_error(f"Invalid protocol: {protocol}")
                else:
                    if test_connection(ip, port, protocol, timeout):
                        status = colored("OK", "green")
                    else:
                        status = colored("KO", "red", attrs=["reverse", "bold"])

                    table.add_row([name, fqdn, ip, service, port, protocol, status])

        print(table)


if __name__ == "__main__":
    main()
