#
# AUTHOR: DJ Kemmet, dj@ziosk.com
# DATE: 8/14/17
# REQUIREMENTS: Python 3.4 or greater, Python Standard Library.
# PURPOSE: The Purpose of this script is to collect the necessary data-points required to import a site into Central.
# CURRENT VERSION: Milestone 0.5
#

import csv
import logging
import os


# Set up global variables
logging. basicConfig(filename='error.log', level=logging.WARNING)
errors_to_csv = ['Site Marked for retry', 'Site marked for retry', 'Site marked for retry']


# Make sure the inventory file where the results go exists, if not, create it and verify it.
def verify_supporting_files():

    # Check for and create inventory.csv if necessary
    if os.path.lexists('inventory.csv'):
        print('Inventory Manifest Found. ')
    else:
        with open('inventory.csv', 'a+') as results_file:
            results_file.close()
        print('Inventory Manifest created.')

    # Check for and create error.log if necessary.
    if os.path.lexists('error.log'):
        print('Error Log Found.')
    else:
        with open('error.log', 'a+') as log_file:
            log_file.close()
        print('Error Log Created')

    # Check for and create retries.csv if necessary.
    if os.path.lexists('retries.csv'):
        print("Previous retry queue was discovered. Something should be done about that.")
    else:
        with open('retries.csv', 'a+') as retry_file:
            retry_file.close()
        print('Retry log created.')

    # Check for and create Completed directory if necessary.
    if os.path.lexists('Completed/'):
        pass
    else:
        os.system('mkdir Completed')


