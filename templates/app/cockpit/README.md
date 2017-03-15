#template: ayscockpit

##Description:

This actor template installs an ays cockpit on a parent os.

##Schema:
 - os: Parent os service name defined in blueprint. *Required*
 - oauth.client_id: Client id obtained from itsyouonline.com
 - oauth.client_secret: Client secret obtained from itsyouonline.com
 - oauth.organization: Organization name for authentication obtained from itsyouonline.com 


##Example:
Replace \<with actual value \>

```yaml
g8client__client:
    url: <url>
    login: <login>
    password: <password>
    account: <account>

vdc__main:
    g8client: client
    account: <account>
    location: <location>

node.ovc__cockpitvm:
    memory: 4
    ports:
        - "80:82"
    ssh.login: admin
    ssh.password: admin
    vdc: main
    os.image: "Ubuntu 16.04 x64"

cockpit__cockpitapp:
    host_node: cockpitvm
    oauth.organization : <organization>
    oauth.client_id : <client_id>
    oauth.client_secret : <client_secret>

actions:
    - action: install

```