# Ansible Role - iPXE CA

An Ansible role to cross-sign all Root CAs with your own CA for iPXE.

## Requirements

* Ansible
* CA used for cross-signing

## Role Variables

``` yaml
ipxe_ca__web_path: '/var/www/ca'

ipxe_ca__ca_cert_path: '/etc/ssl/private/ipxe.crt'
ipxe_ca__ca_key_path: '/etc/ssl/private/ipxe.key'

ipxe_ca__certificate_valid_days: 180
ipxe_ca__systemd_timer_enabled: true
```

## Dependencies

None.

## Example Playbook

``` yaml
- hosts: all
  roles:
    - hetzner.ipxe_ca
```

## License

GPL-3.0
