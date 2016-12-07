
This is an example AYS repo to show how to create a docker on a vm hosted on openvcloud.

To demo/try out this blueprint, do
```python
# Set this repo to be on "noexec" mode
ays noexec --enable

# Apply these blueprints
ays blueprint

# Run!
ays run
```

If you want to actually create a docker on a vm hosted on openvcloud
 1. create a new ays repo
    ```python
    ays create_repo -g "http://github.com/<account>/<repo>" -p "<path>"
    ```
 2. Copy these blueprints into it
 3. Make it reality!
    ```python
    # Apply these blueprints
    ays blueprint

    # Run!
    ays run
    ```




----------------------------------------
#### Services used:
 - [g8client](/ays_jumpscale8/blob/8.1.0/templates/clients/g8client)
 - [vdc](ays_jumpscale8/blob/8.1.0/templates/ovc/vdc)
 - [os.ssh.ubuntu](ays_jumpscale8/blob/8.1.0/templates/os/os.ssh.ubuntu)
 - [node.ovc](ays_jumpscale8/blob/8.1.0/templates/nodes/node.ovc)
 - [node.docker](ays_jumpscale8/blob/8.1.0/templates/nodes/node.docker)

#### Useful links:
- More about [AYS noexec](https://github.com/Jumpscale/jumpscale_core8/blob/8.1.0/docs/AYS/Commands/noexe.md)
- More about [AYS](https://gig.gitbooks.io/jumpscale-core8/content/AYS/AYS-Introduction.html)
- More about [AYS repo structure](https://gig.gitbooks.io/jumpscale-core8/content/AYS/FileDetails/FilesDetails.html)
