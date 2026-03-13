"""
Azure Cost Optimization Scanner
Author: Karan
Purpose: Detect unused resources and estimate potential savings
"""

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.costmanagement import CostManagementClient
import datetime

# Authentication
credential = DefaultAzureCredential()
subscription_id = "c93bb824-65c3-4eba-b18c-c40a23030467"

compute_client = ComputeManagementClient(credential, subscription_id)
network_client = NetworkManagementClient(credential, subscription_id)
resource_graph_client = ResourceGraphClient(credential)
cost_client = CostManagementClient(credential)

# Resource Graph Queries
def find_unattached_disks():
    query = {
        "subscriptions": [subscription_id],
        "query": "Resources | where type =~ 'microsoft.compute/disks' | where properties.diskState == 'Unattached'"
    }
    result = resource_graph_client.resources(query)
    return result.data

def find_unassociated_ips():
    query = {
        "subscriptions": [subscription_id],
        "query": "Resources | where type =~ 'microsoft.network/publicipaddresses' | where isnull(properties.ipConfiguration)"
    }
    result = resource_graph_client.resources(query)
    return result.data

def find_unused_nics():
    query = {
        "subscriptions": [subscription_id],
        "query": "Resources | where type =~ 'microsoft.network/networkinterfaces' | where isnull(properties.virtualMachine)"
    }
    result = resource_graph_client.resources(query)
    return result.data

def find_stopped_vms():
    query = {
        "subscriptions": [subscription_id],
        "query": "Resources | where type =~ 'microsoft.compute/virtualmachines' | where properties.extended.instanceView.powerState.code != 'PowerState/running'"
    }
    result = resource_graph_client.resources(query)
    return result.data

# Cost Estimation (rough values)
def estimate_disk_cost(size_gb):
    return size_gb * 0.05   # $0.05 per GB/month

def estimate_ip_cost():
    return 3.0   # $3/month per IP

def estimate_nic_cost():
    return 0.0   # NICs are free

def estimate_vm_cost():
    return 25.0  # $25/month for stopped VM

# Report
def print_report(vms, disks, ips, nics):
    print("\n" + "="*50)
    print("AZURE FINOPS COST OPTIMIZATION REPORT")
    print("="*50)
    print(f"Generated at: {datetime.datetime.now()}")
    print("="*50)

    total_savings = 0

    print("\nStopped VMs:")
    if vms:
        for vm in vms:
            print(f"- {vm['name']} | {vm['resourceGroup']}")
            total_savings += estimate_vm_cost()
    else:
        print("None")

    print("\nUnattached Disks:")
    if disks:
        for disk in disks:
            size_gb = disk['properties'].get('diskSizeGB', 0)
            cost = estimate_disk_cost(size_gb)
            print(f"- {disk['name']} ({size_gb} GB) | Est. ${cost:.2f}/month")
            total_savings += cost
    else:
        print("None")

    print("\nUnassociated Public IPs:")
    if ips:
        for ip in ips:
            cost = estimate_ip_cost()
            print(f"- {ip['name']} | Est. ${cost:.2f}/month")
            total_savings += cost
    else:
        print("None")

    print("\nUnused NICs:")
    if nics:
        for nic in nics:
            print(f"- {nic['name']}")
    else:
        print("None")

    print("\n" + "="*50)
    print(f"Estimated Potential Savings: ${total_savings:.2f}/month")
    print("="*50)

# Main
def main():
    print("\nAzure Cost Optimization Scanner\n")

    vms = find_stopped_vms()
    disks = find_unattached_disks()
    ips = find_unassociated_ips()
    nics = find_unused_nics()

    print_report(vms, disks, ips, nics)

if __name__ == "__main__":
    main()