# Inventories the Controller at a given store.
def inventory_controller(site_ip):

    print("inventorying site: " + site_ip)
    try:
        # Facilitates Gathering the Hostname, Software Version, and Controller Model.
        simfile_system = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' system')
        simfile_system_lines = simfile_system.readlines()

        # For each line of output from the host device, Check for the system string
        for line in simfile_system_lines:
            # Gather Model and Software Version.
            if "sysDescr" in line:
                system_string = line
                pass1 = str.split(system_string, '=')
                pass2 = str.split(pass1[1], ',')
                pass3 = str.split(pass2[0], ':')
                controller = ((pass3[2]).replace(")", "")).strip()
                software_root_version = (pass2[1]).strip()

            # Gather Hostname.
            if "sysName" in line:
                if 'Aruba' in line:
                    print('This host was not named.')
                    hostname = 'System Not Named: ' + site_ip
                    break
                else:
                    dirty_sys_line = line
                    pass1 = str.split(dirty_sys_line, '=')
                    pass2 = str.split(pass1[1], ':')
                    hostname = ((pass2[1]).replace("\n", '')).strip()
                    break

        # Facilitates Gathering the System Serial Number.
        software_root_version_split = str.split(software_root_version, " ")
        software_string = software_root_version_split[1].strip()
        if "7.4.0.1" in software_string:
            serial_request = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.2.1.47.1.1.1.1.11.1001')
            for line in serial_request.readlines():
                if "STRING" in line:
                    dirty_serial_line = line
                    pass1 = str.split(dirty_serial_line, ' ')
                    pass2 = pass1[3]
                    serial = str.replace(pass2, '"', '').strip()

        if "7.4.0.4" in software_string:
            serial_request = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.2.1.47.1.1.1.1.11.1001')
            for line in serial_request.readlines():
                if "STRING" in line:
                    dirty_serial_line = line
                    pass1 = str.split(dirty_serial_line, ' ')
                    pass2 = pass1[3]
                    serial = str.replace(pass2, '"', '').strip()

        elif "7.4.1.1" in software_string:
            serial_request = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.2.1.47.1.1.1.1.11.1001')
            for line in serial_request.readlines():
                if "STRING" in line:
                    dirty_serial_line = line
                    pass1 = str.split(dirty_serial_line, ' ')
                    pass2 = pass1[3]
                    serial = str.replace(pass2, '"', '').strip()

        elif "8.1.0.1" in software_string:
            serial_request = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.4.1.14823.2.2.1.1.1.12')
            for line in serial_request.readlines():
                if "STRING" in line:
                    dirty_serial_line = line
                    pass1 = str.split(dirty_serial_line, ' ')
                    pass2 = pass1[3]
                    pass3 = str.replace(pass2, '"', '').strip()
                    serial = pass3

        MAC_request = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.4.1.14823.2.2.1.2.1.7')
        for line in MAC_request.readlines():
            if "STRING" in line:
                dirty_mac_line = line
                pass1 = str.split(dirty_mac_line, '=')
                pass2 = pass1[1]
                pass2 = str.split(pass2, ':')
                pass3 = str.strip(pass2[1], ' ')
                MAC = str.strip(str.strip(pass3, '\n'), ' ')

        data_gathered = [hostname, controller, software_root_version, serial, MAC]
        with open('inventory.csv', "a", newline="") as inventory_file:
            file_writer = csv.writer(inventory_file, quoting=csv.QUOTE_ALL)
            file_writer.writerow(data_gathered)
            inventory_file.close()

        print(hostname + " has been inventoried.")

    # Define Exceptions for the code above.
    except IndexError:
        logging.info(hostname + " Could not collect requested SNMP Objects.")
        with open('inventory.csv', "a", newline="") as inventory_file:
            file_writer = csv.writer(inventory_file, quoting=csv.QUOTE_ALL)
            file_writer.write(errors_to_csv)
            inventory_file.close()
            logging.debug(site_ip + ' could not be reliably inventoried')
            inventory_file.close()
        exit()

        with open('retries.csv', "a", newline="") as retries_file:
            retry_writer = csv.writer(retries_file, quoting=csv.QUOTE_ALL)
            retry_site = [site_ip]
            retry_writer.writerow(retry_site)
            retries_file.close()

    except TimeoutError:
        logging.info(hostname + "is either unavailable or removed from service.")
        with open('inventory.csv', "a", newline="") as inventory_file:
            file_writer = csv.writer(inventory_file, quoting=csv.QUOTE_ALL)
            file_writer.write(errors_to_csv)
            inventory_file.close()
            logging.debug(site_ip + ' site did not respond to snmp query')
        with open('retries.csv', "a", newline="") as retries_file:
            retry_writer = csv.writer(retries_file, quoting=csv.QUOTE_ALL)
            retry_site = [site_ip]
            retry_writer.writerow(retry_site)
            retries_file.close()

    except KeyboardInterrupt:
        logging.debug('Inventory interrupted by Keystroke. Removing Inventory file.')
        # os.system('rm -rf inventory.csv')
        exit()

    except UnboundLocalError:
        print("General Exception has occurred.")
        with open('inventory.csv', "a", newline="") as inventory_file:
            print("Inventory Stopped By User Key Stroke. Deleting Inventory Manifest.")
            file_writer = csv.writer(inventory_file, quoting=csv.QUOTE_ALL)
            file_writer.writerow(errors_to_csv)
            inventory_file.close()
            logging.debug(site_ip + ' encountered a general exception occurred.')
        with open('retries.csv', "a", newline="") as retries_file:
            retry_writer = csv.writer(retries_file, quoting=csv.QUOTE_ALL)
            retry_site =[site_ip]
            retry_writer.writerow(retry_site)
            retries_file.close()


