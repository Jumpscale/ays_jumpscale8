## osis

Object Storage & Indexing Server

to install, quick howto
```
#make sure you have system redis installed
ays init -n redis.system -i system 

#make sure mongodb is installed
ays init -n mongodb.local

#make sure influxdb is installed
ays init -n influxdb.local

#if redis, mongodb & influxdb in advance installed then the dependency def will put the right consumptions in place
#this does not work if there is more than 1 service of a specific role in place !
#dependencies are now only based on roles
ays init -n osis --data "param.osis.superadmin.passwd=rooter"

ays apply

```