# Patch Release v1.0.2 (2023-02-13)
  * **Tom Siewert**
    * tasks: Set timer state to started or stopped
      
      Even if the timer is enabled, systemd will not generate certificates
      until the system has been rebooted or the timer has been started
      directly.
    * tasks: Do not recurse on directory task
    
      Ansible does not only recurse on the directory inodes, but also on the
      files in these directories. Due to this behaviour, Ansible sets the permission
      of all created certificates to 0755.

*Released by Tom Siewert <tom.siewert@hetzner.com>*

# Patch Release v1.0.1 (2023-02-07)
  * **Tom Siewert**
    * meta: Use correct license

*Released by Tom Siewert <tom.siewert@hetzner.com>*

# Major Release v1.0.0 (2023-01-30)
  * **Tom Siewert**
    * Init for GitHub

*Released by Tom Siewert <tom.siewert@hetzner.com>*
