import binascii

def construct_link_local_address(duid):
    """
    Constructs a link-local IPv6 address using the EUI-64 method from the last 48 bits of the DUID.
    
    Parameters:
    duid (str): The DUID string in colon-separated hexadecimal format.
    
    Returns:
    str: The constructed link-local IPv6 address.
    """
    # Remove colons and convert to bytes
    duid_bytes = bytes.fromhex(duid.replace(':', ''))
    
    # Ensure the DUID is long enough
    if len(duid_bytes) < 6:
        raise ValueError("DUID is too short to extract 48 bits.")
    
    # Extract last 6 bytes (48 bits)
    last6 = duid_bytes[-6:]
    
    # Split into first 3 bytes and last 3 bytes
    first3 = last6[:3]
    last3 = last6[3:]
    
    # Insert 'ff:fe' in the middle to form EUI-64
    eui64 = first3 + b'\xff\xfe' + last3
    
    # Convert to a mutable bytearray to modify bits
    eui64 = bytearray(eui64)
    
    # Flip the 7th bit (Universal/Local bit) of the first byte
    eui64[0] ^= 0x02  # Toggle the second least significant bit
    
    # Convert the modified EUI-64 to the standard IPv6 interface identifier format
    interface_id = ':'.join(['{:02x}{:02x}'.format(eui64[i], eui64[i+1]) for i in range(0, 8, 2)])
    
    # Combine with the link-local prefix
    link_local = f'fe80::{interface_id}'
    
    return link_local

# Example usage
if __name__ == "__main__":
    # Given log message DUID
    duid = '00:01:00:01:2e:9e:5c:49:bc:24:11:c5:9c:5d'
    
    # Construct the link-local IPv6 address
    link_local_address = construct_link_local_address(duid)
    
    print("Link-local IPv6 address:", link_local_address)
