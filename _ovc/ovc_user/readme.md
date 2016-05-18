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
  authentication_method: 'oauth2' # Possible values: 'oauth2' or 'password
  authentication_provider: 'itsyou.online' # Currently only 'itsyou.online' is supported, and only required when authentication_method = 'oath2'
  username: 'testuser'
  password: 'moehaha' # Only required when authentication_method = 'password'
  email: 'user@mail.com'
  vdc: 'user1' # if sepcified, it will give this user access to the vdc called user1
```
