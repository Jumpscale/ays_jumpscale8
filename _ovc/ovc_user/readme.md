## usage of ovc_user
### example
```

g8client__bescale1:
  g8.url: 'be-scale-1.demo.greenitglobe.com'
  g8.login: 'mylogin'
  g8.password: 'secret'

vdc__user1:
    g8.client.name: 'bescale1'

# this will check if a user with username 'testuser' exists. if not, it will create it.
ovc_user__user1:
    g8.client.name: 'main'
    username: 'testuser'
    password: 'secret'
    email: 'mail@fake.com'
    vdc: 'user1' # if sepcified, it will give this user access to the vdc called user1
```
