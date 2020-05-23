# Custom Inventory Agent
This custom inventory agent was built to collect the necessary information to migrate a device from airwave and other 
managment tools into aruba central. Given the complexity of and lack of documentation for SNMP in aruba products, this 
tool was written to collect only the necessary information. However, future iterations of this tool will likely accept 
a list of OIDs and process them into a CSV simliar to what this tool currently puts out.

## What does this tool collect?
This tool collects the following information and stores them as a string to 
a CSV file for further consumption
1. Hostname
    * If a system did not have it's host name defined, This ool acknowledges the
      default hostname and makes the user aware of this issue in the inventory
2. Controller Model
3. Software Version
    * Supported Platforms include:
        * ArubaOS 7.4.0.1
        * ArubaOS 7.4.1.1
        * ArubaOS 8.1.0.1
4. System Serial
5. System MAC address