# Inventories the AP Cluster at a given store.
def inventory_APs(site_ip):
    #
    # CLUSTER SOFTWARE VERSION. Results in a single string
    #
    cluster_software_version = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.4.1.14823.2.3.3.1.1.4.0')
    results = cluster_software_version.readlines()
    for line in results:
        pass1 = line.split("STRING:")
        pass2 = pass1[1].strip()
        final_cluster_software_version = str.replace(pass2, '"', "")


    #
    # CLUSTER NAME. Results in a single string
    #
    cluster_name = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.4.1.14823.2.3.3.1.1.2.0')
    for line in cluster_name.readlines():
        pass1 = line.split("STRING:")
        pass2 = pass1[1].strip()
        final_cluster_name = pass2.replace('"', '')

    #
    # MEMBER AP MAC ADDRESSES. returns a list of mac addresses, one of each AP in the cluster.
    #
    membermac_list = []
    member_mac_addresses = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.4.1.14823.2.3.3.1.2.1.1.1')
    for line in member_mac_addresses.readlines():
        pass1 = line.split("STRING:")
        pass2 = pass1[1].strip()
        final_member_mac_address = pass2.replace(" ", "")
        membermac_list.append(final_member_mac_address)

    #
    # MEMBER AP SERIAL NUMBERS. returns a list of serials, one of each AP in the cluster.
    #
    memberserial_list = []
    member_serial_numbers = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.4.1.14823.2.3.3.1.2.1.1.4')
    for line in member_serial_numbers.readlines():
        pass1 = line.split("STRING: ")
        pass2 = pass1[1].replace('"', '')
        final_member_serial_number = pass2.strip()
        memberserial_list.append(final_member_serial_number)

    #
    # MEMBER AP MODEL NUMBERS. returns a list of model numbers, one of each AP in the cluster.
    #
    membermodel_list = []
    member_model_numbers = os.popen('snmpwalk -v 2c -c nhB7S@wX ' + site_ip + ' .1.3.6.1.4.1.14823.2.3.3.1.2.1.1.6')
    for line in member_model_numbers.readlines():
        pass1 = line.split("STRING:")
        pass2 = pass1[1].replace('"', '')
        final_member_model_number = pass2.strip()
        membermodel_list.append(final_member_model_number)


    # Get the length of each list:
    if len(membermac_list) == len(memberserial_list):
        if len(membermac_list) == len(membermodel_list):
            for entry in range(0, len(membermac_list)):
                name = final_cluster_name
                software = final_cluster_software_version
                model = membermac_list[entry]
                mac = membermac_list[entry]
                serial = memberserial_list[entry]
                data_gathered = [name, software, model, mac, serial]
                with open('inventory.csv', "a", newline="") as inventory_file:
                    file_writer = csv.writer(inventory_file, quoting=csv.QUOTE_ALL)
                    file_writer.writerow(data_gathered)
                    inventory_file.close()
                    print("wrote "+ name + " " + software + " " + model + " " + mac + " " + serial + " " + serial)
                inventory_file.close()
    else:
        print("Cannot reliably inventory " + cluster_name + ". It appears that one or more APs did not respond to "
                                                            "an SNMP query ")


# Converts a Site Address to a Controller address and returns it to the calling function
def check_ip(site_ip):
    site_ip = (str.replace(site_ip, '"', ''))
    new_ip = ''
    if "\n" in site_ip:
        site_ip = site_ip.replace('\n', "")
        site_octets = str(site_ip).split(".")
        if site_octets[3] is not "1":
            site_octets[3] = "1"
            for octet in site_octets:
                if octet is not "1":
                    new_ip += octet + "."
                else:
                    new_ip += octet
            site_ip = new_ip
        else:
            site_ip = site_ip
    return site_ip


# Converts a Site Address to a VC address and returns it to the calling function
def make_ap_ip(site_ip):
    site_ip = (str.replace(site_ip, '"', ''))
    new_ip = ''
    if "\n" in site_ip:
        site_ip = str.replace(site_ip, "\n", '')
        octets = str(site_ip).split(".")
        if octets[3] is not "2":
            octets[3] = "2"
            for octet in octets:
                if octet is not "2":
                    new_ip += octet + "."
                else:
                    new_ip += octet
        else:
            new_ip = site_ip
    return new_ip


# The Sauce of this tool.
def main():
    verify_supporting_files()
    for file in os.listdir('.'):
        if '.csv' in file:
            verify_supporting_files()            with open(file, 'r') as list_file:
                reader = list_file.readlines()
                for site in reader:
                    inventory_controller(check_ip(site))
                    inventory_APs(make_ap_ip(site))

            if os.path.lexists('retries.csv') is True:
                with open('retries.csv', 'r') as retries:
                    reader = retries.readlines()
                    for site in reader:
                        inventory_controller(check_ip(site))
                        inventory_APs(make_ap_ip(site))

        job_name = str(file.split(".")[0])
        os.system('mkdir Completed/' + job_name)

        # Move inventory.csv, error.log, retries.csv the CSV itself to this directory
        os.system('mv inventory.csv error.log retries.csv ' + job_name + '.csv' + ' Completed/' + job_name)


main()