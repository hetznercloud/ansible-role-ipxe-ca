#!/usr/bin/env python3

# License: GPL-3.0-or-later
# Author: Tom Siewert <tom.siewert@hetzner.com>
# Author: Tobias Mädel <tobias.maedel@hetzner-cloud.de>

"""
ipxe-asn1-hack: Sign an X.509 PEM certificate and convert it to a special-crafted DER
file where both the iPXE CA and the cross-signed Root CA get merged into one ASN.1 set.

CA- and output directory will be set via env variables.
"""

import base64
import binascii
import os
import subprocess

import pyasn1
from pyasn1.codec.der import decoder, encoder

class IPXEASN1Hack:
    def __init__(
            self, openssl_config_path, signed_ipxe_path,
            ca_web_path, ca_pubkey_path, ca_privkey_path,
            ca_certificates_path
    ):
        self.openssl_config_path = openssl_config_path
        self.signed_ipxe_path = signed_ipxe_path
        self.ca_web_path = ca_web_path
        self.ca_pubkey_path = ca_pubkey_path
        self.ca_certificates_path = ca_certificates_path

    def decode_pem_certificate(self, content):
        """
        Removes the first, the last and newlines of a PEM X.509 certificate
        and decodes the base64 string.
        """
        return base64.b64decode(''.join(content.splitlines()[1:-1]))

    def create_ipxe_asn1_set(self, certs):
        """
        Create an iPXE-compatible ASN.1 Set with the iPXE CA and the
        cross-signed Root CA.
        """
        asn1set = pyasn1.type.univ.Set()
        for pos, cert in enumerate(certs):
            asn1set.setComponentByPosition(pos, decoder.decode(cert)[0])
        return encoder.encode(asn1set)

    def sign_and_convert(self, src, signed_pem_dest):
        """
        Cross-sign the PEM Root CA and convert it to the iPXE ASN.1 "format".
        """
        openssl_command = f'''openssl ca -extensions cross \
        -notext -batch -config {self.openssl_config_path} \
        -preserveDN -ss_cert {src} -out {signed_pem_dest}'''

        sign_process = subprocess.Popen(openssl_command, stdout=subprocess.PIPE, shell=True)
        print(sign_process.communicate())

        # Decode base64 PEM of signed certificate
        signed_certificate = self.decode_pem_certificate(open(signed_pem_dest, 'r').read())

        # Decode ASN.1 of the signed Root CA
        decoded_data = decoder.decode(signed_certificate)

        # Enter the correct ASN.1 sequence
        decoded_data = decoded_data[0]
        decoded_data = decoded_data[0]

        base = 0
        sequence_count = 0
        while sequence_count != 4:
            base += 1
            if isinstance(
                    decoded_data[base], pyasn1.type.univ.Sequence
            ) or isinstance(
                decoded_data[base], pyasn1.type.univ.SequenceOf
            ):
                sequence_count += 1

        subject = decoded_data[sequence_count + 1]
        checksum = binascii.crc32(encoder.encode(subject))

        # Write iPXE der file
        ipxe_filename = ('%08x.der' % ((checksum & 0xffffffff) ^ 0xffffffff))
        print(f'Write iPXE file as {ipxe_filename}')
        with open(os.path.join(signed_ipxe_path, ipxe_filename), mode='wb') as file:
            file.write(
                self.create_ipxe_asn1_set([signed_certificate,
                                           self.decode_pem_certificate(open(ca_pubkey_path, 'r').read())])
            )

if __name__ == "__main__":
    print('Hi Mom!')
    ca_web_path = os.environ['IPXE_CA_WEB_PATH']
    ca_pubkey_path = os.environ['IPXE_CA_CERT_PATH']
    ca_privkey_path = os.environ['IPXE_CA_KEY_PATH']
    signed_ipxe_path = f'{ca_web_path}/auto'
    signed_pem_path = f'{ca_web_path}/signed'
    openssl_config_path = '/etc/default/ipxe-openssl.cnf'
    ca_certificates_path = '/usr/share/ca-certificates/mozilla'

    asn1hack = IPXEASN1Hack(
        openssl_config_path, signed_ipxe_path,
        ca_web_path, ca_pubkey_path, ca_privkey_path,
        ca_certificates_path
    )

    print('Create temporary database and serial')
    open('/tmp/ipxe-ca.db', 'w').close()
    serial_file = open('/tmp/ipxe-ca.serial', 'w')
    serial_file.write('00')
    serial_file.close()

    for raw_cert_name in os.listdir(ca_certificates_path):
        if '.crt' in raw_cert_name:
            print(f'Sign {raw_cert_name}')
            raw_cert_path = os.path.join(ca_certificates_path, raw_cert_name)
            signed_pem_dest = os.path.join(signed_pem_path, raw_cert_name)

            asn1hack.sign_and_convert(raw_cert_path, signed_pem_dest)

    print('Delete temporary database and serial')
    for item in ['db', 'db.old', 'db.attr', 'db.attr.old', 'serial', 'serial.old']:
        if os.path.exists(f'/tmp/ipxe-ca.{item}'):
            os.remove(f'/tmp/ipxe-ca.{item}')
